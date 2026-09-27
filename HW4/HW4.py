import uuid
from datetime import datetime, timedelta

from HW1.HW1 import BankAccount, InvalidOperationError, InsufficientFundsError
from HW2.HW2 import PremiumAccount


# ============================================================
# Transaction
# ============================================================

class Transaction:
    def __init__(
        self,
        transaction_type,
        amount,
        currency,
        sender,
        receiver,
        commission=0,
        priority=1,
        execute_at=None
    ):
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InvalidOperationError(
                "Сумма транзакции должна быть положительным числом"
            )

        if not isinstance(commission, (int, float)) or commission < 0:
            raise InvalidOperationError(
                "Комиссия должна быть неотрицательным числом"
            )

        if priority < 1:
            raise InvalidOperationError(
                "Приоритет должен быть положительным числом"
            )

        self.transaction_id = str(uuid.uuid4())[:8]
        self.transaction_type = transaction_type
        self.amount = amount
        self.currency = currency
        self.commission = commission

        self.sender = sender
        self.receiver = receiver

        self.priority = priority
        self.execute_at = execute_at

        self.status = "pending"
        self.failure_reason = None

        self.created_at = datetime.now()
        self.completed_at = None

        self.attempts = 0

    def __str__(self):
        return (
            f"Transaction {self.transaction_id}: "
            f"{self.transaction_type}, "
            f"{self.amount} {self.currency}, "
            f"status={self.status}, "
            f"priority={self.priority}"
        )


# ============================================================
# TransactionQueue
# ============================================================

class TransactionQueue:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        return True

    def cancel_transaction(self, transaction_id):
        for transaction in self.transactions:
            if transaction.transaction_id == transaction_id:
                if transaction.status != "pending":
                    return False

                transaction.status = "cancelled"
                return True

        return False

    def get_ready_transactions(self):
        current_time = datetime.now()
        ready_transactions = []

        for transaction in self.transactions:
            if transaction.status != "pending":
                continue

            if transaction.execute_at is not None:
                if transaction.execute_at > current_time:
                    continue

            ready_transactions.append(transaction)

        ready_transactions.sort(
            key=lambda transaction: transaction.priority,
            reverse=True
        )

        return ready_transactions

    def __len__(self):
        return len(self.transactions)


# ============================================================
# TransactionProcessor
# ============================================================

