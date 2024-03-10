import sqlalchemy
import json

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


DSN = 'postgresql://postgres:KiaPostgre1809@localhost:5432/books_db'
engine = sqlalchemy.create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)

session = Session()
session.add_all(all_objects)
session.commit()

def get_data(name):
    subq_1 = session.query(Book).join(Publisher, Book.id_publisher == Publisher.id).all()
    # data = session.query(Stock).join(subq_1, Stock.id == subq_1.c.stock_id)
    # subq_2 = subq_1.join(Stock.id_book)
    # subq_3 = subq_2.join(Shop.stock)
    # data = session.query(Sale).join(subq_3, Sale.id_stock == subq_3.c.stock_id).all()
    for e in subq_1:
        print(e.publisher.name)
    pass

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
        query_data = get_data(list_of_publ[int(name) - 1])
        break
    else:
        print('Введено некоректное значение...')

session.close()