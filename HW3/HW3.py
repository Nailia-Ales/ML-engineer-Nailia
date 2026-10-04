from HW1.HW1 import (
    BankAccount,
    check_operation_time,
    InvalidOperationError
)


# ============================================================
# Client
# ============================================================

class Client:

    def __init__(
        self,
        full_name,
        client_id,
        age,
        status,
        contacts,
        password
    ):
        if age < 18:
            raise ValueError(
                "Возраст должен быть 18 лет или старше"
            )

        self.full_name = full_name
        self.client_id = client_id
        self.age = age
        self.status = status
        self.contacts = contacts
        self.password = password

        self.account_ids = []

        self.failed_attempts = 0
        self.is_blocked = False
        self.suspicious_action = False

    def __str__(self):
        return (
            f"Client: {self.full_name}, "
            f"ID: {self.client_id}, "
            f"status: {self.status}"
        )


# ============================================================
# Bank
# ============================================================

class Bank:

    def __init__(self, name):
        self.name = name
        self.clients = []
        self.accounts = []

    # --------------------------------------------------------
    # Добавление клиента
    # --------------------------------------------------------

    def add_client(self, client):

        for existing_client in self.clients:

            if existing_client.client_id == client.client_id:
                raise ValueError(
                    "Клиент с таким ID уже существует"
                )

        self.clients.append(client)

    # --------------------------------------------------------
    # Поиск клиента
    # --------------------------------------------------------

    def find_client(self, client):

        for existing_client in self.clients:

            if existing_client.client_id == client.client_id:
                return existing_client

        raise ValueError("Клиент не найден")

    # --------------------------------------------------------
    # Проверка принадлежности счета клиенту
    # --------------------------------------------------------

    def check_account_belongs_to_client(
        self,
        client,
        account
    ):

        if account.account_id not in client.account_ids:
            raise ValueError(
                "Счет не принадлежит клиенту"
            )

    # --------------------------------------------------------
    # Проверка, что счет зарегистрирован в банке
    # --------------------------------------------------------

    def check_account_in_bank(self, account):

        for existing_account in self.accounts:

            if existing_account.account_id == account.account_id:
                return True

        raise ValueError(
            "Счет не зарегистрирован в банке"
        )

    # --------------------------------------------------------
    # Открытие счета
    # --------------------------------------------------------

    def open_account(self, client, account):

        client = self.find_client(client)

        for existing_account in self.accounts:

            if existing_account.account_id == account.account_id:
                raise ValueError(
                    "Счет с таким ID уже существует"
                )

        self.accounts.append(account)

        client.account_ids.append(
            account.account_id
        )

        account.client_id = client.client_id

    # --------------------------------------------------------
    # Закрытие счета
    # --------------------------------------------------------

    def close_account(self, client, account):

        client = self.find_client(client)

        self.check_account_in_bank(account)

        self.check_account_belongs_to_client(
            client,
            account
        )

        if account.status == "closed":
            raise ValueError(
                "Счет уже закрыт"
            )

        account.status = "closed"

        client.account_ids.remove(
            account.account_id
        )

    # --------------------------------------------------------
    # Заморозка счета
    # --------------------------------------------------------

    def freeze_account(self, client, account):

        client = self.find_client(client)

        self.check_account_in_bank(account)

        self.check_account_belongs_to_client(
            client,
            account
        )

        if account.status == "closed":
            raise ValueError(
                "Нельзя заморозить закрытый счет"
            )

        if account.status == "frozen":
            raise ValueError(
                "Счет уже заморожен"
            )

        account.status = "frozen"

    # --------------------------------------------------------
    # Разморозка счета
    # --------------------------------------------------------

    def unfreeze_account(self, client, account):

        client = self.find_client(client)

        self.check_account_in_bank(account)

        self.check_account_belongs_to_client(
            client,
            account
        )

        if account.status == "closed":
            raise ValueError(
                "Нельзя разморозить закрытый счет"
            )

        if account.status != "frozen":
            raise ValueError(
                "Счет не заморожен"
            )

        account.status = "active"

    # --------------------------------------------------------
    # Авторизация клиента
    # --------------------------------------------------------

    def authenticate_client(self, client, password):

        client = self.find_client(client)

        if client.is_blocked:
            raise ValueError(
                "Клиент заблокирован"
            )

        # Правильный пароль
        if client.password == password:

            client.failed_attempts = 0
            client.is_blocked = False

            print("Вход выполнен")

            return True

        # Неправильный пароль
        client.failed_attempts += 1

        # Три неправильные попытки
        if client.failed_attempts >= 3:

            client.is_blocked = True
            client.suspicious_action = True

            print(
                "Количество попыток исчерпано, "
                "доступ заблокирован"
            )

            return False

        remaining_attempts = (
            3 - client.failed_attempts
        )

        print(
            f"У вас осталось {remaining_attempts} "
            f"попытки до блокировки"
        )

        return False

    # --------------------------------------------------------
    # Поиск счетов клиента
    # --------------------------------------------------------

    def search_accounts(self, client):

        client = self.find_client(client)

        found_accounts = []

        for account in self.accounts:

            if account.account_id in client.account_ids:
                found_accounts.append(account)

        return found_accounts

    # --------------------------------------------------------
    # Общий баланс банка
    # --------------------------------------------------------

    def get_total_balance(self):

        total_balance = 0

        for account in self.accounts:

            # Закрытый счет остается в bank.accounts,
            # поэтому его баланс также учитывается.
            total_balance += account.balance

        return total_balance

    # --------------------------------------------------------
    # Рейтинг клиентов
    # --------------------------------------------------------

    def get_clients_ranking(self):

        total_ranking = []

        for client in self.clients:

            client_balance = 0

            for account in self.accounts:

                if account.account_id in client.account_ids:
                    client_balance += account.balance

            total_ranking.append(
                (client, client_balance)
            )

        total_ranking.sort(
            key=lambda item: item[1],
            reverse=True
        )

        return total_ranking


