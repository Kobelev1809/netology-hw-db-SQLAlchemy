import json
import os

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from models import create_tables
from models import Sale, Stock, Shop, Book, Publisher


type_object = {'publisher': Publisher,
              'book': Book,
              'shop': Shop,
              'stock': Stock,
              'sale': Sale}
all_objects = []

with open('tests_data.json', encoding='utf-8') as f:
    json_data = json.load(f)
for element in json_data:
    some_object = type_object.get(element['model'])
    all_objects.append(some_object(**element['fields']))

user = os.getenv('user')
password = os.getenv('password')
db_name = os.getenv('db_name')
DSN = f'postgresql://{user}:{password}@localhost:5432/{db_name}'
engine = sqlalchemy.create_engine(DSN)
try:
    create_tables(engine)
except:
    print('Для DSN engine не получилось загрузить данные!')
    print('os.getenv(user) =', os.getenv('user'))
    print('os.getenv(password) =', os.getenv('password'))
    print('os.getenv(db_name) =', os.getenv('db_name'))
    exit()
    

Session = sessionmaker(bind=engine)

session = Session()
session.add_all(all_objects)
session.commit()

def select_data(name):
    subq_1 = session.query(Book).join(
        Publisher,
        Book.id_publisher == Publisher.id
        ).filter(
            Publisher.name == name
            ).subquery()
    subq_2 = session.query(Stock).join(
        subq_1,
        Stock.id_book == subq_1.c.id
        ).subquery()
    necessary_data = session.query(Sale).join(
        subq_2,
        Sale.id_stock == subq_2.c.id
        ).all()
    for d_element in necessary_data:
        print_book_data(d_element)

def print_book_data(data):
    all_string = []
    all_string.append(data.stock.books.title.ljust(40, ' '))
    all_string.append(data.stock.books.publisher.name.ljust(20, ' '))
    all_string.append(str(data.price).ljust(5, ' '))
    all_string.append(data.date_sale.strftime('%d-%m-%y'))
    print(' | '.join(all_string))


list_of_publ = []
for publ in session.query(Publisher).all():
    list_of_publ.append(publ.name)

print('В базе данных имеется информация по книгам следующих издательств:')
names = ', '.join([f'{i + 1}: {e}' for i, e in enumerate(list_of_publ)])
print(names)
print('чтобы получить данные введите номер издательства...')
print('чтобы выйти введите просто пустую строку...')
while True:
    name = input('книги какого издательства Вас интересуют: ')
    if name == '':
        break
    elif name.isdigit() and int(name) in range(1, len(list_of_publ) + 1):
        print('здесь сделаем запрос на вывод информации...')
        query_data = select_data(list_of_publ[int(name) - 1])
        break
    else:
        print('Введено некоректное значение...')

session.close()