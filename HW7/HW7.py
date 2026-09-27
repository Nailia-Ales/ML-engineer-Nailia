import csv
import json
import os
from collections import Counter

import matplotlib.pyplot as plt

from HW1.HW1 import BankAccount
from HW2.HW2 import PremiumAccount
from HW3.HW3 import Client, Bank
from HW4.HW4 import Transaction
from HW5.HW5 import AuditLog, RiskAnalyzer
from HW6.HW6 import (
    print_client_accounts,
    get_transaction_history,
)


# ============================================================
# REPORT BUILDER
# ============================================================

class ReportBuilder:
    """
    Класс для формирования отчётов и графиков.
    """

    def __init__(self, bank, transactions, audit_log):
        self.bank = bank
        self.transactions = transactions
        self.audit_log = audit_log

        self.reports_folder = "reports"
        self.charts_folder = os.path.join(
            self.reports_folder,
            "charts"
        )

        os.makedirs(
            self.reports_folder,
            exist_ok=True
        )

        os.makedirs(
            self.charts_folder,
            exist_ok=True
        )

    # ========================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ========================================================

    def _get_client_accounts(self, client):
        """
        Возвращает счета клиента.
        """

        accounts = []

        for account in self.bank.accounts:

            if account.account_id in client.account_ids:
                accounts.append(account)

        return accounts

    def _get_client_transactions(self, client):
        """
        Возвращает транзакции клиента.
        """

        result = []

        for transaction in self.transactions:

            if (
                transaction.sender.client_id
                == client.client_id
                or
                transaction.receiver.client_id
                == client.client_id
            ):
                result.append(transaction)

        return result

    def _get_total_balance_by_currency(self):
        """
        Считает общий баланс банка
        отдельно по валютам.
        """

        balances = {}

        for account in self.bank.accounts:

            currency = account.currency

            if currency not in balances:
                balances[currency] = 0

            balances[currency] += account.balance

        return balances

    def _get_transaction_statistics(self):
        """
        Возвращает статистику транзакций.
        """

        statistics = Counter()

        for transaction in self.transactions:
            statistics[transaction.status] += 1

        return dict(statistics)

    def _get_risk_statistics(self):
        """
        Возвращает статистику по уровням риска.
        """

        statistics = Counter()

        for transaction in self.transactions:

            risk_level = getattr(
                transaction,
                "risk_level",
                None
            )

            if risk_level is not None:
                statistics[risk_level] += 1

        return dict(statistics)

    # ========================================================
    # ТЕКСТОВЫЙ ОТЧЁТ ПО КЛИЕНТУ
    # ========================================================

    def build_client_report(self, client):
        """
        Формирует текстовый отчёт по клиенту.
        """

        accounts = self._get_client_accounts(
            client
        )

        transactions = self._get_client_transactions(
            client
        )

        report_lines = []

        report_lines.append(
            "=========================================="
        )

        report_lines.append(
            "ОТЧЁТ ПО КЛИЕНТУ"
        )

        report_lines.append(
            "=========================================="
        )

        report_lines.append(
            f"ФИО: {client.full_name}"
        )

        report_lines.append(
            f"ID клиента: {client.client_id}"
        )

        report_lines.append(
            f"Возраст: {client.age}"
        )

        report_lines.append(
            f"Статус: {client.status}"
        )

        report_lines.append(
            f"Контакты: {client.contacts}"
        )

        report_lines.append(
            f"Количество счетов: {len(accounts)}"
        )

        report_lines.append("")

        report_lines.append(
            "СЧЕТА:"
        )

        for account in accounts:

            report_lines.append(
                f"- {account.account_id} | "
                f"{account.balance} "
                f"{account.currency} | "
                f"статус: {account.status}"
            )

        report_lines.append("")

        report_lines.append(
            f"Количество транзакций: "
            f"{len(transactions)}"
        )

        report_lines.append("")

        report_lines.append(
            "ТРАНЗАКЦИИ:"
        )

        for transaction in transactions:

            risk_level = getattr(
                transaction,
                "risk_level",
                "не анализировался"
            )

            report_lines.append(
                f"- {transaction.transaction_id} | "
                f"{transaction.amount} "
                f"{transaction.currency} | "
                f"{transaction.status} | "
                f"риск: {risk_level}"
            )

        return "\n".join(
            report_lines
        )

    # ========================================================
    # ТЕКСТОВЫЙ ОТЧЁТ ПО БАНКУ
    # ========================================================

    def build_bank_report(self):
        """
        Формирует текстовый отчёт по банку.
        """

        total_balance = (
            self._get_total_balance_by_currency()
        )

        transaction_statistics = (
            self._get_transaction_statistics()
        )

        report_lines = []

        report_lines.append(
            "=========================================="
        )

        report_lines.append(
            "ОТЧЁТ ПО БАНКУ"
        )

        report_lines.append(
            "=========================================="
        )

        report_lines.append(
            f"Название банка: {self.bank.name}"
        )

        report_lines.append(
            f"Количество клиентов: "
            f"{len(self.bank.clients)}"
        )

        report_lines.append(
            f"Количество счетов: "
            f"{len(self.bank.accounts)}"
        )

        report_lines.append(
            f"Количество транзакций: "
            f"{len(self.transactions)}"
        )

        report_lines.append("")

        report_lines.append(
            "ОБЩИЙ БАЛАНС:"
        )

        for currency, balance in (
            total_balance.items()
        ):

            report_lines.append(
                f"- {currency}: {balance}"
            )

        report_lines.append("")

        report_lines.append(
            "СТАТИСТИКА ТРАНЗАКЦИЙ:"
        )

        for status, count in (
            transaction_statistics.items()
        ):

            report_lines.append(
                f"- {status}: {count}"
            )

        report_lines.append("")

        report_lines.append(
            "КЛИЕНТЫ:"
        )

        for client in self.bank.clients:

            report_lines.append(
                f"- {client.full_name} | "
                f"ID: {client.client_id} | "
                f"счетов: {len(client.account_ids)}"
            )

        return "\n".join(
            report_lines
        )

    # ========================================================
    # ТЕКСТОВЫЙ ОТЧЁТ ПО РИСКАМ
    # ========================================================

    def build_risk_report(self):
        """
        Формирует текстовый отчёт по рискам.
        """

        risk_statistics = (
            self._get_risk_statistics()
        )

        report_lines = []

        report_lines.append(
            "=========================================="
        )

        report_lines.append(
            "ОТЧЁТ ПО РИСКАМ"
        )

        report_lines.append(
            "=========================================="
        )

        report_lines.append("")

        report_lines.append(
            "СТАТИСТИКА ПО УРОВНЯМ РИСКА:"
        )

        for risk_level in [
            "низкий",
            "средний",
            "высокий"
        ]:

            report_lines.append(
                f"- {risk_level}: "
                f"{risk_statistics.get(risk_level, 0)}"
            )

        report_lines.append("")

        report_lines.append(
            "ПОДОЗРИТЕЛЬНЫЕ ОПЕРАЦИИ:"
        )

        suspicious_found = False

        for transaction in self.transactions:

            risk_level = getattr(
                transaction,
                "risk_level",
                None
            )

            if risk_level in (
                "средний",
                "высокий"
            ):

                suspicious_found = True

                report_lines.append(
                    f"- ID: {transaction.transaction_id} | "
                    f"сумма: {transaction.amount} "
                    f"{transaction.currency} | "
                    f"риск: {risk_level} | "
                    f"статус: {transaction.status}"
                )

        if not suspicious_found:

            report_lines.append(
                "- Подозрительных операций нет."
            )

        return "\n".join(
            report_lines
        )

    # ========================================================
    # JSON ОТЧЁТ
    # ========================================================

    def build_json_data(self):
        """
        Формирует все данные в виде словаря
        для последующего сохранения в JSON.
        """

        clients_data = []

        for client in self.bank.clients:

            accounts_data = []

            for account in (
                self._get_client_accounts(client)
            ):

                accounts_data.append(
                    {
                        "account_id":
                            account.account_id,
                        "balance":
                            account.balance,
                        "currency":
                            account.currency,
                        "status":
                            account.status
                    }
                )

            clients_data.append(
                {
                    "client_id":
                        client.client_id,
                    "full_name":
                        client.full_name,
                    "age":
                        client.age,
                    "status":
                        client.status,
                    "contacts":
                        client.contacts,
                    "accounts":
                        accounts_data
                }
            )

        transactions_data = []

        for transaction in self.transactions:

            transactions_data.append(
                {
                    "transaction_id":
                        transaction.transaction_id,
                    "transaction_type":
                        transaction.transaction_type,
                    "amount":
                        transaction.amount,
                    "currency":
                        transaction.currency,
                    "sender_client_id":
                        transaction.sender.client_id,
                    "receiver_client_id":
                        transaction.receiver.client_id,
                    "commission":
                        transaction.commission,
                    "priority":
                        transaction.priority,
                    "status":
                        transaction.status,
                    "risk_level":
                        getattr(
                            transaction,
                            "risk_level",
                            None
                        ),
                    "failure_reason":
                        transaction.failure_reason
                }
            )

        return {
            "bank": {
                "name": self.bank.name,
                "clients_count":
                    len(self.bank.clients),
                "accounts_count":
                    len(self.bank.accounts),
                "transactions_count":
                    len(self.transactions)
            },

            "balances":
                self._get_total_balance_by_currency(),

            "transaction_statistics":
                self._get_transaction_statistics(),

            "risk_statistics":
                self._get_risk_statistics(),

            "clients":
                clients_data,

            "transactions":
                transactions_data
        }

    # ========================================================
    # EXPORT JSON
    # ========================================================

    def export_to_json(
        self,
        file_name="bank_report.json"
    ):
        """
        Сохраняет отчёт в JSON.
        """

        file_path = os.path.join(
            self.reports_folder,
            file_name
        )

        data = self.build_json_data()

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

        return file_path

    # ========================================================
    # EXPORT CSV
    # ========================================================

    def export_to_csv(
        self,
        file_name="transactions_report.csv"
    ):
        """
        Сохраняет транзакции в CSV.
        """

        file_path = os.path.join(
            self.reports_folder,
            file_name
        )

        with open(
            file_path,
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow(
                [
                    "transaction_id",
                    "transaction_type",
                    "amount",
                    "currency",
                    "sender_client_id",
                    "receiver_client_id",
                    "commission",
                    "priority",
                    "status",
                    "risk_level",
                    "failure_reason"
                ]
            )

            for transaction in self.transactions:

                writer.writerow(
                    [
                        transaction.transaction_id,
                        transaction.transaction_type,
                        transaction.amount,
                        transaction.currency,
                        transaction.sender.client_id,
                        transaction.receiver.client_id,
                        transaction.commission,
                        transaction.priority,
                        transaction.status,
                        getattr(
                            transaction,
                            "risk_level",
                            None
                        ),
                        transaction.failure_reason
                    ]
                )

        return file_path

    # ========================================================
    # КРУГОВАЯ ДИАГРАММА
    # ========================================================

    def create_risk_pie_chart(self):
        """
        Создаёт круговую диаграмму
        распределения транзакций по риску.
        """

        risk_statistics = (
            self._get_risk_statistics()
        )

        labels = [
            "Низкий",
            "Средний",
            "Высокий"
        ]

        values = [
            risk_statistics.get(
                "низкий",
                0
            ),

            risk_statistics.get(
                "средний",
                0
            ),

            risk_statistics.get(
                "высокий",
                0
            )
        ]

        # Если данных нет, график не строим.
        if sum(values) == 0:
            return None

        plt.figure(
            figsize=(8, 6)
        )

        plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )

        plt.title(
            "Распределение транзакций по уровню риска"
        )

        plt.tight_layout()

        file_path = os.path.join(
            self.charts_folder,
            "risk_pie_chart.png"
        )

        plt.savefig(
            file_path,
            dpi=150
        )

        plt.close()

        return file_path

    # ========================================================
    # СТОЛБЧАТАЯ ДИАГРАММА
    # ========================================================

    def create_status_bar_chart(self):
        """
        Создаёт столбчатую диаграмму
        по статусам транзакций.
        """

        statistics = (
            self._get_transaction_statistics()
        )

        statuses = [
            "completed",
            "failed",
            "blocked",
            "cancelled",
            "pending"
        ]

        values = [
            statistics.get(
                status,
                0
            )
            for status in statuses
        ]

        plt.figure(
            figsize=(9, 6)
        )

        plt.bar(
            statuses,
            values
        )

        plt.title(
            "Количество транзакций по статусам"
        )

        plt.xlabel(
            "Статус"
        )

        plt.ylabel(
            "Количество"
        )

        plt.xticks(
            rotation=20
        )

        plt.tight_layout()

        file_path = os.path.join(
            self.charts_folder,
            "transaction_status_bar_chart.png"
        )

        plt.savefig(
            file_path,
            dpi=150
        )

        plt.close()

        return file_path

    # ========================================================
    # ГРАФИК ДВИЖЕНИЯ БАЛАНСА
    # ========================================================

    def create_balance_movement_chart(
        self,
        account
    ):
        """
        Показывает изменение баланса выбранного счёта
        после каждой операции.
        """

        current_balance = account.balance

        balance_values = [
            current_balance
        ]

        operation_numbers = [
            0
        ]

        balance = current_balance

        # Идём по транзакциям в обратном направлении,
        # чтобы восстановить приблизительную историю
        # изменения баланса.

        relevant_transactions = []

        for transaction in self.transactions:

            if (
                transaction.status != "completed"
            ):
                continue

            if (
                transaction.sender.account_id
                == account.account_id
                or
                transaction.receiver.account_id
                == account.account_id
            ):
                relevant_transactions.append(
                    transaction
                )

        # Восстанавливаем баланс назад.
        historical_balances = [
            balance
        ]

        for transaction in reversed(
            relevant_transactions
        ):

            if (
                transaction.receiver.account_id
                == account.account_id
            ):

                balance -= transaction.amount

            elif (
                transaction.sender.account_id
                == account.account_id
            ):

                balance += (
                    transaction.amount
                    + transaction.commission
                )

            historical_balances.append(
                balance
            )

        historical_balances.reverse()

        operation_numbers = list(
            range(
                len(historical_balances)
            )
        )

        plt.figure(
            figsize=(10, 6)
        )

        plt.plot(
            operation_numbers,
            historical_balances,
            marker="o"
        )

        plt.title(
            f"Движение баланса счёта "
            f"{account.account_id}"
        )

        plt.xlabel(
            "Номер операции"
        )

        plt.ylabel(
            f"Баланс, {account.currency}"
        )

        plt.grid(
            True
        )

        plt.tight_layout()

        file_path = os.path.join(
            self.charts_folder,
            "balance_movement_chart.png"
        )

        plt.savefig(
            file_path,
            dpi=150
        )

        plt.close()

        return file_path

    # ========================================================
    # СОХРАНЕНИЕ ВСЕХ ГРАФИКОВ
    # ========================================================

    def save_charts(self):
        """
        Создаёт и сохраняет все необходимые графики.
        """

        saved_charts = []

        risk_chart = (
            self.create_risk_pie_chart()
        )

        if risk_chart is not None:
            saved_charts.append(
                risk_chart
            )

        status_chart = (
            self.create_status_bar_chart()
        )

        if status_chart is not None:
            saved_charts.append(
                status_chart
            )

        if self.bank.accounts:

            balance_chart = (
                self.create_balance_movement_chart(
                    self.bank.accounts[0]
                )
            )

            if balance_chart is not None:
                saved_charts.append(
                    balance_chart
                )

        return saved_charts


