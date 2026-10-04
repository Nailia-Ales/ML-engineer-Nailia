from datetime import datetime, time, timedelta
from collections import Counter

from HW1.HW1 import BankAccount
from HW2.HW2 import PremiumAccount
from HW3.HW3 import Client
from HW4.HW4 import Transaction


class AuditLog:
    """
    Система аудита банковских операций.
    Хранит события в памяти и сохраняет их в файл.
    """

    def __init__(self, file_name="audit.log"):
        self.logs = []
        self.file_name = file_name

    def log(self, level, message, transaction=None):
        """
        Добавляет запись в журнал.
        """

        log_entry = {
            "timestamp": datetime.now(),
            "level": level,
            "message": message,
            "transaction_id": (
                transaction.transaction_id
                if transaction is not None
                else None
            )
        }

        self.logs.append(log_entry)

        with open(self.file_name, "a", encoding="utf-8") as file:
            file.write(
                f"{log_entry['timestamp']} | "
                f"{log_entry['level']} | "
                f"{log_entry['message']} | "
                f"transaction_id={log_entry['transaction_id']}\n"
            )

    def filter_by_level(self, level):
        """
        Возвращает записи определённого уровня важности.
        """

        return [
            log
            for log in self.logs
            if log["level"] == level
        ]

    def get_all_logs(self):
        """
        Возвращает все записи аудита.
        """

        return self.logs


class RiskAnalyzer:
    """
    Анализатор риска транзакций.
    """

    def __init__(
        self,
        audit_log,
        large_amount_threshold=100000,
        frequent_operations_limit=3
    ):
        self.audit_log = audit_log
        self.large_amount_threshold = large_amount_threshold
        self.frequent_operations_limit = frequent_operations_limit

        self.client_operations = {}
        self.known_receivers = {}

    def _get_risk_level(self, risk_points):
        """
        Определяет уровень риска по количеству баллов.
        """

        if risk_points >= 6:
            return "высокий"

        elif risk_points >= 3:
            return "средний"

        else:
            return "низкий"

    def analyze_transaction(self, transaction):
        """
        Анализирует одну транзакцию.
        """

        risk_points = 0
        reasons = []

        # -----------------------------------------
        # 1. Проверка крупной суммы
        # -----------------------------------------

        if transaction.amount >= self.large_amount_threshold:
            risk_points += 3
            reasons.append("крупная сумма")

        # -----------------------------------------
        # 2. Проверка частых операций
        # -----------------------------------------

        sender_id = transaction.sender.client_id

        if sender_id not in self.client_operations:
            self.client_operations[sender_id] = []

        now = transaction.created_at

        recent_operations = []

        for operation_time in self.client_operations[sender_id]:
            if now - operation_time <= timedelta(hours=1):
                recent_operations.append(operation_time)

        self.client_operations[sender_id] = recent_operations

        if len(recent_operations) >= self.frequent_operations_limit:
            risk_points += 2
            reasons.append("слишком частые операции")

        self.client_operations[sender_id].append(now)

        # -----------------------------------------
        # 3. Проверка нового счёта получателя
        # -----------------------------------------

        if sender_id not in self.known_receivers:
            self.known_receivers[sender_id] = set()

        # ВАЖНО:
        # Запоминаем именно account_id получателя,
        # а не client_id.
        #
        # У одного клиента может быть несколько счетов.
        # Поэтому client_id здесь недостаточно.
        receiver_account_id = transaction.receiver.account_id

        if receiver_account_id not in self.known_receivers[sender_id]:
            risk_points += 2
            reasons.append("перевод на новый счёт")

        self.known_receivers[sender_id].add(receiver_account_id)

        # -----------------------------------------
        # 4. Проверка ночной операции
        # -----------------------------------------

        transaction_time = transaction.created_at.time()

        if time(0, 0) <= transaction_time < time(5, 0):
            risk_points += 3
            reasons.append("операция выполнена ночью")

        # -----------------------------------------
        # 5. Определяем уровень риска
        # -----------------------------------------

        risk_level = self._get_risk_level(risk_points)

        # Сохраняем уровень риска прямо в транзакции
        transaction.risk_level = risk_level

        result = {
            "transaction_id": transaction.transaction_id,
            "risk_level": risk_level,
            "risk_points": risk_points,
            "reasons": reasons
        }

        # -----------------------------------------
        # 6. Записываем результат в аудит
        # -----------------------------------------

        if risk_level == "высокий":

            self.audit_log.log(
                "ERROR",
                f"Высокий риск: {', '.join(reasons)}",
                transaction
            )

        elif risk_level == "средний":

            self.audit_log.log(
                "WARNING",
                f"Средний риск: {', '.join(reasons)}",
                transaction
            )

        else:

            self.audit_log.log(
                "INFO",
                "Операция имеет низкий уровень риска",
                transaction
            )

        return result

    def is_dangerous(self, risk_result):
        """
        Определяет, нужно ли блокировать операцию.
        """

        return risk_result["risk_level"] == "высокий"


