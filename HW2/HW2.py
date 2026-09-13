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
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InvalidOperationError("Сумма должна быть положительным числом")
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
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InvalidOperationError("Сумма должна быть положительным числом")
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
        if not isinstance(portfolio, dict):
            raise InvalidOperationError("Портфель должен быть словарем")
        allowed_assets = {"stocks", "bonds", "etf"}
        for asset, amount in portfolio.items():
            if asset not in allowed_assets:
                raise InvalidOperationError("Недопустимый актив")
            if not isinstance(amount, (int, float)) or amount < 0:
                raise InvalidOperationError(
                    "Сумма актива должна быть неотрицательным числом"
                )
        self.portfolio = portfolio

    def project_yearly_growth(self):
        rates = {
            "stocks": 0.16,
            "bonds": 0.12,
            "etf": 0.12
        }
        total = 0
        for asset, rate in rates.items():
            amount = self.portfolio.get(asset, 0)
            total += amount * (1 + rate)
        return total

    def withdraw(self, amount):
        return super().withdraw(amount)

    def get_account_info(self):
        return (
            f"{self.account_id}, {self.owner}, {self._balance}, "
            f"{self.status}, {self.currency}, {self.portfolio}"
        )

    def __str__(self):
        return (
            f"InvestmentAccount, {self.owner}, {self.account_id[-4:]}, "
            f"{self.status}, {self._balance}, {self.currency}, {self.portfolio}"
        )


if __name__ == "__main__":
    # =========================
    # SavingsAccount
    # =========================
    savings_1 = SavingsAccount(
        owner="Наиля",
        balance=10000,
        status="active",
        currency="RUB",
        min_balance=2000,
        monthly_rate=0.05
    )
    savings_2 = SavingsAccount(
        owner="Иван",
        balance=20000,
        status="active",
        currency="RUB",
        min_balance=5000,
        monthly_rate=0.03
    )
    print(savings_1)
    print(savings_2)
    # Разные операции
    savings_1.withdraw(3000)
    savings_2.apply_monthly_interest()
    print(savings_1)
    print(savings_2)
    # =========================
    # PremiumAccount
    # =========================
    premium_1 = PremiumAccount(
        owner="Наиля",
        balance=10000,
        status="active",
        currency="RUB",
        overdraft_limit=5000,
        commission=100
    )
    premium_2 = PremiumAccount(
        owner="Иван",
        balance=20000,
        status="active",
        currency="RUB",
        overdraft_limit=10000,
        commission=200
    )
    print(premium_1)
    print(premium_2)
    # Разные операции
    premium_1.withdraw(14000)
    premium_2.withdraw(5000)
    print(premium_1)
    print(premium_2)
    # =========================
    # InvestmentAccount
    # =========================
    investment_1 = InvestmentAccount(
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
    investment_2 = InvestmentAccount(
        owner="Иван",
        balance=15000,
        status="active",
        currency="RUB",
        portfolio={
            "stocks": 10000
        }
    )
    print(investment_1)
    print(investment_2)
    # Разные операции
    print(investment_1.project_yearly_growth())
    print(investment_2.project_yearly_growth())
    investment_1.withdraw(2000)
    investment_2.deposit(3000)
    print(investment_1)
    print(investment_2)