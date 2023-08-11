from Bot import Handler
from contacts_core import AddressBook


def main():
    handler = Handler()
    file_name = "contacts_book.bin"
    book_data = AddressBook(file_name)
    while True:
        print(handler(input("Write command or type 'help': "), data=book_data))


if __name__ == "__main__":
    main()
