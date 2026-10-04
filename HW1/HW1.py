import uuid
from abc import ABC, abstractmethod
from datetime import datetime


# ============================================================
# ИСКЛЮЧЕНИЯ
# ============================================================

class AccountFrozenError(Exception):
    pass


class AccountClosedError(Exception):
    pass


class InvalidOperationError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


# ============================================================
# ПРОВЕРКА ВРЕМЕНИ ФИНАНСОВЫХ ОПЕРАЦИЙ
# ============================================================

def check_operation_time():
    """
    Финансовые операции запрещены
    с 00:00 до 05:00.
    """

    current_hour = datetime.now().hour

    if 0 <= current_hour < 5:
        raise InvalidOperationError(
            "Финансовые операции запрещены "
            "с 00:00 до 05:00"
        )

    return True


# ============================================================
# ABSTRACT ACCOUNT
# ============================================================

class AbstractAccount(ABC):

    def __init__(
        self,
        account_id,
        owner,
        balance,
        status
    ):
        self.account_id = account_id
        self.owner = owner
        self._balance = balance
        self.status = status

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def get_account_info(self):
        pass


# ============================================================
# BANK ACCOUNT
# ============================================================

class BankAccount(AbstractAccount):

    def __init__(
        self,
        owner,
        balance,
        status,
        currency,
        account_id=None
    ):

        # ----------------------------------------------------
        # Проверка владельца
        # ----------------------------------------------------

        if not owner:
            raise InvalidOperationError(
                "Владелец не может быть пустым"
            )

        # ----------------------------------------------------
        # Проверка валюты
        # ----------------------------------------------------

        allowed_currencies = [
            "RUB",
            "USD",
            "EUR",
            "KZT",
            "CNY"
        ]

        if currency not in allowed_currencies:
            raise InvalidOperationError(
                "Недопустимая валюта"
            )

        # ----------------------------------------------------
        # Проверка статуса
        # ----------------------------------------------------

        allowed_statuses = [
            "active",
            "frozen",
            "closed"
        ]

        if status not in allowed_statuses:
            raise InvalidOperationError(
                "Недопустимый статус"
            )

        # ----------------------------------------------------
        # Создание ID
        # ----------------------------------------------------

        if account_id is None:
            account_id = str(uuid.uuid4())[:8]

        # ----------------------------------------------------
        # Проверка баланса
        # ----------------------------------------------------

        if (
            not isinstance(balance, (int, float))
            or isinstance(balance, bool)
            or balance < 0
        ):
            raise InvalidOperationError(
                "Баланс должен быть неотрицательным числом"
            )

        # ----------------------------------------------------
        # Инициализация родительского класса
        # ----------------------------------------------------

        super().__init__(
            account_id,
            owner,
            balance,
            status
        )

        self.currency = currency

    # ========================================================
    # ПРОВЕРКА СТАТУСА
    # ========================================================

    def _check_status(self):

        if self.status == "frozen":
            raise AccountFrozenError(
                "Аккаунт заморожен"
            )

        if self.status == "closed":
            raise AccountClosedError(
                "Аккаунт закрыт"
            )

    # ========================================================
    # ПОПОЛНЕНИЕ
    # ========================================================

    def deposit(self, amount):

        # Сначала проверяем, что счет доступен
        self._check_status()

        # Затем проверяем время операции
        check_operation_time()

        # Проверяем сумму
        if (
            not isinstance(amount, (int, float))
            or isinstance(amount, bool)
            or amount <= 0
        ):
            raise InvalidOperationError(
                "Сумма должна быть положительным числом"
            )

        # Только после всех проверок меняем баланс
        self._balance += amount

        return True

    # ========================================================
    # СНЯТИЕ
    # ========================================================

    def withdraw(self, amount):

        # Сначала проверяем, что счет доступен
        self._check_status()

        # Затем проверяем время операции
        check_operation_time()

        # Проверяем сумму
        if (
            not isinstance(amount, (int, float))
            or isinstance(amount, bool)
            or amount <= 0
        ):
            raise InvalidOperationError(
                "Сумма должна быть положительным числом"
            )

        # Проверяем наличие средств
        if amount > self._balance:
            raise InsufficientFundsError(
                "Недостаточно средств"
            )

        # Только после всех проверок меняем баланс
        self._balance -= amount

        return True

    # ========================================================
    # ИНФОРМАЦИЯ О СЧЕТЕ
    # ========================================================

    def get_account_info(self):
        return (
            f"{self.account_id}, "
            f"{self.owner}, "
            f"{self._balance}, "
            f"{self.status}, "
            f"{self.currency}"
        )

    # ========================================================
    # СТРОКОВОЕ ПРЕДСТАВЛЕНИЕ
    # ========================================================

    def __str__(self):
        return (
            f"BankAccount, "
            f"{self.owner}, "
            f"{self.account_id[-4:]}, "
            f"{self.status}, "
            f"{self._balance}, "
            f"{self.currency}"
        )

    # ========================================================
    # BALANCE
    # ========================================================

    @property
    def balance(self):
        return self._balance


