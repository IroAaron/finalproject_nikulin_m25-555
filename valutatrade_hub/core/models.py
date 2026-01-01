import hashlib
import datetime
import json
from typing import Optional
from typing import Union
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime

class User:
    def __init__(
        self, 
        user_id: int, 
        username: str, 
        hashed_password: str, 
        salt: str, 
        registration_date: datetime.datetime
    ):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def registration_date(self) -> datetime.datetime:
        return self._registration_date

    @username.setter
    def username(self, value: str):
        if not value:
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value

    def get_user_info(self) -> dict:
        """Возвращает информацию о пользователе без пароля"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }

    def change_password(self, new_password: str):
        """Меняет пароль пользователя с хешированием"""
        if len(new_password) < 4:
            raise ValueError("Пароль должен содержать минимум 4 символа")
        
        self._hashed_password = self._hash_password(new_password)

    def verify_password(self, password: str) -> bool:
        """Проверяет соответствие введённого пароля"""
        return self._hash_password(password) == self._hashed_password

    def _hash_password(self, password: str) -> str:
        """Хеширует пароль с солью"""
        hash_object = hashlib.sha256()
        password_bytes = password.encode('utf-8')
        salt_bytes = self._salt.encode('utf-8')
        hash_object.update(password_bytes + salt_bytes)
        return hash_object.hexdigest()

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Создаёт объект User из словаря"""
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            hashed_password=data['hashed_password'],
            salt=data['salt'],
            registration_date=datetime.datetime.fromisoformat(data['registration_date'])
        )

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для сохранения в JSON"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat()
        }

if __name__ == "__main__":
    user = User(
        user_id=1,
        username="alice",
        hashed_password="",
        salt="x5T9!",
        registration_date=datetime.datetime.now()
    )
    
    user.change_password("securepass")
    
    print(user.verify_password("securepass"))
    print(user.verify_password("wrongpass"))
    
    print(user.get_user_info())

class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self._balance = Decimal(str(balance))

    @property
    def balance(self) -> Decimal:
        """Геттер для баланса"""
        return self._balance

    @balance.setter
    def balance(self, value: Union[float, int, str]):
        """Сеттер с валидацией"""
        try:
            value = Decimal(str(value))
        except (ValueError, TypeError):
            raise ValueError("Баланс должен быть числом")
            
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
            
        self._balance = value

    def deposit(self, amount: Union[float, int]) -> None:
        """Пополнение баланса"""
        if not isinstance(amount, (float, int)):
            raise TypeError("Сумма должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
            
        self.balance += Decimal(str(amount))

    def withdraw(self, amount: Union[float, int]) -> None:
        """Снятие средств"""
        if not isinstance(amount, (float, int)):
            raise TypeError("Сумма должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
            
        if amount > self.balance:
            raise ValueError("Недостаточно средств для снятия")
            
        self.balance -= Decimal(str(amount))

    def get_balance_info(self) -> dict:
        """Информация о балансе"""
        return {
            "currency_code": self.currency_code,
            "balance": float(self.balance)
        }

    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        return {
            "currency_code": self.currency_code,
            "balance": float(self.balance)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Wallet':
        """Создание объекта из словаря"""
        return cls(
            currency_code=data['currency_code'],
            balance=data['balance']
        )

if __name__ == "__main__":
    wallet = Wallet("BTC", 0.05)
    
    wallet.deposit(0.1)
    print(wallet.get_balance_info())
    
    wallet.withdraw(0.05)
    print(wallet.get_balance_info())
    
    try:
        wallet.withdraw(1.0)
    except ValueError as e:
        print(e)

class Portfolio:
    EXCHANGE_RATES = {
        'USD': 1.0,
        'EUR': 1.1,
        'BTC': 40000.0,
        'RUB': 0.012
    }

    def __init__(self, user_id: int):
        self._user_id = user_id
        self._wallets: Dict[str, Wallet] = {}

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Wallet]:
        """Возвращает копию словаря кошельков"""
        return self._wallets.copy()

    def add_currency(self, currency_code: str) -> None:
        """Добавляет новый кошелёк, если его ещё нет"""
        if currency_code in self._wallets:
            raise ValueError(f"Кошелёк для валюты {currency_code} уже существует")
        
        if currency_code not in self.EXCHANGE_RATES:
            raise ValueError(f"Неизвестный код валюты {currency_code}")
            
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Optional[Wallet]:
        """Возвращает кошелёк по коду валюты"""
        return self._wallets.get(currency_code)

    def get_total_value(self, base_currency: str = 'USD') -> float:
        """Возвращает общую стоимость портфеля в базовой валюте"""
        if base_currency not in self.EXCHANGE_RATES:
            raise ValueError(f"Неизвестный код базовой валюты {base_currency}")
            
        total_value = 0.0
        
        for wallet in self._wallets.values():
            currency_rate = self.EXCHANGE_RATES.get(wallet.currency_code)
            base_rate = self.EXCHANGE_RATES.get(base_currency)
            
            if currency_rate is None or base_rate is None:
                continue
                
            value_in_base = (wallet.balance * currency_rate) / base_rate
            total_value += value_in_base
            
        return total_value

    def buy_currency(self, amount: float, from_currency: str, to_currency: str) -> None:
        """Покупка валюты"""
        if amount <= 0:
            raise ValueError("Сумма покупки должна быть положительной")
            
        from_wallet = self.get_wallet(from_currency)
        to_wallet = self.get_wallet(to_currency)
        
        if not from_wallet or not to_wallet:
            raise ValueError("Один из кошельков не существует")
            
        from_wallet.withdraw(amount)
        
        from_rate = self.EXCHANGE_RATES[from_currency]
        to_rate = self.EXCHANGE_RATES[to_currency]
        converted_amount = (amount * from_rate) / to_rate
        
        to_wallet.deposit(converted_amount)

    def sell_currency(self, amount: float, from_currency: str, to_currency: str) -> None:
        """Продажа валюты"""
        if amount <= 0:
            raise ValueError("Сумма продажи должна быть положительной")
            
        from_wallet = self.get_wallet(from_currency)
        to_wallet = self.get_wallet(to_currency)
        
        if not from_wallet or not to_wallet:
            raise ValueError("Один из кошельков не существует")
            
        if from_wallet.balance < amount:
            raise ValueError("Недостаточно средств для продажи")
            
        from_wallet.withdraw(amount)
        
        from_rate = self.EXCHANGE_RATES[from_currency]