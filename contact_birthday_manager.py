import datetime
import pickle
from collections import UserDict
class Field:
    def __init__(self, value):
        self.value = value
class Name(Field):
    pass
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Incorrect date format, should be DD.MM.YYYY")
        super().__init__(value)
class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]
    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"{self.name.value}: {phones_str}{birthday_str}"
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    def find(self, name):
        return self.data.get(name)
    def delete(self, name):
        if name in self.data:
            del self.data[name]
    def load_data(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except (FileNotFoundError, EOFError):
            self.data = {}
    def save_data(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)
    def get_birthdays_per_week(self):
        today = datetime.date.today()
        result = []
        for record in self.data.values():
            if record.birthday:
                birthday = datetime.datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)
                if 0 <= (birthday_this_year - today).days < 7:
                    result.append(record.name.value)
        return result
class CLIAssistant:
    def __init__(self):
        self.book = AddressBook()
        self.book.load_data('address_book.data')
    def run(self):
        print("Welcome to the CLI Address Book Assistant!")
        while True:
            user_input = input("Enter a command: ")
            command, args = parse_input(user_input)
            if command in ["exit", "close"]:
                self.book.save_data('address_book.data')
                print("Good bye!")
                break
            self.handle_command(command, args)
    def handle_command(self, command, args):
        if command == "add" and len(args) == 2:
            name, phone = args
            try:
                record = self.book.get(name, Record(name))
                record.add_phone(phone)
                self.book.add_record(record)
                print(f"Contact {name} added with phone number {phone}.")
            except ValueError as e:
                print(e)
        elif command == "change" and len(args) == 2:
            name, new_phone = args
            record = self.book.find(name)
            if record:
                record.edit_phone(record.phones[0].value, new_phone)
                print(f"Phone for {name} changed to {new_phone}.")
            else:
                print(f"Contact {name} not found.")
        elif command == "phone" and len(args) == 1:
            name = args[0]
            record = self.book.find(name)
            if record:
                print(f"{name}: {', '.join(phone.value for phone in record.phones)}")
            else:
                print(f"Contact {name} not found.")
        elif command == "all":
            for name, record in self.book.data.items():
                print(record)
        elif command == "add-birthday" and len(args) == 2:
            name, birthday = args
            record = self.book.find(name)
            if record:
                record.add_birthday(birthday)
                print(f"Birthday for {name} set to {birthday}.")
            else:
                print(f"Contact {name} not found.")
        elif command == "show-birthday" and len(args) == 1:
            name = args[0]
            record = self.book.find(name)
            if record and record.birthday:
                print(f"{name}'s birthday is on {record.birthday.value}.")
            else:
                print(f"Contact {name} not found or birthday not set.")
        elif command == "birthdays":
            birthdays = self.book.get_birthdays_per_week()
            if birthdays:
                print("Birthdays this week:")
                for name in birthdays:
                    print(name)
            else:
                print("No birthdays this week.")
        elif command == "hello":
            print("How can I help you?")
        else:
            print("Invalid command or arguments.")

def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.lower(), args

if __name__ == "__main__":
    assistant = CLIAssistant()
    assistant.run()
