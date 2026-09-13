import uuid
from abc import ABC, abstractmethod

class AccountFrozenError(Exception):
    pass

class AccountClosedError(Exception):
    pass

class InvalidOperationError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

class AbstractAccount(ABC):
    def __init__(self, account_id, owner, balance, status):
        self.account_id = account_id
        self.owner = owner
        self._balance = balance
        self.status = status

    @abstractmethod #любой конкретный класс-наследник обязан иметь свой deposit()
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def get_account_info(self):
        pass

    # AbstractAccount — это каркас.
    # Он говорит: Любой настоящий счёт должен иметь ID, владельца, баланс, статус
    # и уметь пополняться, снимать деньги и выдавать информацию о себе.
    # Но сам AbstractAccount не знает, как именно это делать.

class BankAccount(AbstractAccount):
    def __init__(self, owner, balance, status, currency, account_id=None):
        if not owner:
            raise InvalidOperationError("Владелец не может быть пустым")
        allowed_currencies = ["RUB", "USD", "EUR", "KZT", "CNY"]
        allowed_statuses = ["active", "frozen", "closed"]
        if currency not in allowed_currencies:
            raise InvalidOperationError("Недопустимая валюта") # raise должен создать объект ошибки, а не просто ссылаться на класс, поэтому нужно указать в скобках текст
        if account_id is None:
            account_id = str(uuid.uuid4())[:8]
        if balance < 0:
            raise InvalidOperationError("Баланс не может быть отрицательным")
        if status not in allowed_statuses:
            raise InvalidOperationError("Недопустимый статус")
        super().__init__(account_id, owner, balance, status)
        self.currency = currency

    def _check_status(self):
        if self.status == "frozen":
            raise AccountFrozenError("Аккаунт заморожен")
        elif self.status == "closed":
            raise AccountClosedError("Аккаунт закрыт")

    def deposit(self, amount):
        self._check_status()
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InvalidOperationError("Сумма должна быть положительным числом")
        self._balance += amount
        return True

    def withdraw(self, amount):
        self._check_status()
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InvalidOperationError("Сумма должна быть положительным числом")
        if amount > self._balance:
            raise InsufficientFundsError("Недостаточно средств")
        self._balance -= amount
        return True

    def get_account_info(self):
        return f"{self.account_id}, {self.owner}, {self._balance}, {self.status}, {self.currency}"

    def __str__(self):
        return f"BankAccount, {self.owner}, {self.account_id[-4:]}, {self.status}, {self._balance}, {self.currency}"

    @property
    def balance(self):
        return self._balance

# Демонстрация работы
if __name__ == "__main__":
    account1 = BankAccount(
        owner="Наиля",
        balance=10000,
        status="active",
        currency="RUB"
    )

    account2 = BankAccount(
        owner="Наиля",
        balance=5000,
        status="frozen",
        currency="RUB"
    )

    # Проверка №1
    print(account1)
    print(account2)

    # Проверка №2
    try:
        account2.deposit(1000)
    except AccountFrozenError as e:
        print(e)

    # Проверка №3
    account1.deposit(2000)
    print(account1)

    # Проверка №4
    account1.withdraw(3000)
    print(account1)