class TransactionProcessor:
    def __init__(self, exchange_rates=None, max_retries=3):
        if exchange_rates is None:
            exchange_rates = {
                "RUB": 1.0,
                "USD": 0.011,
                "EUR": 0.0095,
                "KZT": 5.5,
                "CNY": 0.079
            }

        self.exchange_rates = exchange_rates
        self.max_retries = max_retries

        self.error_log = []

    # --------------------------------------------------------
    # Комиссия
    # --------------------------------------------------------

    def calculate_commission(self, transaction):
        if transaction.transaction_type == "external":
            return transaction.amount * 0.01

        return 0

    # --------------------------------------------------------
    # Конвертация валют
    # --------------------------------------------------------

    def convert_currency(self, amount, from_currency, to_currency):
        if from_currency == to_currency:
            return amount

        if from_currency not in self.exchange_rates:
            raise InvalidOperationError(
                f"Неизвестная валюта: {from_currency}"
            )

        if to_currency not in self.exchange_rates:
            raise InvalidOperationError(
                f"Неизвестная валюта: {to_currency}"
            )

        amount_in_rub = amount / self.exchange_rates[from_currency]
        converted_amount = amount_in_rub * self.exchange_rates[to_currency]

        return converted_amount

    # --------------------------------------------------------
    # Проверка счета
    # --------------------------------------------------------

    def check_account(self, account):
        if account.status == "frozen":
            raise InvalidOperationError(
                "Операция запрещена: счет заморожен"
            )

        if account.status == "closed":
            raise InvalidOperationError(
                "Операция запрещена: счет закрыт"
            )

    # --------------------------------------------------------
    # Выполнение одной транзакции
    # --------------------------------------------------------

    def process_transaction(self, transaction):
        transaction.attempts += 1

        try:
            sender = transaction.sender
            receiver = transaction.receiver

            # Проверяем статус счетов
            self.check_account(sender)
            self.check_account(receiver)

            # Рассчитываем комиссию
            transaction.commission = self.calculate_commission(
                transaction
            )

            # Сколько нужно списать со счета отправителя
            total_to_withdraw = (
                transaction.amount + transaction.commission
            )

            # ------------------------------------------------
            # Если валюта транзакции отличается от валюты
            # счета отправителя — конвертируем сумму списания.
            # ------------------------------------------------

            sender_amount = self.convert_currency(
                total_to_withdraw,
                transaction.currency,
                sender.currency
            )

            # ------------------------------------------------
            # Проверяем средства.
            #
            # Для обычного счета отрицательный баланс запрещен.
            # Для PremiumAccount допускается овердрафт.
            # ------------------------------------------------

            if not isinstance(sender, PremiumAccount):
                if sender.balance < sender_amount:
                    raise InsufficientFundsError(
                        "Недостаточно средств для выполнения перевода"
                    )

            # Списание
            sender.withdraw(sender_amount)

            # ------------------------------------------------
            # Сумма, которая поступит получателю.
            # Комиссия не переводится получателю.
            # ------------------------------------------------

            receiver_amount = self.convert_currency(
                transaction.amount,
                transaction.currency,
                receiver.currency
            )

            receiver.deposit(receiver_amount)

            transaction.status = "completed"
            transaction.completed_at = datetime.now()
            transaction.failure_reason = None

            return True

        except Exception as error:
            transaction.failure_reason = str(error)

            self.error_log.append(
                {
                    "transaction_id": transaction.transaction_id,
                    "error": str(error),
                    "attempt": transaction.attempts,
                    "timestamp": datetime.now()
                }
            )

            if transaction.attempts >= self.max_retries:
                transaction.status = "failed"

            return False

    # --------------------------------------------------------
    # Обработка очереди
    # --------------------------------------------------------

    def process_queue(self, queue):
        ready_transactions = queue.get_ready_transactions()

        for transaction in ready_transactions:
            while (
                transaction.status == "pending"
                and transaction.attempts < self.max_retries
            ):
                self.process_transaction(transaction)

    # --------------------------------------------------------
    # Повторная обработка одной транзакции
    # --------------------------------------------------------

    def retry_transaction(self, transaction):
        if transaction.status != "failed":
            return False

        if transaction.attempts >= self.max_retries:
            transaction.attempts = 0
            transaction.status = "pending"
            transaction.failure_reason = None

        return self.process_transaction(transaction)