class AuditReport:
    """
    Формирование отчётов аудита.
    """

    def __init__(self, audit_log, risk_analyzer):
        self.audit_log = audit_log
        self.risk_analyzer = risk_analyzer
        self.transactions = []

    def suspicious_transactions(self):
        """
        Возвращает подозрительные операции.
        """

        result = []

        for transaction in self.transactions:

            if transaction.risk_level in ("средний", "высокий"):
                result.append(transaction)

        return result

    def client_risk_profile(self, client):
        """
        Возвращает риск-профиль конкретного клиента.
        """

        client_transactions = []

        # Находим все транзакции, связанные с клиентом
        for transaction in self.transactions:

            sender_client_id = transaction.sender.client_id
            receiver_client_id = transaction.receiver.client_id

            if (
                sender_client_id == client.client_id
                or receiver_client_id == client.client_id
            ):
                client_transactions.append(transaction)

        high_risk = 0
        medium_risk = 0
        low_risk = 0

        # Считаем каждую транзакцию только один раз
        for transaction in client_transactions:

            if transaction.risk_level == "высокий":
                high_risk += 1

            elif transaction.risk_level == "средний":
                medium_risk += 1

            elif transaction.risk_level == "низкий":
                low_risk += 1

        # Определяем общий риск-профиль клиента
        if high_risk > 0:
            profile = "высокий"

        elif medium_risk > 0:
            profile = "средний"

        else:
            profile = "низкий"

        return {
            "client": client.full_name,
            "risk_profile": profile,
            "high_risk_operations": high_risk,
            "medium_risk_operations": medium_risk,
            "low_risk_operations": low_risk
        }

    def error_statistics(self):
        """
        Возвращает статистику ошибок аудита.
        """

        error_logs = self.audit_log.filter_by_level("ERROR")

        return {
            "total_errors": len(error_logs),
            "error_messages": Counter(
                log["message"]
                for log in error_logs
            )
        }


# ============================================================
# ТЕСТИРОВАНИЕ
# ============================================================