# ============================================================
# ТЕСТИРОВАНИЕ ДЗ 3
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ДЗ 3 — БАНК И КЛИЕНТЫ")
    print("=" * 60)

    # ========================================================
    # 1. Создаем банк
    # ========================================================

    bank = Bank("Sber")

    print("\nБанк создан:")
    print(bank.name)

    # ========================================================
    # 2. Создаем клиентов
    # ========================================================

    client1 = Client(
        "Иван Иванов",
        "001",
        25,
        "active",
        "ivan@mail.ru",
        "1234"
    )

    client2 = Client(
        "Анна Петрова",
        "002",
        30,
        "active",
        "anna@mail.ru",
        "5678"
    )

    # ========================================================
    # 3. Добавляем клиентов
    # ========================================================

    bank.add_client(client1)
    bank.add_client(client2)

    print("\nКлиенты банка:")

    for client in bank.clients:

        print(
            client.full_name,
            "| ID:",
            client.client_id
        )

    # ========================================================
    # 4. Создаем счета
    # ========================================================

    account1 = BankAccount(
        owner="Иван Иванов",
        balance=100000,
        status="active",
        currency="RUB"
    )

    account2 = BankAccount(
        owner="Иван Иванов",
        balance=50000,
        status="active",
        currency="RUB"
    )

    account3 = BankAccount(
        owner="Анна Петрова",
        balance=200000,
        status="active",
        currency="RUB"
    )

    # ========================================================
    # 5. Открываем счета
    # ========================================================

    print("\nОткрытие счетов:")

    try:

        bank.open_account(
            client1,
            account1
        )

        print("Счет Ивана №1 открыт")

        bank.open_account(
            client1,
            account2
        )

        print("Счет Ивана №2 открыт")

        bank.open_account(
            client2,
            account3
        )

        print("Счет Анны открыт")

    except (
        ValueError,
        InvalidOperationError
    ) as error:

        print("Ошибка:", error)

    # ========================================================
    # 6. Показываем счета
    # ========================================================

    print("\nВсе счета банка:")

    for account in bank.accounts:

        print(account)

    # ========================================================
    # 7. Счета Ивана
    # ========================================================

    print("\nСчета Ивана:")

    for account in bank.search_accounts(client1):

        print(account)

    # ========================================================
    # 8. Счета Анны
    # ========================================================

    print("\nСчета Анны:")

    for account in bank.search_accounts(client2):

        print(account)

    # ========================================================
    # 9. Общий баланс
    # ========================================================

    print("\nОбщий баланс банка:")

    print(
        bank.get_total_balance(),
        "RUB"
    )

    # ========================================================
    # 10. Заморозка счета
    # ========================================================

    print("\nЗаморозка счета Ивана:")

    try:

        bank.freeze_account(
            client1,
            account1
        )

        print(account1)

    except (
        ValueError,
        InvalidOperationError
    ) as error:

        print("Ошибка:", error)

    # ========================================================
    # 11. Разморозка счета
    # ========================================================

    print("\nРазморозка счета Ивана:")

    try:

        bank.unfreeze_account(
            client1,
            account1
        )

        print(account1)

    except (
        ValueError,
        InvalidOperationError
    ) as error:

        print("Ошибка:", error)

    # ========================================================
    # 12. Закрытие второго счета Ивана
    # ========================================================

    print("\nЗакрытие второго счета Ивана:")

    try:

        bank.close_account(
            client1,
            account2
        )

        print(account2)

    except (
        ValueError,
        InvalidOperationError
    ) as error:

        print("Ошибка:", error)

    # ========================================================
    # 13. Счета Ивана после закрытия
    # ========================================================

    print("\nАктивные счета Ивана после закрытия:")

    for account in bank.search_accounts(client1):

        print(account)

    # ========================================================
    # 14. Правильный пароль
    # ========================================================

    print("\nАвторизация Ивана:")

    bank.authenticate_client(
        client1,
        "1234"
    )

    # ========================================================
    # 15. Неправильный пароль
    # ========================================================

    print("\nНеправильный пароль Анны:")

    bank.authenticate_client(
        client2,
        "wrong"
    )

    # ========================================================
    # 16. Три неправильные попытки
    # ========================================================

    print("\nПроверка блокировки Анны:")

    bank.authenticate_client(
        client2,
        "wrong"
    )

    bank.authenticate_client(
        client2,
        "wrong"
    )

    # ========================================================
    # 17. Проверяем блокировку
    # ========================================================

    print("\nСтатус Анны:")

    print(
        "Заблокирована:",
        client2.is_blocked
    )

    print(
        "Подозрительное действие:",
        client2.suspicious_action
    )

    print(
        "Неудачных попыток:",
        client2.failed_attempts
    )

    # ========================================================
    # 18. Рейтинг клиентов
    # ========================================================

    print("\nРейтинг клиентов:")

    ranking = bank.get_clients_ranking()

    for number, (client, balance) in enumerate(
        ranking,
        start=1
    ):

        print(
            f"{number}. "
            f"{client.full_name} — "
            f"{balance} RUB"
        )

    # ========================================================
    # 19. Финальный вывод
    # ========================================================

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ДЗ 3 ЗАВЕРШЕНА")
    print("=" * 60)