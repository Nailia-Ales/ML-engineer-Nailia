from HW1.HW1 import BankAccount
from datetime import datetime, time

class Client:
    def __init__(self, full_name, client_id, age, status, contacts, password):
        if age < 18:
            raise ValueError("Возраст должен быть 18 лет или старше")
        self.full_name = full_name
        self.client_id = client_id
        self.age = age
        self.status = status
        self.account_ids = []
        self.contacts = contacts
        self.password = password
        self.failed_attempts = 0
        self.is_blocked = False
        self.suspicious_action = False


class Bank:
    def __init__(self, name):
        self.name = name
        self.clients = []
        self.accounts = []

    def add_client(self, client):
        for existing_client in self.clients:
            if existing_client.client_id == client.client_id:
                raise ValueError("Клиент с таким ID уже существует")
        self.clients.append(client)

    def open_account(self, client, account):
        self.check_operation_time()
        for existing_client in self.clients:
            if existing_client.client_id == client.client_id:
                break
        else:
            raise ValueError("Клиент не найден")
        self.accounts.append(account)
        client.account_ids.append(account.account_id)
        account.client_id = client.client_id

    def close_account(self, client, account):
        self.check_operation_time()
        for existing_client in self.clients:
            if existing_client.client_id == client.client_id:
                if account.account_id not in existing_client.account_ids:
                    raise ValueError("Счет не принадлежит клиенту")
                break
        else:
            raise ValueError("Клиент не найден")
        account.status = "closed"
        client.account_ids.remove(account.account_id)

    def freeze_account(self, client, account):
        self.check_operation_time()
        for existing_client in self.clients:
            if existing_client.client_id == client.client_id:
                if account.account_id not in existing_client.account_ids:
                    raise ValueError("Счет не принадлежит клиенту")
                break
        else:
            raise ValueError("Клиент не найден")
        account.status = "frozen"

    def unfreeze_account(self, client, account):
        self.check_operation_time()
        for existing_client in self.clients:
            if existing_client.client_id == client.client_id:
                if account.account_id not in existing_client.account_ids:
                    raise ValueError("Счет не принадлежит клиенту")
                break
        else:
            raise ValueError("Клиент не найден")
        account.status = "active"

    def authenticate_client(self, client, password):
        for existing_client in self.clients:
            if existing_client.client_id == client.client_id:
                if existing_client.is_blocked:
                    raise ValueError("Клиент заблокирован")
                if existing_client.password == password:
                    existing_client.failed_attempts = 0
                    existing_client.is_blocked = False
                    print("Вход выполнен")
                else:
                    existing_client.failed_attempts += 1
                    if existing_client.failed_attempts >= 3:
                        existing_client.is_blocked = True
                        existing_client.suspicious_action = True
                        print(
                            "Количество попыток исчерпано, "
                            "доступ заблокирован"
                        )
                    else:
                        remaining_attempts = (
                            3 - existing_client.failed_attempts
                        )
                        print(
                            f"У вас осталось {remaining_attempts} "
                            f"попытки до блокировки"
                        )

                break
        else:
            raise ValueError("Клиент не найден")

    def search_accounts(self, client):
        found_accounts = []
        for existing_client in self.clients:
            if existing_client.client_id == client.client_id:
                for account in self.accounts:
                    if account.account_id in existing_client.account_ids:
                        found_accounts.append(account)
                if not found_accounts:
                    print("Счет не найден")
                return found_accounts
        else:
            raise ValueError("Клиент не найден")

    def check_operation_time(self):
        current_time = datetime.now().time()
        if time(0, 0) <= current_time < time(5, 0):
            raise ValueError(
                "Операции недоступны с 00:00 до 05:00"
            )

    def get_total_balance(self):
        total_balance = 0
        for account in self.accounts:
            total_balance += account.balance
        return total_balance

    def get_clients_ranking(self):
        total_ranking = []
        for existing_client in self.clients:
            client_balance = 0
            for account in self.accounts:
                if account.account_id in existing_client.account_ids:
                    client_balance += account.balance

            total_ranking.append(
                (existing_client, client_balance)
            )

        total_ranking.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return total_ranking


# ТЕСТЫ К ДЗ 3

if __name__ == "__main__":

    # =========================
    # 1. Создаем банк
    # =========================

    bank = Bank("Sber")


    # =========================
    # 2. Создаем клиентов
    # =========================

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


    # =========================
    # 3. Добавляем клиентов
    # =========================

    bank.add_client(client1)
    bank.add_client(client2)

    print("Клиенты банка:")

    for client in bank.clients:
        print(client.full_name, client.client_id)


    # =========================
    # 4. Создаем счета
    # =========================

    account1 = BankAccount(
        "Иван Иванов",
        100000,
        "active",
        "RUB"
    )

    account2 = BankAccount(
        "Иван Иванов",
        50000,
        "active",
        "RUB"
    )

    account3 = BankAccount(
        "Анна Петрова",
        200000,
        "active",
        "RUB"
    )


    # =========================
    # 5. Открываем счета
    # =========================

    bank.open_account(client1, account1)
    bank.open_account(client1, account2)
    bank.open_account(client2, account3)

    print("\nСчета:")

    for account in bank.accounts:
        print(account)


    # =========================
    # 6. Счета конкретных клиентов
    # =========================

    print("\nСчета Ивана:")

    for account in bank.search_accounts(client1):
        print(account)

    print("\nСчета Анны:")

    for account in bank.search_accounts(client2):
        print(account)


    # =========================
    # 7. Общий баланс
    # =========================

    print("\nОбщий баланс:")
    print(bank.get_total_balance())


    # =========================
    # 8. Заморозка счета
    # =========================

    bank.freeze_account(client1, account1)

    print("\nПосле заморозки:")
    print(account1)


    # =========================
    # 9. Разморозка счета
    # =========================

    bank.unfreeze_account(client1, account1)

    print("\nПосле разморозки:")
    print(account1)


    # =========================
    # 10. Закрытие счета
    # =========================

    bank.close_account(client1, account2)

    print("\nПосле закрытия второго счета Ивана:")
    print(account2)

    print("\nСчета Ивана после закрытия:")

    for account in bank.search_accounts(client1):
        print(account)


    # =========================
    # 11. Правильный пароль
    # =========================

    print("\nАвторизация Ивана:")
    bank.authenticate_client(client1, "1234")


    # =========================
    # 12. Неправильный пароль
    # =========================

    print("\nНеправильный пароль:")
    bank.authenticate_client(client2, "wrong")


    # =========================
    # 13. Три неправильные попытки
    # =========================

    print("\nПроверка блокировки:")

    bank.authenticate_client(client2, "wrong")
    bank.authenticate_client(client2, "wrong")


    # =========================
    # 14. Проверяем блокировку
    # =========================

    print("\nСтатус Анны:")
    print("Заблокирован:", client2.is_blocked)
    print("Подозрительное действие:", client2.suspicious_action)


    # =========================
    # 15. Рейтинг клиентов
    # =========================

    print("\nРейтинг клиентов:")

    ranking = bank.get_clients_ranking()

    for client, balance in ranking:
        print(client.full_name, balance)