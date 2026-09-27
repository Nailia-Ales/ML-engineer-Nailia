from datetime import datetime, timedelta
from collections import Counter

from HW1.HW1 import BankAccount
from HW2.HW2 import PremiumAccount
from HW3.HW3 import Client, Bank
from HW4.HW4 import Transaction, TransactionQueue, TransactionProcessor
from HW5.HW5 import AuditLog, RiskAnalyzer, AuditReport


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def print_client_accounts(client, bank):
    """
    Показывает все счета клиента.
    """

    print(
        f"\nСчета клиента: {client.full_name}"
    )

    accounts = []

    for account in bank.accounts:
        if account.client_id == client.client_id:
            accounts.append(account)

    if not accounts:
        print("Счетов нет.")
        return

    for account in accounts:
        print(
            f"  {account}"
        )


def get_transaction_history(client, transactions):
    """
    Возвращает историю транзакций клиента.
    """

    history = []

    for transaction in transactions:

        if (
            transaction.sender.client_id == client.client_id
            or transaction.receiver.client_id == client.client_id
        ):
            history.append(transaction)

    return history


def print_client_history(client, transactions):
    """
    Показывает историю операций клиента.
    """

    print(
        f"\nИстория операций клиента: "
        f"{client.full_name}"
    )

    history = get_transaction_history(
        client,
        transactions
    )

    if not history:
        print("История операций отсутствует.")
        return

    for transaction in history:

        risk_level = (
            transaction.risk_level
            if transaction.risk_level is not None
            else "не анализировался"
        )

        print(
            f"  ID: {transaction.transaction_id} | "
            f"{transaction.amount} {transaction.currency} | "
            f"{transaction.transaction_type} | "
            f"статус: {transaction.status} | "
            f"риск: {risk_level}"
        )


def print_client_suspicious_operations(
    client,
    transactions
):
    """
    Показывает подозрительные операции клиента.
    """

    print(
        f"\nПодозрительные операции клиента: "
        f"{client.full_name}"
    )

    suspicious = []

    for transaction in transactions:

        if (
            transaction.sender.client_id == client.client_id
            or transaction.receiver.client_id == client.client_id
        ):

            if transaction.risk_level in (
                "средний",
                "высокий"
            ):
                suspicious.append(transaction)

    if not suspicious:
        print("Подозрительных операций нет.")
        return

    for transaction in suspicious:

        print(
            f"  ID: {transaction.transaction_id} | "
            f"{transaction.amount} {transaction.currency} | "
            f"риск: {transaction.risk_level} | "
            f"статус: {transaction.status}"
        )


def print_transaction_statistics(transactions):
    """
    Показывает статистику транзакций.
    """

    print(
        "\n========== СТАТИСТИКА ТРАНЗАКЦИЙ =========="
    )

    total = len(transactions)

    completed = 0
    failed = 0
    blocked = 0
    pending = 0
    cancelled = 0

    for transaction in transactions:

        if transaction.status == "completed":
            completed += 1

        elif transaction.status == "failed":
            failed += 1

        elif transaction.status == "blocked":
            blocked += 1

        elif transaction.status == "pending":
            pending += 1

        elif transaction.status == "cancelled":
            cancelled += 1

    print(
        "Всего транзакций:",
        total
    )

    print(
        "Выполнено:",
        completed
    )

    print(
        "Ошибок:",
        failed
    )

    print(
        "Заблокировано:",
        blocked
    )

    print(
        "Ожидает выполнения:",
        pending
    )

    print(
        "Отменено:",
        cancelled
    )

    # -----------------------------------------
    # Статистика по риску
    # -----------------------------------------

    risk_counter = Counter()

    for transaction in transactions:

        if transaction.risk_level is not None:
            risk_counter[transaction.risk_level] += 1

    print("\nПо уровню риска:")

    print(
        "  Низкий:",
        risk_counter["низкий"]
    )

    print(
        "  Средний:",
        risk_counter["средний"]
    )

    print(
        "  Высокий:",
        risk_counter["высокий"]
    )


def print_total_balance(bank):
    """
    Показывает общий баланс банка
    отдельно по каждой валюте.
    """

    print(
        "\n========== ОБЩИЙ БАЛАНС =========="
    )

    balances = {}

    for account in bank.accounts:

        currency = account.currency

        if currency not in balances:
            balances[currency] = 0

        balances[currency] += account.balance

    for currency, balance in balances.items():

        print(
            f"{currency}: {balance}"
        )