if __name__ == "__main__":

    print("========== ДЕНЬ 5 ==========")

    # ========================================================
    # 1. СОЗДАЁМ БАНК
    # ========================================================

    from HW3.HW3 import Bank

    bank = Bank("Demo Bank")

    print("\nБанк создан.")

    # ========================================================
    # 2. СОЗДАЁМ ЖУРНАЛ АУДИТА
    # ========================================================

    audit_log = AuditLog("audit.log")

    print("Журнал аудита создан.")

    # ========================================================
    # 3. СОЗДАЁМ АНАЛИЗАТОР РИСКА
    # ========================================================

    risk_analyzer = RiskAnalyzer(
        audit_log=audit_log,
        large_amount_threshold=100000,
        frequent_operations_limit=3
    )

    print("Анализатор риска создан.")

    # ========================================================
    # 4. СОЗДАЁМ КЛИЕНТОВ
    # ========================================================

    client1 = Client(
        full_name="Иван Иванов",
        client_id="001",
        age=30,
        status="active",
        contacts="ivan@mail.ru",
        password="1234"
    )

    client2 = Client(
        full_name="Анна Петрова",
        client_id="002",
        age=28,
        status="active",
        contacts="anna@mail.ru",
        password="5678"
    )

    client3 = Client(
        full_name="Пётр Сидоров",
        client_id="003",
        age=35,
        status="active",
        contacts="petr@mail.ru",
        password="9999"
    )

    bank.add_client(client1)
    bank.add_client(client2)
    bank.add_client(client3)

    print("\nКлиенты созданы.")

    # ========================================================
    # 5. СОЗДАЁМ СЧЕТА
    # ========================================================

    account1 = BankAccount(
        owner="Иван Иванов",
        balance=500000,
        status="active",
        currency="RUB"
    )

    account2 = BankAccount(
        owner="Анна Петрова",
        balance=300000,
        status="active",
        currency="RUB"
    )

    account3 = BankAccount(
        owner="Пётр Сидоров",
        balance=250000,
        status="active",
        currency="RUB"
    )

    # Открываем счета через банк.
    # В этот момент каждому счёту добавляется client_id.
    bank.open_account(client1, account1)
    bank.open_account(client2, account2)
    bank.open_account(client3, account3)

    print("\nСчета созданы.")

    print(account1)
    print(account2)
    print(account3)

    # ========================================================
    # 6. СОЗДАЁМ ТРАНЗАКЦИИ
    # ========================================================

    transactions = []

    transaction1 = Transaction(
        transaction_type="internal",
        amount=5000,
        currency="RUB",
        sender=account1,
        receiver=account2
    )

    transaction2 = Transaction(
        transaction_type="internal",
        amount=7000,
        currency="RUB",
        sender=account1,
        receiver=account2
    )

    transaction3 = Transaction(
        transaction_type="internal",
        amount=3000,
        currency="RUB",
        sender=account2,
        receiver=account1
    )

    transaction4 = Transaction(
        transaction_type="external",
        amount=500000,
        currency="RUB",
        sender=account1,
        receiver=account3
    )

    transaction5 = Transaction(
        transaction_type="internal",
        amount=2000,
        currency="RUB",
        sender=account3,
        receiver=account1
    )

    transaction6 = Transaction(
        transaction_type="internal",
        amount=150000,
        currency="RUB",
        sender=account2,
        receiver=account3
    )

    transaction7 = Transaction(
        transaction_type="internal",
        amount=1000,
        currency="RUB",
        sender=account1,
        receiver=account2
    )

    transaction8 = Transaction(
        transaction_type="internal",
        amount=1200,
        currency="RUB",
        sender=account1,
        receiver=account2
    )

    transaction9 = Transaction(
        transaction_type="external",
        amount=250000,
        currency="RUB",
        sender=account3,
        receiver=account2
    )

    transaction10 = Transaction(
        transaction_type="internal",
        amount=900,
        currency="RUB",
        sender=account2,
        receiver=account1
    )

    transactions.extend([
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
    ])

    print(
        f"\nСоздано транзакций: {len(transactions)}"
    )

    # ========================================================
    # 7. АНАЛИЗИРУЕМ ТРАНЗАКЦИИ
    # ========================================================

    print("\n========== АНАЛИЗ ТРАНЗАКЦИЙ ==========")

    for transaction in transactions:

        risk_result = risk_analyzer.analyze_transaction(
            transaction
        )

        print(
            f"\nТранзакция: "
            f"{transaction.transaction_id}"
        )

        print(
            f"Сумма: "
            f"{transaction.amount} "
            f"{transaction.currency}"
        )

        print(
            f"Уровень риска: "
            f"{risk_result['risk_level']}"
        )

        print(
            f"Баллы риска: "
            f"{risk_result['risk_points']}"
        )

        if risk_result["reasons"]:

            print(
                "Причины:",
                ", ".join(risk_result["reasons"])
            )

        else:

            print("Причины: нет")

        # ====================================================
        # БЛОКИРОВКА ОПАСНОЙ ОПЕРАЦИИ
        # ====================================================

        if risk_analyzer.is_dangerous(risk_result):

            transaction.status = "blocked"

            print(
                "РЕЗУЛЬТАТ: "
                "операция заблокирована"
            )

            audit_log.log(
                "ERROR",
                "Опасная операция заблокирована",
                transaction
            )

        else:

            transaction.status = "completed"

            print(
                "РЕЗУЛЬТАТ: "
                "операция разрешена"
            )

    # ========================================================
    # 8. ПРОВЕРКА НОЧНОЙ ОПЕРАЦИИ
    # ========================================================

    night_transaction = Transaction(
        transaction_type="external",
        amount=200000,
        currency="RUB",
        sender=account1,
        receiver=account3,
        commission=300
    )

    # Искусственно устанавливаем ночное время
    night_transaction.created_at = datetime.now().replace(
        hour=2,
        minute=30,
        second=0,
        microsecond=0
    )

    transactions.append(night_transaction)

    print(
        "\n========== НОЧНАЯ ОПЕРАЦИЯ =========="
    )

    night_result = risk_analyzer.analyze_transaction(
        night_transaction
    )

    print(
        f"Уровень риска: "
        f"{night_result['risk_level']}"
    )

    print(
        f"Баллы риска: "
        f"{night_result['risk_points']}"
    )

    print(
        "Причины:",
        ", ".join(night_result["reasons"])
    )

    if risk_analyzer.is_dangerous(night_result):

        night_transaction.status = "blocked"

        print(
            "РЕЗУЛЬТАТ: "
            "операция заблокирована"
        )

        audit_log.log(
            "ERROR",
            "Ночная опасная операция заблокирована",
            night_transaction
        )

    else:

        night_transaction.status = "completed"

        print(
            "РЕЗУЛЬТАТ: "
            "операция разрешена"
        )

    # ========================================================
    # 9. СОЗДАЁМ ОТЧЁТ
    # ========================================================

    report = AuditReport(
        audit_log,
        risk_analyzer
    )

    report.transactions = transactions

    print("\nОтчёт аудита создан.")

    # ========================================================
    # 10. ПОДОЗРИТЕЛЬНЫЕ ОПЕРАЦИИ
    # ========================================================

    print(
        "\n========== ПОДОЗРИТЕЛЬНЫЕ ОПЕРАЦИИ =========="
    )

    suspicious = report.suspicious_transactions()

    if suspicious:

        for transaction in suspicious:

            print(
                f"ID: {transaction.transaction_id} | "
                f"Сумма: {transaction.amount} "
                f"{transaction.currency} | "
                f"Риск: {transaction.risk_level} | "
                f"Статус: {transaction.status}"
            )

    else:

        print("Подозрительных операций нет.")

    # ========================================================
    # 11. ФИЛЬТРАЦИЯ ERROR ЛОГОВ
    # ========================================================

    print(
        "\n========== ERROR ЛОГИ =========="
    )

    error_logs = audit_log.filter_by_level("ERROR")

    if error_logs:

        for log in error_logs:

            print(
                log["timestamp"],
                "|",
                log["message"]
            )

    else:

        print("ERROR логов нет.")

    # ========================================================
    # 12. РИСК-ПРОФИЛИ КЛИЕНТОВ
    # ========================================================

    print(
        "\n========== РИСК-ПРОФИЛИ КЛИЕНТОВ =========="
    )

    for client in [client1, client2, client3]:

        profile = report.client_risk_profile(
            client
        )

        print(
            f"\nКлиент: "
            f"{profile['client']}"
        )

        print(
            f"Общий риск: "
            f"{profile['risk_profile']}"
        )

        print(
            f"Высокий риск: "
            f"{profile['high_risk_operations']}"
        )

        print(
            f"Средний риск: "
            f"{profile['medium_risk_operations']}"
        )

        print(
            f"Низкий риск: "
            f"{profile['low_risk_operations']}"
        )

    # ========================================================
    # 13. СТАТИСТИКА ОШИБОК
    # ========================================================

    print(
        "\n========== СТАТИСТИКА ОШИБОК =========="
    )

    statistics = report.error_statistics()

    print(
        "Всего ошибок:",
        statistics["total_errors"]
    )

    for message, count in (
        statistics["error_messages"].items()
    ):

        print(
            f"{message}: {count}"
        )

    # ========================================================
    # 14. ВСЕ ЗАПИСИ АУДИТА
    # ========================================================

    print(
        "\n========== ВСЕ ЗАПИСИ АУДИТА =========="
    )

    all_logs = audit_log.get_all_logs()

    for log in all_logs:

        print(
            f"{log['timestamp']} | "
            f"{log['level']} | "
            f"{log['message']} | "
            f"{log['transaction_id']}"
        )

    # ========================================================
    # 15. ИТОГОВАЯ ПРОВЕРКА
    # ========================================================

    print(
        "\n========== ИТОГОВАЯ ПРОВЕРКА =========="
    )

    print(
        "Количество транзакций:",
        len(transactions)
    )

    print(
        "Количество записей аудита:",
        len(audit_log.logs)
    )

    print(
        "Количество ERROR:",
        len(audit_log.filter_by_level("ERROR"))
    )

    print(
        "Количество WARNING:",
        len(audit_log.filter_by_level("WARNING"))
    )

    print(
        "Количество INFO:",
        len(audit_log.filter_by_level("INFO"))
    )

    blocked_transactions = [
        transaction
        for transaction in transactions
        if transaction.status == "blocked"
    ]

    print(
        "Заблокировано операций:",
        len(blocked_transactions)
    )

    print(
        "\nГотово."
    )

    print(
        "Логи сохранены в файл audit.log"
    )