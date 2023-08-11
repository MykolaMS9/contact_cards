import collections
from collections import UserDict
from datetime import datetime
import re
import pickle
from abc import ABC, abstractmethod
from typing import Dict


class ContactExist(Exception):
    pass


class ContactNotExist(Exception):
    pass


class UncorrectedPhoneNumber(Exception):
    pass


class UncorrectedBirthdayType(Exception):
    pass


class TypeValue(Exception):
    pass


class UnknownCommand(Exception):
    pass


class Event:
    _observers = []

    def register(self, observer: object):
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer: object):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: str, data=None):
        for observer in self._observers:
            observer(event, data)


# --------------------------------adding listeners
class ISubject(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class FileWorker(ISubject):
    def __init__(self, filename: str):
        self.filename = filename

    def load(self) -> Dict:
        try:
            with open(self.filename, "rb") as fl:
                return pickle.load(fl)
        except:
            return {}

    def __call__(self, event: str, data: object):
        with open(self.filename, "wb") as file:
            pickle.dump(data, file)


# --------------------------------end adding listeners


class AddressBook(UserDict):
    max_value = 1

    def __init__(self, filename: str):
        self.event = Event()
        self.__file_worker = FileWorker(filename)
        self.event.register(self.__file_worker)
        self.data = self.__file_worker.load()

    def __setitem__(self, key: str, value: object):
        self.data[key] = value
        self.event.notify("New data", self.data)

    def __getitem__(self, key: str):
        return self.data[key]

    def __call__(self, n=1, *args, **kwargs):
        self.max_value = int(n)
        self.list_keys = list(self.data.keys())
        return self

    def __next__(self) -> str:
        return_obj = []
        if not self.list_keys:
            raise StopIteration
        for _ in range(self.max_value):
            if self.list_keys:
                key = self.list_keys.pop(0)
                return_obj.append(self.data[key])
        return "|| ".join([str(val) for val in return_obj])

    def __iter__(self):
        return self


class Record:
    def __init__(self, name: str, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def __repr__(self) -> str:
        result = f"{self.name.value}"
        if self.phones:
            result += f'; phones {", ".join([phone.value for phone in self.phones])}'
        if self.birthday.value:
            result += f"; birthday in {self.days_to_birthday()} days"
        return result

    def add_phone(self, phone: str):
        if phone:
            self.phones.append(Phone(phone))

    def __find_phone(self, phone: str) -> object | None:
        result = list(filter(lambda phon: phon.value == phone, self.phones))
        return result[0] if len(result) > 0 else None

    def delete_phone(self, phone: str):
        phone = Phone(phone)
        self.phones.remove(self.__find_phone(phone.value))

    def edit_phone(self, exist_phone: str, new_phone: str):
        exist_phone = Phone(exist_phone)
        self.phones[self.phones.index(self.__find_phone(exist_phone.value))] = Phone(
            new_phone
        )

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self) -> int:
        birthday = self.birthday.value
        today = datetime.now().date()
        years = today.year - birthday.year
        if (
            birthday.month == today.month
            and birthday.day >= today.day
            or birthday.month > today.month
        ):
            years -= 1
        next_day = datetime(
            year=birthday.year + years + 1, month=birthday.month, day=birthday.day
        ).date()
        return (next_day - today).days


class Field(ABC):
    def __init__(self, value: str):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value


class Name(Field):
    pass


class Phone(Field):
    # Constants
    FULL_LEN_NUMBER = 12
    SHORT_LEN_NUMBER = 10

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(
        self,
        value: str,
        full_len_number=FULL_LEN_NUMBER,
        short_len_number=SHORT_LEN_NUMBER,
    ):
        result = "".join(re.findall("[0-9]", value))
        if len(result) == full_len_number:
            result = f"+{result}"
        elif len(result) == short_len_number:
            result = f"+38{result}"
        else:
            raise UncorrectedPhoneNumber
        self._value = result


class Birthday(Field):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: str):
        if value:
            birthday_str = value.split("-")  # YYYY-mm-dd
            if len(birthday_str) != 3:
                birthday_str = value.split(".")  # YYYY.mm.dd
            elif len(birthday_str) != 3:
                birthday_str = value.split("/")  # YYYY/mm/dd
            elif len(birthday_str) != 3:
                raise UncorrectedBirthdayType
            try:
                int(birthday_str[0])
                int(birthday_str[1])
                int(birthday_str[2])
            except:
                raise UncorrectedBirthdayType
            self._value = datetime(
                year=int(birthday_str[0]),
                month=int(birthday_str[1]),
                day=int(birthday_str[2]),
            ).date()
        else:
            self._value = value