# ============================================================
# ОСНОВНАЯ ПРОГРАММА
# ============================================================

if __name__ == "__main__":

    print(
        "=================================================="
    )
    print(
        "              ДЕНЬ 6 — ДЕМО БАНКА"
    )
    print(
        "=================================================="
    )

    # ========================================================
    # 1. СОЗДАЁМ БАНК
    # ========================================================

    bank = Bank("Demo Bank")

    print(
        "\nБанк создан:",
        bank.name
    )

    # ========================================================
    # 2. СОЗДАЁМ ЖУРНАЛ АУДИТА
    # ========================================================

    audit_log = AuditLog(
        "audit_day6.log"
    )

    print(
        "Журнал аудита создан."
    )

    # ========================================================
    # 3. СОЗДАЁМ АНАЛИЗАТОР РИСКА
    # ========================================================

    risk_analyzer = RiskAnalyzer(
        audit_log=audit_log,
        large_amount_threshold=100000,
        frequent_operations_limit=3
    )

    print(
        "Анализатор риска создан."
    )

    # ========================================================
    # 4. СОЗДАЁМ ПРОЦЕССОР ТРАНЗАКЦИЙ
    # ========================================================

    transaction_processor = TransactionProcessor(
        max_retries=3
    )

    print(
        "Процессор транзакций создан."
    )

    # ========================================================
    # 5. СОЗДАЁМ ОЧЕРЕДЬ
    # ========================================================

    transaction_queue = TransactionQueue()

    print(
        "Очередь транзакций создана."
    )

    # ========================================================
    # 6. СОЗДАЁМ КЛИЕНТОВ
    # ========================================================

    clients = [
        Client(
            full_name="Иван Иванов",
            client_id="001",
            age=30,
            status="active",
            contacts="ivan@mail.ru",
            password="1111"
        ),

        Client(
            full_name="Анна Петрова",
            client_id="002",
            age=28,
            status="active",
            contacts="anna@mail.ru",
            password="2222"
        ),

        Client(
            full_name="Пётр Сидоров",
            client_id="003",
            age=35,
            status="active",
            contacts="petr@mail.ru",
            password="3333"
        ),

        Client(
            full_name="Мария Смирнова",
            client_id="004",
            age=31,
            status="active",
            contacts="maria@mail.ru",
            password="4444"
        ),

        Client(
            full_name="Алексей Кузнецов",
            client_id="005",
            age=40,
            status="active",
            contacts="alex@mail.ru",
            password="5555"
        ),

        Client(
            full_name="Елена Попова",
            client_id="006",
            age=27,
            status="active",
            contacts="elena@mail.ru",
            password="6666"
        )
    ]

    for client in clients:
        bank.add_client(client)

    print(
        f"\nСоздано клиентов: {len(clients)}"
    )

    # ========================================================
    # 7. СОЗДАЁМ СЧЕТА
    # ========================================================

    account1 = BankAccount(
        owner="Иван Иванов",
        balance=500000,
        status="active",
        currency="RUB"
    )

    account2 = BankAccount(
        owner="Иван Иванов",
        balance=120000,
        status="active",
        currency="RUB"
    )

    account3 = BankAccount(
        owner="Анна Петрова",
        balance=300000,
        status="active",
        currency="RUB"
    )

    account4 = BankAccount(
        owner="Анна Петрова",
        balance=80000,
        status="active",
        currency="RUB"
    )

    account5 = BankAccount(
        owner="Пётр Сидоров",
        balance=250000,
        status="active",
        currency="RUB"
    )

    account6 = BankAccount(
        owner="Пётр Сидоров",
        balance=60000,
        status="active",
        currency="RUB"
    )

    account7 = BankAccount(
        owner="Мария Смирнова",
        balance=180000,
        status="active",
        currency="RUB"
    )

    account8 = BankAccount(
        owner="Мария Смирнова",
        balance=70000,
        status="active",
        currency="RUB"
    )

    account9 = BankAccount(
        owner="Алексей Кузнецов",
        balance=450000,
        status="active",
        currency="RUB"
    )

    account10 = BankAccount(
        owner="Алексей Кузнецов",
        balance=90000,
        status="active",
        currency="RUB"
    )

    account11 = BankAccount(
        owner="Елена Попова",
        balance=220000,
        status="active",
        currency="RUB"
    )

    account12 = PremiumAccount(
        owner="Елена Попова",
        balance=50000,
        status="active",
        currency="RUB",
        overdraft_limit=30000,
        commission=100
    )

    accounts = [
        account1,
        account2,
        account3,
        account4,
        account5,
        account6,
        account7,
        account8,
        account9,
        account10,
        account11,
        account12
    ]

    # Открываем счета через банк.
    for client, client_accounts in [
        (clients[0], [account1, account2]),
        (clients[1], [account3, account4]),
        (clients[2], [account5, account6]),
        (clients[3], [account7, account8]),
        (clients[4], [account9, account10]),
        (clients[5], [account11, account12])
    ]:

        for account in client_accounts:
            bank.open_account(
                client,
                account
            )

    print(
        f"Создано счетов: {len(bank.accounts)}"
    )

    # ========================================================
    # 8. ПОКАЗЫВАЕМ СЧЕТА КЛИЕНТОВ
    # ========================================================

    print(
        "\n========== СЧЕТА КЛИЕНТОВ =========="
    )

    for client in clients:
        print_client_accounts(
            client,
            bank
        )

    # ========================================================
    # 9. ЗАМОРАЖИВАЕМ ОДИН СЧЕТ
    # ========================================================

    bank.freeze_account(
        clients[3],
        account8
    )

    print(
        "\nСчет",
        account8.account_id,
        "заморожен для демонстрации ошибки."
    )

    # ========================================================
    # 10. СОЗДАЁМ 38 ТРАНЗАКЦИЙ
    # ========================================================

    transactions = []

    # --------------------------------------------------------
    # Обычные операции
    # --------------------------------------------------------

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=5000,
            currency="RUB",
            sender=account1,
            receiver=account3,
            priority=2
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=7000,
            currency="RUB",
            sender=account3,
            receiver=account5,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=3000,
            currency="RUB",
            sender=account5,
            receiver=account7,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=4000,
            currency="RUB",
            sender=account7,
            receiver=account9,
            priority=2
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=6000,
            currency="RUB",
            sender=account9,
            receiver=account11,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=2500,
            currency="RUB",
            sender=account11,
            receiver=account1,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=8000,
            currency="RUB",
            sender=account2,
            receiver=account4,
            priority=2
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=9000,
            currency="RUB",
            sender=account4,
            receiver=account6,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=3500,
            currency="RUB",
            sender=account6,
            receiver=account10,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=4500,
            currency="RUB",
            sender=account10,
            receiver=account12,
            priority=2
        )
    )

    # --------------------------------------------------------
    # Ещё обычные операции
    # --------------------------------------------------------

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=5500,
            currency="RUB",
            sender=account1,
            receiver=account5,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=6500,
            currency="RUB",
            sender=account3,
            receiver=account7,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=7500,
            currency="RUB",
            sender=account5,
            receiver=account9,
            priority=2
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=8500,
            currency="RUB",
            sender=account7,
            receiver=account11,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=9500,
            currency="RUB",
            sender=account9,
            receiver=account1,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=11000,
            currency="RUB",
            sender=account11,
            receiver=account3,
            priority=2
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=12000,
            currency="RUB",
            sender=account2,
            receiver=account6,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=13000,
            currency="RUB",
            sender=account4,
            receiver=account10,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=14000,
            currency="RUB",
            sender=account6,
            receiver=account12,
            priority=2
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=15000,
            currency="RUB",
            sender=account10,
            receiver=account2,
            priority=1
        )
    )

    # --------------------------------------------------------
    # Подозрительные крупные операции
    # --------------------------------------------------------

    transactions.append(
        Transaction(
            transaction_type="external",
            amount=150000,
            currency="RUB",
            sender=account1,
            receiver=account3,
            priority=3
        )
    )

    transactions.append(
        Transaction(
            transaction_type="external",
            amount=200000,
            currency="RUB",
            sender=account3,
            receiver=account5,
            priority=3
        )
    )

    transactions.append(
        Transaction(
            transaction_type="external",
            amount=250000,
            currency="RUB",
            sender=account5,
            receiver=account7,
            priority=3
        )
    )

    transactions.append(
        Transaction(
            transaction_type="external",
            amount=180000,
            currency="RUB",
            sender=account7,
            receiver=account9,
            priority=3
        )
    )

    transactions.append(
        Transaction(
            transaction_type="external",
            amount=300000,
            currency="RUB",
            sender=account9,
            receiver=account11,
            priority=3
        )
    )

    transactions.append(
        Transaction(
            transaction_type="external",
            amount=220000,
            currency="RUB",
            sender=account11,
            receiver=account1,
            priority=3
        )
    )

    # --------------------------------------------------------
    # Операции для проверки частоты
    # --------------------------------------------------------

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=1000,
            currency="RUB",
            sender=account1,
            receiver=account2,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=1100,
            currency="RUB",
            sender=account1,
            receiver=account2,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=1200,
            currency="RUB",
            sender=account1,
            receiver=account2,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=1300,
            currency="RUB",
            sender=account1,
            receiver=account2,
            priority=1
        )
    )

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=1400,
            currency="RUB",
            sender=account1,
            receiver=account2,
            priority=1
        )
    )

    # --------------------------------------------------------
    # Ошибочные операции
    # --------------------------------------------------------

    # Недостаточно средств
    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=80000,
            currency="RUB",
            sender=account4,
            receiver=account1,
            priority=2
        )
    )

    # Замороженный счёт получателя
    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=5000,
            currency="RUB",
            sender=account3,
            receiver=account8,
            priority=2
        )
    )

    # Недостаточно средств
    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=100000,
            currency="RUB",
            sender=account6,
            receiver=account2,
            priority=2
        )
    )

    # Большая сумма + недостаточно средств
    transactions.append(
        Transaction(
            transaction_type="external",
            amount=900000,
            currency="RUB",
            sender=account2,
            receiver=account4,
            priority=3
        )
    )

    # Замороженный счёт
    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=3000,
            currency="RUB",
            sender=account7,
            receiver=account8,
            priority=2
        )
    )

    # --------------------------------------------------------
    # Операция с PremiumAccount
    # --------------------------------------------------------

    transactions.append(
        Transaction(
            transaction_type="internal",
            amount=60000,
            currency="RUB",
            sender=account12,
            receiver=account1,
            priority=2
        )
    )

    # --------------------------------------------------------
    # Отложенная операция
    # --------------------------------------------------------

    delayed_transaction = Transaction(
        transaction_type="internal",
        amount=10000,
        currency="RUB",
        sender=account2,
        receiver=account3,
        priority=2,
        execute_at=datetime.now() + timedelta(hours=1)
    )

    transactions.append(
        delayed_transaction
    )

    print(
        f"\nСоздано транзакций: {len(transactions)}"
    )

    # ========================================================
    # 11. ИНИЦИАЛИЗИРУЕМ УРОВЕНЬ РИСКА
    # ========================================================

    # Transaction из HW4 не создаёт risk_level
    # самостоятельно, поэтому задаём его для всех
    # транзакций до начала анализа.

    for transaction in transactions:
        transaction.risk_level = None

    # ========================================================
    # 12. ДОБАВЛЯЕМ ТРАНЗАКЦИИ В ОЧЕРЕДЬ
    # ========================================================

    print(
        "\n========== ДОБАВЛЕНИЕ В ОЧЕРЕДЬ =========="
    )

    for transaction in transactions:

        transaction_queue.add_transaction(
            transaction
        )

        audit_log.log(
            "INFO",
            "Транзакция добавлена в очередь",
            transaction
        )

        print(
            f"В очередь добавлена транзакция "
            f"{transaction.transaction_id} | "
            f"приоритет={transaction.priority}"
        )

    print(
        "\nРазмер очереди:",
        len(transaction_queue)
    )

    # ========================================================
    # 13. ОТМЕНЯЕМ ОТЛОЖЕННУЮ ТРАНЗАКЦИЮ
    # ========================================================

    cancelled = transaction_queue.cancel_transaction(
        delayed_transaction.transaction_id
    )

    if cancelled:

        audit_log.log(
            "WARNING",
            "Отложенная транзакция отменена",
            delayed_transaction
        )

        print(
            "\nТранзакция",
            delayed_transaction.transaction_id,
            "отменена."
        )

    # ========================================================
    # 14. АНАЛИЗ РИСКА
    # ========================================================

    print(
        "\n========== АНАЛИЗ РИСКА =========="
    )

    for transaction in transactions:

        # Отменённую транзакцию не анализируем
        if transaction.status == "cancelled":
            continue

        risk_result = risk_analyzer.analyze_transaction(
            transaction
        )

        print(
            f"Транзакция "
            f"{transaction.transaction_id} | "
            f"сумма={transaction.amount} | "
            f"риск={risk_result['risk_level']} | "
            f"баллы={risk_result['risk_points']}"
        )

        if risk_result["reasons"]:

            print(
                "  Причины:",
                ", ".join(
                    risk_result["reasons"]
                )
            )

        # ----------------------------------------------------
        # Блокировка высокого риска
        # ----------------------------------------------------

        if risk_analyzer.is_dangerous(
            risk_result
        ):

            transaction.status = "blocked"

            audit_log.log(
                "ERROR",
                "Операция заблокирована из-за высокого риска",
                transaction
            )

            print(
                "  Результат: ЗАБЛОКИРОВАНА"
            )

    # ========================================================
    # 15. ПОЛУЧАЕМ ГОТОВЫЕ ТРАНЗАКЦИИ ИЗ ОЧЕРЕДИ
    # ========================================================

    print(
        "\n========== ПОЛУЧЕНИЕ ТРАНЗАКЦИЙ ИЗ ОЧЕРЕДИ =========="
    )

    ready_transactions = (
        transaction_queue.get_ready_transactions()
    )

    print(
        "Готовых к выполнению:",
        len(ready_transactions)
    )

    # ========================================================
    # 16. ВЫПОЛНЯЕМ ТРАНЗАКЦИИ
    # ========================================================

    print(
        "\n========== ВЫПОЛНЕНИЕ ТРАНЗАКЦИЙ =========="
    )

    for transaction in ready_transactions:

        # Заблокированные операции не выполняем
        if transaction.status == "blocked":

            print(
                f"{transaction.transaction_id} | "
                f"пропущена: операция заблокирована"
            )

            continue

        # Отменённые операции не выполняем
        if transaction.status == "cancelled":

            print(
                f"{transaction.transaction_id} | "
                f"пропущена: операция отменена"
            )

            continue

        audit_log.log(
            "INFO",
            "Транзакция передана на выполнение",
            transaction
        )

        print(
            f"\nВыполняется "
            f"{transaction.transaction_id}"
        )

        # ----------------------------------------------------
        # Выполняем транзакцию с учётом повторных попыток
        # ----------------------------------------------------

        success = False

        while (
            transaction.status == "pending"
            and transaction.attempts
            < transaction_processor.max_retries
        ):

            success = (
                transaction_processor.process_transaction(
                    transaction
                )
            )

            if success:
                break

        if success:

            audit_log.log(
                "INFO",
                "Транзакция успешно выполнена",
                transaction
            )

            print(
                "  Результат: ВЫПОЛНЕНО"
            )

        else:

            # После максимального количества попыток
            # считаем операцию окончательно отклонённой.

            if transaction.status == "pending":
                transaction.status = "failed"

            audit_log.log(
                "ERROR",
                f"Транзакция окончательно отклонена: "
                f"{transaction.failure_reason}",
                transaction
            )

            print(
                "  Результат: ОТКЛОНЕНА"
            )

            print(
                "  Причина:",
                transaction.failure_reason
            )

            print(
                "  Количество попыток:",
                transaction.attempts
            )

    # ========================================================
    # 17. СОЗДАЁМ ОТЧЁТ
    # ========================================================

    report = AuditReport(
        audit_log,
        risk_analyzer
    )

    report.transactions = transactions

    print(
        "\n========== ОТЧЁТ АУДИТА СОЗДАН =========="
    )

    # ========================================================
    # 18. ПОЛЬЗОВАТЕЛЬСКИЕ СЦЕНАРИИ
    # ========================================================

    print(
        "\n=================================================="
    )
    print(
        "           ПОЛЬЗОВАТЕЛЬСКИЕ СЦЕНАРИИ"
    )
    print(
        "=================================================="
    )

    selected_client = clients[0]

    # --------------------------------------------------------
    # Счета клиента
    # --------------------------------------------------------

    print_client_accounts(
        selected_client,
        bank
    )

    # --------------------------------------------------------
    # История операций
    # --------------------------------------------------------

    print_client_history(
        selected_client,
        transactions
    )

    # --------------------------------------------------------
    # Подозрительные операции
    # --------------------------------------------------------

    print_client_suspicious_operations(
        selected_client,
        transactions
    )

    # ========================================================
    # 19. ПОДОЗРИТЕЛЬНЫЕ ОПЕРАЦИИ ВСЕГО БАНКА
    # ========================================================

    print(
        "\n========== ПОДОЗРИТЕЛЬНЫЕ ОПЕРАЦИИ БАНКА =========="
    )

    suspicious_transactions = (
        report.suspicious_transactions()
    )

    if suspicious_transactions:

        for transaction in suspicious_transactions:

            print(
                f"ID: {transaction.transaction_id} | "
                f"Сумма: {transaction.amount} "
                f"{transaction.currency} | "
                f"Риск: {transaction.risk_level} | "
                f"Статус: {transaction.status}"
            )

    else:

        print(
            "Подозрительных операций нет."
        )

    # ========================================================
    # 20. ТОП-3 КЛИЕНТОВ
    # ========================================================

    print(
        "\n========== ТОП-3 КЛИЕНТОВ =========="
    )

    ranking = bank.get_clients_ranking()

    top_three = ranking[:3]

    for position, item in enumerate(
        top_three,
        start=1
    ):

        client = item[0]
        balance = item[1]

        print(
            f"{position}. "
            f"{client.full_name} | "
            f"баланс: {balance} RUB"
        )

    # ========================================================
    # 21. СТАТИСТИКА ТРАНЗАКЦИЙ
    # ========================================================

    print_transaction_statistics(
        transactions
    )

    # ========================================================
    # 22. ОБЩИЙ БАЛАНС
    # ========================================================

    print_total_balance(
        bank
    )

    # ========================================================
    # 23. СТАТИСТИКА ОШИБОК
    # ========================================================

    print(
        "\n========== СТАТИСТИКА ОШИБОК =========="
    )

    error_statistics = (
        report.error_statistics()
    )

    print(
        "Всего ERROR:",
        error_statistics["total_errors"]
    )

    for message, count in (
        error_statistics["error_messages"].items()
    ):

        print(
            f"{message}: {count}"
        )

    # ========================================================
    # 24. РИСК-ПРОФИЛИ КЛИЕНТОВ
    # ========================================================

    print(
        "\n========== РИСК-ПРОФИЛИ КЛИЕНТОВ =========="
    )

    for client in clients:

        profile = report.client_risk_profile(
            client
        )

        print(
            f"\n{profile['client']}"
        )

        print(
            "  Общий риск:",
            profile["risk_profile"]
        )

        print(
            "  Высокий риск:",
            profile["high_risk_operations"]
        )

        print(
            "  Средний риск:",
            profile["medium_risk_operations"]
        )

        print(
            "  Низкий риск:",
            profile["low_risk_operations"]
        )

    # ========================================================
    # 25. ФИНАЛЬНЫЙ АУДИТ
    # ========================================================

    print(
        "\n========== ФИНАЛЬНЫЙ АУДИТ =========="
    )

    print(
        "Всего транзакций:",
        len(transactions)
    )

    print(
        "Записей аудита:",
        len(audit_log.logs)
    )

    print(
        "INFO:",
        len(
            audit_log.filter_by_level("INFO")
        )
    )

    print(
        "WARNING:",
        len(
            audit_log.filter_by_level("WARNING")
        )
    )

    print(
        "ERROR:",
        len(
            audit_log.filter_by_level("ERROR")
        )
    )

    # --------------------------------------------------------
    # Итоговое количество статусов
    # --------------------------------------------------------

    status_counter = Counter(
        transaction.status
        for transaction in transactions
    )

    print(
        "\nСтатусы транзакций:"
    )

    print(
        "  completed:",
        status_counter["completed"]
    )

    print(
        "  failed:",
        status_counter["failed"]
    )

    print(
        "  blocked:",
        status_counter["blocked"]
    )

    print(
        "  cancelled:",
        status_counter["cancelled"]
    )

    print(
        "  pending:",
        status_counter["pending"]
    )

    print(
        "\nЛоги сохранены в файл:",
        "audit_day6.log"
    )

    print(
        "\n=================================================="
    )
    print(
        "             ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА"
    )
    print(
        "=================================================="
    )