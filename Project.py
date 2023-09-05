from datetime import datetime
import pytz


class Account:
    transaction_id = 0
    interest_rate = 0.0

    def __init__(self, account_number, first_name, last_name, preferred_timezone=None, starting_balance=0.0):
        self.account_number = account_number
        self.first_name = first_name
        self.last_name = last_name
        self.preferred_timezone = preferred_timezone
        self.balance = starting_balance
        self.transactions = []

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def get_account_number(self):
        return self.account_number

    @property
    def get_balance(self):
        return self.balance

    def set_first_name(self, first_name):
        self.first_name = first_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_account_number(self, account_number):
        self.account_number = account_number

    @classmethod
    def set_interest_rate(cls, rate):
        cls.interest_rate = rate

    def _generate_confirmation_number(self, transaction_type):
        Account.transaction_id += 1
        current_time = datetime.utcnow()
        if self.preferred_timezone:
            current_time = current_time.replace(tzinfo=pytz.utc)
            current_time = current_time.astimezone(self.preferred_timezone)
        timestamp = current_time.strftime("%Y%m%d%H%M%S")
        confirmation_number = f"{transaction_type}-{self.account_number}-{timestamp}-{Account.transaction_id}"
        return confirmation_number

    def _record_transaction(self, transaction_type, amount):
        confirmation_number = self._generate_confirmation_number(transaction_type)
        self.transactions.append({
            "type": transaction_type,
            "amount": amount,
            "timestamp": datetime.utcnow(),
            "confirmation_number": confirmation_number
        })

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self._record_transaction("D", amount)
            return self._generate_confirmation_number("D")
        else:
            return self._generate_confirmation_number("X")

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self._record_transaction("W", amount)
            return self._generate_confirmation_number("W")
        else:
            return self._generate_confirmation_number("X")

    def deposit_interest(self):
        if Account.interest_rate > 0:
            interest_earned = self.balance * (Account.interest_rate / 100)
            self.balance += interest_earned
            self._record_transaction("I", interest_earned)
            return self._generate_confirmation_number("I")

    def parse_confirmation_code(self, confirmation_code, target_timezone=None):
        parts = confirmation_code.split('-')
        if len(parts) == 4:
            transaction_type, account_number, timestamp, transaction_id = parts
            transaction_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
            if target_timezone:
                transaction_time = transaction_time.replace(tzinfo=pytz.utc)
                transaction_time = transaction_time.astimezone(target_timezone)
            return {
                "account_number": account_number,
                "transaction_code": transaction_type,
                "transaction_id": int(transaction_id),
                "time": transaction_time.strftime("%Y-%m-%d %H:%M:%S (%Z)"),
                "time_utc": transaction_time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        else:
            return None


mst_timezone = pytz.timezone('Etc/GMT-2')
account = Account("140568", "John", "Doe", mst_timezone, 100.00)
Account.set_interest_rate(0.5)
confirmation_number = account.deposit(50.00)
print(f"Confirmation Number: {confirmation_number}")
parsed_transaction = account.parse_confirmation_code(confirmation_number, mst_timezone)
print(f"Account Number: {parsed_transaction['account_number']}")
print(f"Transaction Code: {parsed_transaction['transaction_code']}")
print(f"Transaction ID: {parsed_transaction['transaction_id']}")
print(f"Time (MST): {parsed_transaction['time']}")
print(f"Time (UTC): {parsed_transaction['time_utc']}")
print(f"New Balance: {account.balance:.2f}")