# ============================================================
# ТЕСТИРОВАНИЕ
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ДЗ 4 — СИСТЕМА ТРАНЗАКЦИЙ")
    print("=" * 60)

    # --------------------------------------------------------
    # Создаем счета
    # --------------------------------------------------------

    account1 = BankAccount(
        owner="Наиля",
        balance=100000,
        status="active",
        currency="RUB"
    )

    account2 = BankAccount(
        owner="Иван",
        balance=50000,
        status="active",
        currency="RUB"
    )

    account3 = BankAccount(
        owner="Анна",
        balance=1000,
        status="active",
        currency="RUB"
    )

    premium_account = PremiumAccount(
        owner="Петр",
        balance=10000,
        status="active",
        currency="RUB",
        overdraft_limit=50000,
        commission=100
    )

    frozen_account = BankAccount(
        owner="Олег",
        balance=30000,
        status="frozen",
        currency="RUB"
    )

    usd_account = BankAccount(
        owner="Kate",
        balance=1000,
        status="active",
        currency="USD"
    )

    print("\nСчета до операций:")

    print(account1)
    print(account2)
    print(account3)
    print(premium_account)
    print(frozen_account)
    print(usd_account)

    # --------------------------------------------------------
    # Создаем очередь
    # --------------------------------------------------------

    queue = TransactionQueue()

    # --------------------------------------------------------
    # Создаем процессор
    # --------------------------------------------------------

    processor = TransactionProcessor()

    # ========================================================
    # 10 ТРАНЗАКЦИЙ
    # ========================================================

    # 1. Обычный внутренний перевод
    transaction1 = Transaction(
        transaction_type="internal",
        amount=5000,
        currency="RUB",
        sender=account1,
        receiver=account2,
        priority=2
    )

    # 2. Еще один внутренний перевод
    transaction2 = Transaction(
        transaction_type="internal",
        amount=3000,
        currency="RUB",
        sender=account2,
        receiver=account1,
        priority=1
    )

    # 3. Внешний перевод с комиссией
    transaction3 = Transaction(
        transaction_type="external",
        amount=10000,
        currency="RUB",
        sender=account1,
        receiver=account2,
        priority=3
    )

    # 4. Перевод с недостатком средств
    transaction4 = Transaction(
        transaction_type="internal",
        amount=5000,
        currency="RUB",
        sender=account3,
        receiver=account1,
        priority=2
    )

    # 5. Перевод с PremiumAccount
    transaction5 = Transaction(
        transaction_type="internal",
        amount=30000,
        currency="RUB",
        sender=premium_account,
        receiver=account1,
        priority=4
    )

    # 6. Перевод на замороженный счет
    transaction6 = Transaction(
        transaction_type="internal",
        amount=2000,
        currency="RUB",
        sender=account1,
        receiver=frozen_account,
        priority=2
    )

    # 7. Перевод RUB → USD
    transaction7 = Transaction(
        transaction_type="external",
        amount=10000,
        currency="RUB",
        sender=account1,
        receiver=usd_account,
        priority=3
    )

    # 8. Небольшой перевод
    transaction8 = Transaction(
        transaction_type="internal",
        amount=1000,
        currency="RUB",
        sender=account2,
        receiver=account1,
        priority=1
    )

    # 9. Еще один внешний перевод
    transaction9 = Transaction(
        transaction_type="external",
        amount=7000,
        currency="RUB",
        sender=account1,
        receiver=account2,
        priority=5
    )

    # 10. Отложенный перевод
    transaction10 = Transaction(
        transaction_type="internal",
        amount=1500,
        currency="RUB",
        sender=account2,
        receiver=account1,
        priority=2,
        execute_at=datetime.now() + timedelta(seconds=60)
    )

    transactions = [
        transaction1,
        transaction2,
        transaction3,
        transaction4,
        transaction5,
        transaction6,
        transaction7,
        transaction8,
        transaction9,
        transaction10
    ]

    # --------------------------------------------------------
    # Добавляем все транзакции в очередь
    # --------------------------------------------------------

    for transaction in transactions:
        queue.add_transaction(transaction)

    print("\nКоличество транзакций в очереди:")
    print(len(queue))

    # --------------------------------------------------------
    # Проверяем отмену транзакции
    # --------------------------------------------------------

    cancelled_transaction = Transaction(
        transaction_type="internal",
        amount=500,
        currency="RUB",
        sender=account1,
        receiver=account2,
        priority=1
    )

    queue.add_transaction(cancelled_transaction)

    print("\nОтмена отдельной транзакции:")
    print(
        queue.cancel_transaction(
            cancelled_transaction.transaction_id
        )
    )

    print(cancelled_transaction)

    # --------------------------------------------------------
    # Выводим порядок обработки по приоритету
    # --------------------------------------------------------

    print("\nТранзакции, готовые к выполнению:")

    ready_transactions = queue.get_ready_transactions()

    for transaction in ready_transactions:
        print(
            transaction.transaction_id,
            "priority:",
            transaction.priority
        )

    # --------------------------------------------------------
    # Выполняем очередь
    # --------------------------------------------------------

    print("\nОбработка очереди:")

    processor.process_queue(queue)

    # --------------------------------------------------------
    # Результаты транзакций
    # --------------------------------------------------------

    print("\nРезультаты транзакций:")

    for transaction in transactions:
        print(
            transaction.transaction_id,
            "|",
            transaction.status,
            "|",
            "попытки:",
            transaction.attempts,
            "|",
            "комиссия:",
            transaction.commission,
            "|",
            "ошибка:",
            transaction.failure_reason
        )

    # --------------------------------------------------------
    # Итоговые балансы
    # --------------------------------------------------------

    print("\nИтоговые балансы:")

    print(account1)
    print(account2)
    print(account3)
    print(premium_account)
    print(frozen_account)
    print(usd_account)

    # --------------------------------------------------------
    # Журнал ошибок
    # --------------------------------------------------------

    print("\nЖурнал ошибок:")

    for error in processor.error_log:
        print(
            error["transaction_id"],
            "|",
            error["error"],
            "| попытка:",
            error["attempt"]
        )

    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)