# ============================================================
# СОЗДАНИЕ ДЕМОНСТРАЦИОННЫХ ДАННЫХ
# ============================================================

def create_demo_data():
    """
    Создаёт банк, клиентов, счета и транзакции
    для тестирования HW7.
    """

    bank = Bank(
        "Demo Bank"
    )

    audit_log = AuditLog(
        "audit_day7.log"
    )

    # ========================================================
    # КЛИЕНТЫ
    # ========================================================

    clients = [
        Client(
            "Иван Иванов",
            "001",
            30,
            "active",
            "ivan@mail.ru",
            "1111"
        ),

        Client(
            "Анна Петрова",
            "002",
            28,
            "active",
            "anna@mail.ru",
            "2222"
        ),

        Client(
            "Пётр Сидоров",
            "003",
            35,
            "active",
            "petr@mail.ru",
            "3333"
        ),

        Client(
            "Мария Смирнова",
            "004",
            31,
            "active",
            "maria@mail.ru",
            "4444"
        ),

        Client(
            "Алексей Кузнецов",
            "005",
            40,
            "active",
            "alex@mail.ru",
            "5555"
        ),

        Client(
            "Елена Попова",
            "006",
            27,
            "active",
            "elena@mail.ru",
            "6666"
        )
    ]

    for client in clients:
        bank.add_client(
            client
        )

    # ========================================================
    # СЧЕТА
    # ========================================================

    account1 = BankAccount(
        "Иван Иванов",
        500000,
        "active",
        "RUB"
    )

    account2 = BankAccount(
        "Анна Петрова",
        300000,
        "active",
        "RUB"
    )

    account3 = BankAccount(
        "Пётр Сидоров",
        250000,
        "active",
        "RUB"
    )

    account4 = BankAccount(
        "Мария Смирнова",
        180000,
        "active",
        "RUB"
    )

    account5 = BankAccount(
        "Алексей Кузнецов",
        450000,
        "active",
        "RUB"
    )

    account6 = PremiumAccount(
        "Елена Попова",
        50000,
        "active",
        "RUB",
        30000,
        100
    )

    accounts = [
        account1,
        account2,
        account3,
        account4,
        account5,
        account6
    ]

    # ========================================================
    # ПРИВЯЗЫВАЕМ СЧЕТА К КЛИЕНТАМ
    # ========================================================

    for client, account in zip(
        clients,
        accounts
    ):

        bank.open_account(
            client,
            account
        )

    # ========================================================
    # СОЗДАЁМ ТРАНЗАКЦИИ
    # ========================================================

    transactions = [
        Transaction(
            "internal",
            5000,
            "RUB",
            account1,
            account2
        ),

        Transaction(
            "internal",
            7000,
            "RUB",
            account2,
            account3
        ),

        Transaction(
            "internal",
            10000,
            "RUB",
            account3,
            account4
        ),

        Transaction(
            "external",
            150000,
            "RUB",
            account1,
            account3
        ),

        Transaction(
            "external",
            200000,
            "RUB",
            account5,
            account1
        ),

        Transaction(
            "internal",
            3000,
            "RUB",
            account4,
            account5
        ),

        Transaction(
            "internal",
            8000,
            "RUB",
            account1,
            account6
        ),

        Transaction(
            "external",
            250000,
            "RUB",
            account3,
            account5
        ),

        Transaction(
            "internal",
            4000,
            "RUB",
            account5,
            account2
        ),

        Transaction(
            "internal",
            6000,
            "RUB",
            account6,
            account1
        )
    ]

    # ========================================================
    # ЗАДАЁМ СТАТУСЫ И РИСКИ ДЛЯ ДЕМО
    # ========================================================

    risk_levels = [
        "низкий",
        "низкий",
        "средний",
        "высокий",
        "средний",
        "низкий",
        "средний",
        "высокий",
        "низкий",
        "средний"
    ]

    statuses = [
        "completed",
        "completed",
        "completed",
        "blocked",
        "completed",
        "completed",
        "completed",
        "failed",
        "completed",
        "completed"
    ]

    for transaction, risk_level, status in zip(
        transactions,
        risk_levels,
        statuses
    ):

        transaction.risk_level = risk_level
        transaction.status = status

    return (
        bank,
        clients,
        accounts,
        transactions,
        audit_log
    )