# ============================================================
# ДЕМОНСТРАЦИЯ
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ HW1")
    print("=" * 60)

    # --------------------------------------------------------
    # Создаем активный счет
    # --------------------------------------------------------

    account1 = BankAccount(
        owner="Наиля",
        balance=10000,
        status="active",
        currency="RUB"
    )

    # --------------------------------------------------------
    # Создаем замороженный счет
    # --------------------------------------------------------

    account2 = BankAccount(
        owner="Наиля",
        balance=5000,
        status="frozen",
        currency="RUB"
    )

    # --------------------------------------------------------
    # Показываем счета
    # --------------------------------------------------------

    print("\nСчета:")

    print(account1)
    print(account2)

    # --------------------------------------------------------
    # Проверка замороженного счета
    # --------------------------------------------------------

    print("\nПроверка замороженного счета:")

    try:
        account2.deposit(1000)

    except AccountFrozenError as error:
        print("Ошибка:", error)

    except InvalidOperationError as error:
        print("Ошибка:", error)

    # --------------------------------------------------------
    # Проверка пополнения
    # --------------------------------------------------------

    print("\nПополнение активного счета:")

    try:
        account1.deposit(2000)

        print("Пополнение успешно")
        print(account1)

    except InvalidOperationError as error:
        print("Ошибка:", error)

    # --------------------------------------------------------
    # Проверка снятия
    # --------------------------------------------------------

    print("\nСнятие денег:")

    try:
        account1.withdraw(3000)

        print("Снятие успешно")
        print(account1)

    except InvalidOperationError as error:
        print("Ошибка:", error)

    except InsufficientFundsError as error:
        print("Ошибка:", error)

    # --------------------------------------------------------
    # Проверка недостатка средств
    # --------------------------------------------------------

    print("\nПроверка недостатка средств:")
    try:
        account1.withdraw(100000)
    except Exception as error:
        print(f"Ошибка: {error}")

    # --------------------------------------------------------
    # Проверка отрицательной суммы
    # --------------------------------------------------------

    print("\nПроверка некорректной суммы:")

    try:
        account1.deposit(-100)

    except InvalidOperationError as error:
        print("Ошибка:", error)

    # --------------------------------------------------------
    # Проверка времени
    # --------------------------------------------------------

    print("\nПроверка времени финансовых операций:")

    current_time = datetime.now().strftime("%H:%M")

    print("Текущее время:", current_time)

    try:
        check_operation_time()

        print(
            "Финансовые операции разрешены"
        )

    except InvalidOperationError as error:
        print("Ошибка:", error)

    # --------------------------------------------------------
    # Финальный баланс
    # --------------------------------------------------------

    print("\nФинальное состояние счета:")

    print(account1)

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ HW1 ЗАВЕРШЕНА")
    print("=" * 60)