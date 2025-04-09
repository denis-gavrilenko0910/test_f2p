import pickle
from collections import UserDict
from datetime import datetime, timedelta


class Field:
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return str(self.value)
  

class Name(Field):
  pass


class Phone(Field):
  def __init__(self, value: str):
    if value.isdigit() and len(value) == 10:
      super().__init__(value)
    else:
      raise ValueError('Incorrect phone number')
    

class Birthday(Field):
  def __init__(self, value):
    try:
      brth_date = datetime.strptime(value, '%d.%m.%Y')
      super().__init__(brth_date)
    except ValueError:
      raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
  def __init__(self, name):
    self.name = Name(name)
    self.phones = []
    self.birthday = None
  
  def add_birthday(self, birthday):
    self.birthday = Birthday(birthday)

  def add_phone(self, phone):
    self.phones.append(Phone(phone))
  
  def find_phone(self, phone):
    for phone_obj in self.phones:
      if phone_obj.value == phone:
        return phone_obj
      
  def remove_phone(self, phone):
    rem_phone = self.find_phone(phone)
    if rem_phone:
      self.phones.remove(rem_phone)

  def edit_phone(self, old_phone, new_phone):
    phone_obj = self.find_phone(old_phone)
    if phone_obj:
      phone_obj.value = new_phone

  def __str__(self):
    birthday = self.birthday.value.strftime('%d.%m.%Y') if self.birthday else '-'
    return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {birthday}"


class AddressBook(UserDict):
  def add_record(self, record: Record):
    self.data[record.name.value] = record

  def find(self, name) -> Record:
    if name in self.data:
      return self.data[name]
    
  def get_upcoming_birthdays(self):
    result = []
    date_now = datetime.today().date()
    for name, record in self.data.items():
      if record.birthday:    
        user_brthday = record.birthday.value.date()
        user_brthday = user_brthday.replace(year=date_now.year)
        if user_brthday < date_now:
          user_brthday = user_brthday.replace(year=date_now.year + 1)

        if user_brthday >= date_now and user_brthday < date_now + timedelta(days=7):
          user_brthday = user_brthday.strftime('%d.%m.%Y')
          result.append({'name': name, 'congratulation_date':  user_brthday})
      
    return result  
  
  def delete(self, name):
    del_contact = self.find(name)
    if del_contact:
      self.data.pop(name, None)


def input_error(func):
  def inner(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except ValueError:
      return "Give me name and phone please."
    except IndexError:
      return "Give me the name."
    except KeyError:
      return "No such contact."

  return inner

def parse_input(user_input) -> tuple:
  cmd, *args = user_input.split()
  cmd = cmd.strip().lower()
  return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
  name, phone, *_ = args
  record = book.find(name)
  message = "Contact updated."
  if record is None:
    record = Record(name)
    book.add_record(record)
    message = "Contact added."
  if phone:
    record.add_phone(phone)
  return message

@input_error
def change_contact(args, book: AddressBook) -> str:
  name, old_phone, new_phone = args
  result = 'No contact found'
  record: Record = book.find(name)
  if record:
    record.edit_phone(old_phone, new_phone)
    result = 'Contact updated.'    
  return result 

@input_error
def show_phone(args, book: AddressBook) -> str:
  name = args[0]
  record: Record = book.find(name)
  if record:
    result = f"phones: {'; '.join(p.value for p in record.phones)}"
  return result 

@input_error
def show_all(book: AddressBook) -> str:
  result = ''
  for name, record in book.data.items():
    result += f'{record}\n'
  if not result:
    return 'no contacts :('
  return result

@input_error
def add_birthday(args, book: AddressBook) -> str:
  name, birthday = args
  record: Record = book.find(name)
  if record:
    record.add_birthday(birthday)
    return 'Contact`s birthday added'
  return 'no contact'

@input_error
def show_birthday(args, book: AddressBook) -> str:
  name = args[0]
  record: Record = book.find(name)
  if record:
    birthday = record.birthday.value.strftime('%d.%m.%Y') if record.birthday else '-'
    return birthday
  return 'The contact is not found'

@input_error
def birthdays(book: AddressBook):
  result = book.get_upcoming_birthdays()
  all_cont_brthds = ''
  for el in result:
    all_cont_brthds += f'name: {el["name"]}, congratulation date: {el["congratulation_date"]}'
  return all_cont_brthds
    

def save_data(book, filename="addressbook.pkl"):
  with open(filename, "wb") as f:
    pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
  try:
    with open(filename, "rb") as f:
      return pickle.load(f)
  except FileNotFoundError:
    return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
  book = load_data()
  print("Welcome to the assistant bot!")
  while True:
    user_input = input("Enter a command: ")
    command, *args = parse_input(user_input)
    if command in ["close", "exit"]:
      save_data(book)
      print("Good bye!")
      break
    elif command == "hello":
      print("How can I help you?")
    elif command == "add":
      print(add_contact(args, book))
    elif command == "change":
      print(change_contact(args, book))
    elif command == "phone":
      print(show_phone(args, book))
    elif command == "all":
      print(show_all(book))
    elif command == "add-birthday":
      print(add_birthday(args, book))
    elif command == "show-birthday":
      print(show_birthday(args, book))
    elif command == "birthdays":
      print(birthdays(book))         
    else:
      print("Invalid command.")
        

if __name__ == "__main__":
  main()