# ============================================================
# ТЕСТИРОВАНИЕ HW7
# ============================================================

if __name__ == "__main__":

    print(
        "=================================================="
    )

    print(
        "       ДЕНЬ 7 — СИСТЕМА ОТЧЁТНОСТИ"
    )

    print(
        "=================================================="
    )

    # ========================================================
    # 1. СОЗДАЁМ ДАННЫЕ
    # ========================================================

    (
        bank,
        clients,
        accounts,
        transactions,
        audit_log
    ) = create_demo_data()

    print(
        "\nБанк:",
        bank.name
    )

    print(
        "Клиентов:",
        len(clients)
    )

    print(
        "Счетов:",
        len(accounts)
    )

    print(
        "Транзакций:",
        len(transactions)
    )

    # ========================================================
    # 2. СОЗДАЁМ REPORT BUILDER
    # ========================================================

    report_builder = ReportBuilder(
        bank=bank,
        transactions=transactions,
        audit_log=audit_log
    )

    print(
        "\nReportBuilder создан."
    )

    # ========================================================
    # 3. ОТЧЁТ ПО КЛИЕНТУ
    # ========================================================

    print(
        "\n========== ОТЧЁТ ПО КЛИЕНТУ =========="
    )

    client_report = (
        report_builder.build_client_report(
            clients[0]
        )
    )

    print(
        client_report
    )

    client_report_path = os.path.join(
        "reports",
        "client_report.txt"
    )

    with open(
        client_report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            client_report
        )

    print(
        "\nТекстовый отчёт клиента сохранён:"
    )

    print(
        client_report_path
    )

    # ========================================================
    # 4. ОТЧЁТ ПО БАНКУ
    # ========================================================

    print(
        "\n========== ОТЧЁТ ПО БАНКУ =========="
    )

    bank_report = (
        report_builder.build_bank_report()
    )

    print(
        bank_report
    )

    bank_report_path = os.path.join(
        "reports",
        "bank_report.txt"
    )

    with open(
        bank_report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            bank_report
        )

    print(
        "\nТекстовый отчёт банка сохранён:"
    )

    print(
        bank_report_path
    )

    # ========================================================
    # 5. ОТЧЁТ ПО РИСКАМ
    # ========================================================

    print(
        "\n========== ОТЧЁТ ПО РИСКАМ =========="
    )

    risk_report = (
        report_builder.build_risk_report()
    )

    print(
        risk_report
    )

    risk_report_path = os.path.join(
        "reports",
        "risk_report.txt"
    )

    with open(
        risk_report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            risk_report
        )

    print(
        "\nТекстовый отчёт по рискам сохранён:"
    )

    print(
        risk_report_path
    )

    # ========================================================
    # 6. JSON
    # ========================================================

    print(
        "\n========== EXPORT JSON =========="
    )

    json_path = (
        report_builder.export_to_json()
    )

    print(
        "JSON сохранён:"
    )

    print(
        json_path
    )

    # ========================================================
    # 7. CSV
    # ========================================================

    print(
        "\n========== EXPORT CSV =========="
    )

    csv_path = (
        report_builder.export_to_csv()
    )

    print(
        "CSV сохранён:"
    )

    print(
        csv_path
    )

    # ========================================================
    # 8. ГРАФИКИ
    # ========================================================

    print(
        "\n========== СОХРАНЕНИЕ ГРАФИКОВ =========="
    )

    chart_paths = (
        report_builder.save_charts()
    )

    for chart_path in chart_paths:

        print(
            "График сохранён:"
        )

        print(
            chart_path
        )

    # ========================================================
    # 9. ПРОВЕРКА ФАЙЛОВ
    # ========================================================

    print(
        "\n========== ПРОВЕРКА =========="
    )

    files_to_check = [
        client_report_path,
        bank_report_path,
        risk_report_path,
        json_path,
        csv_path
    ]

    files_to_check.extend(
        chart_paths
    )

    for file_path in files_to_check:

        if os.path.exists(
            file_path
        ):

            print(
                f"OK: {file_path}"
            )

        else:

            print(
                f"ERROR: файл не найден "
                f"{file_path}"
            )

    print(
        "\n=================================================="
    )

    print(
        "          ДЕМОНСТРАЦИЯ HW7 ЗАВЕРШЕНА"
    )

    print(
        "=================================================="
    )