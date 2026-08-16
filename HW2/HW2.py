from HW1.HW1 import BankAccount, InvalidOperationError, InsufficientFundsError


class SavingsAccount(BankAccount):
    def __init__(self, owner, balance, status, currency, min_balance, monthly_rate, account_id=None):
        super().__init__(owner, balance, status, currency, account_id)
        self.min_balance = min_balance
        self.monthly_rate = monthly_rate
        if not isinstance(min_balance, (int, float)) or min_balance < 0:
            raise InvalidOperationError("Минимальный баланс должен быть неотрицательным числом")
        if not isinstance(monthly_rate, (int, float)) or monthly_rate < 0:
            raise InvalidOperationError("Ставка должна быть неотрицательным числом")

    def withdraw(self, amount):
        self._check_status()
        if amount <= 0:
            raise InvalidOperationError()
        if self._balance - amount < self.min_balance:
            raise InsufficientFundsError("Нельзя снять сумму, оставив баланс ниже минимального")
        self._balance -= amount
        return True

    def apply_monthly_interest(self):
        self._check_status()
        interest = self._balance * self.monthly_rate
        self._balance += interest
        return True

    def get_account_info(self):
        return f"{self.account_id}, {self.owner}, {self._balance}, {self.status}, {self.currency}, {self.min_balance}, {self.monthly_rate}"

    def __str__(self):
        return f"SavingsAccount, {self.owner}, {self.account_id[-4:]}, {self.status}, {self._balance}, {self.currency}, {self.min_balance}, {self.monthly_rate}"


class PremiumAccount(BankAccount):
    def __init__(self, owner, balance, status, currency, overdraft_limit, commission, account_id=None):
        super().__init__(owner, balance, status, currency, account_id)
        self.overdraft_limit = overdraft_limit
        self.commission = commission
        if not isinstance(overdraft_limit, (int, float)) or overdraft_limit < 0:
            raise InvalidOperationError("Лимит овердрафта должен быть неотрицательным числом")
        if not isinstance(commission, (int, float)) or commission < 0:
            raise InvalidOperationError("Комиссия должна быть неотрицательным числом")

    def withdraw(self, amount):
        self._check_status()
        if amount <= 0:
            raise InvalidOperationError("Сумма должна быть положительной")
        total = amount + self.commission
        new_balance = self._balance - total
        if new_balance < -self.overdraft_limit:
            raise InsufficientFundsError("Превышен лимит овердрафта")
        self._balance = new_balance
        return True

    def get_account_info(self):
        return f"{self.account_id}, {self.owner}, {self._balance}, {self.status}, {self.currency}, {self.overdraft_limit}, {self.commission}"

    def __str__(self):
        return f"PremiumAccount, {self.owner}, {self.account_id[-4:]}, {self.status}, {self._balance}, {self.currency}, {self.overdraft_limit}, {self.commission}"


class InvestmentAccount(BankAccount):
    def __init__(self, owner, balance, status, currency, portfolio, account_id=None):
        super().__init__(owner, balance, status, currency, account_id)
        self.portfolio = portfolio

    def project_yearly_growth(self):
        rates = {
            "stocks": 0.16,
            "bonds": 0.12,
            "etf": 0.12
        }
        total = 0
        for asset in rates:
            total += self.portfolio[asset] * (1 + rates[asset])
        return total

    def withdraw(self, amount):
        return super().withdraw(amount)

    def get_account_info(self):
        return f"{self.account_id}, {self.owner}, {self._balance}, {self.status}, {self.currency}, {self.portfolio}"

    def __str__(self):
        return f"InvestmentAccount, {self.owner}, {self.account_id[-4:]}, {self.status}, {self._balance}, {self.currency}, {self.portfolio}"


# Демонстрация работы PremiumAccount

premium = PremiumAccount(
    owner="Наиля",
    balance=10000,
    status="active",
    currency="RUB",
    overdraft_limit=5000,
    commission=100
)

print(premium)

# Проверяем овердрафт и комиссию
premium.withdraw(14000)
print(premium)

# Проверяем превышение лимита овердрафта
try:
    premium.withdraw(1000)
except InsufficientFundsError as e:
    print(e)

# Проверяем, что баланс не изменился после неудачной операции
print(premium)

# Демонстрация работы InvestmentAccount
investment = InvestmentAccount(
    owner="Наиля",
    balance=10000,
    status="active",
    currency="RUB",
    portfolio={
        "stocks": 5000,
        "bonds": 3000,
        "etf": 2000
    }
)

print(investment)

# Прогноз стоимости портфеля через год
print(investment.project_yearly_growth())

# Проверяем, что баланс счёта не изменился
print(investment)