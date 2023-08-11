from abc import ABC, abstractmethod
import sys
from contacts_core import (
    AddressBook,
    Record,
    ContactExist,
    ContactNotExist,
    UncorrectedPhoneNumber,
    TypeValue,
    UncorrectedBirthdayType,
    UnknownCommand,
)
from typing import Dict, Tuple, List


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeValue:
            return "Uncorrected format of a contact!!! \nExample: \n         add/change contact_name phone_number"
        except ContactExist:
            return "Contact is already existed!!! \nExample: \n         add new_contact_name new_phone_number"
        except ContactNotExist:
            return "Contact is not exist :("
        except UncorrectedPhoneNumber:
            return "Uncorrected type of number :("
        except SystemExit:
            return func(*args, **kwargs)
        except UnknownCommand:
            return f"Error command or uncorrected format"
        except TypeError:
            return "Missing arguments: name or number :("
        except ValueError:
            return "Number is not exist :("
        except UncorrectedBirthdayType:
            return 'Check correct type of data:\nexpected "yyyy-mm-dd" or "yyyy.mm.dd" or "yyyy/mm/dd"'
        except:
            return f"Error command or uncorrected format"

    return inner


def raise_error():
    raise UnknownCommand


# ------------ add commands


class NewCommand(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self, data: object, *args, **kwargs):
        pass


class Close(NewCommand):
    def __init__(self):
        self.command = ["close", "good bye", "exit"]

    @input_error
    def __call__(self, *args, **kwargs):
        sys.exit(f"Good bye!")


class Hello(NewCommand):
    def __init__(self):
        self.command = ["hello"]

    @input_error
    def __call__(self, *args, **kwargs):
        return f"How can I help you?"


class AddPhone(NewCommand):
    def __init__(self):
        self.command = ["add phone"]

    @input_error
    def __call__(
        self, contact_name: str, phone_number: str, *args, data: AddressBook, **kwargs
    ) -> str:
        if not contact_name or not phone_number:
            raise TypeValue
        if contact_name in data.data:
            # added new phone to existed record
            record_ = data[contact_name]
        else:
            # created new record with name
            record_ = Record(contact_name)
        record_.add_phone(phone_number)
        data[contact_name] = record_
        return f"Successfully added {contact_name} with number {phone_number}"


class AddBirthday(NewCommand):
    def __init__(self):
        self.command = ["add birthday"]

    @input_error
    def __call__(
        self, contact_name: str, birthday_date: str, *args, data: AddressBook, **kwargs
    ) -> str:
        if not contact_name or not birthday_date:
            raise TypeValue
        if contact_name in data.data:
            # added new phone to existed record
            record_ = data[contact_name]
        else:
            # created new record with name
            record_ = Record(contact_name)
        record_.add_birthday(birthday_date)
        data[contact_name] = record_
        return f"Successfully added to {contact_name} a new birthday {birthday_date}"


class Change(NewCommand):
    def __init__(self):
        self.command = ["change"]

    @input_error
    def __call__(
        self,
        contact_name: str,
        exist_phone: str,
        phone_number: str,
        *args,
        data: AddressBook,
        **kwargs,
    ) -> str:
        if not contact_name or not phone_number or not exist_phone:
            raise TypeValue
        if contact_name in data.data:
            # added new phone to existed record
            record_ = data[contact_name]
            record_.edit_phone(exist_phone, phone_number)
            data[contact_name] = record_
        else:
            raise ContactNotExist
        return f"Successfully changed {contact_name} exist number {exist_phone} to {phone_number}"


class Phone(NewCommand):
    def __init__(self):
        self.command = ["phone"]

    @input_error
    def __call__(self, contact_name: str, *args, data: AddressBook, **kwargs) -> object:
        if not contact_name:
            raise TypeValue
        if contact_name in data.data:
            return data[contact_name]
        else:
            raise ContactNotExist


class ShowAll(NewCommand):
    def __init__(self):
        self.command = ["show all"]

    @input_error
    def __call__(self, n: str, *args, data: AddressBook, **kwargs) -> str:
        if not n:
            n = 1
        for val in data(int(n)):
            print(val)
        return "End of list"


class Search(NewCommand):
    def __init__(self):
        self.command = ["search"]

    @input_error
    def __call__(self, need_find: str, *args, data: AddressBook, **kwargs) -> str:
        flag = False
        for key in data.data:
            if need_find in key:
                print(data[key])
                flag = True
            else:
                for phone in data[key].phones:
                    if need_find in phone.value:
                        print(data[key])
                        flag = True
                        break
        if flag:
            return f"End of list!"
        return f"No results :("


class Delete(NewCommand):
    def __init__(self):
        self.command = ["delete"]

    @input_error
    def __call__(
        self, contact_name: str, phone_number: str, *args, data: AddressBook, **kwargs
    ) -> str:
        if not phone_number or not contact_name:
            raise TypeError
        if contact_name in data.data:
            record_ = data[contact_name]
            record_.delete_phone(phone_number)
            data[contact_name] = record_
            return f"Number {phone_number} in {contact_name} has been deleted"
        else:
            raise ContactNotExist


class Help(NewCommand):
    def __init__(self):
        self.command = ["help"]

    @input_error
    def __call__(self, *args, commands_dict: Dict[str, object], **kwargs) -> str:
        print(f"Here's existed commands:")
        for key in commands_dict:
            print("{:<10}{:}".format(" ", key))
        return f"Good luck!"


# ---------------end commands


class Handler:
    dict_ = {}

    def __init__(self):
        commands_list = [
            Close(),
            Hello(),
            AddPhone(),
            AddBirthday(),
            Change(),
            Phone(),
            ShowAll(),
            Search(),
            Delete(),
            Help(),
        ]
        for command_obj in commands_list:
            for command in command_obj.command:
                self.dict_[command] = command_obj

    def __find_command(self, string: str) -> Tuple[None | str, List[str]]:
        for key in self.dict_:
            l1 = key.split(" ")
            l2 = string.split(" ")
            command = l2[: len(l1)]
            if key == (" ".join(command).lower()):
                return key, l2[len(l1) :]
        return None, []

    @input_error
    def __call__(self, input_string: str, data: object) -> object:
        (command_name, arguments) = self.__find_command(input_string)
        if command_name not in self.dict_:
            raise_error()
        command = self.dict_.get(command_name)
        values = 3 * [None]
        for val, arg in zip(values, arguments):
            values[values.index(val)] = arg
        return command(
            values[0], values[1], values[2], data=data, commands_dict=self.dict_
        )
