import sqlite3
from faker import Faker
import random


fake = Faker()


con = sqlite3.connect("Library.db")
cursor = con.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS book(
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    date_issue DATE NOT NULL,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES author(id)
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS author(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    birth_date DATE NOT NULL,
    birth_place TEXT NOT NULL
)
""")


def is_table_empty(table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    return row_count == 0


def author_generator():
    authors = []
    for _ in range(500):
        author = (
            fake.first_name(),
            fake.last_name(),
            fake.date_between(start_date='-65y', end_date='-25y'),
            fake.city()
        )
        authors.append(author)
    return authors


if is_table_empty("author"):
    cursor.executemany("""
    INSERT INTO author (name, surname, birth_date, birth_place) VALUES (?,?,?,?)
    """, author_generator())


def book_generator():
    books = []
    for _ in range(1000):
        book = (
            fake.sentence(nb_words=3),
            fake.word(),
            random.randint(100, 1000),
            fake.date_between(start_date='-24y', end_date='now'),
            random.randint(1, 500)
        )
        books.append(book)
    return books


if is_table_empty("book"):
    cursor.executemany("""
    INSERT INTO book (name, category, page_number, date_issue, author_id) VALUES (?,?,?,?,?)
    """, book_generator())


cursor.execute("SELECT * FROM book WHERE page_number = (SELECT MAX(page_number) FROM book)")
result = cursor.fetchall()
print("Max page book:")
for row in result:
    print(row)

cursor.execute("SELECT AVG(page_number) FROM book")
print("\nAverage page number:")
print(cursor.fetchone()[0])


cursor.execute("SELECT MAX(birth_date), name FROM author")
print("\nYoungest author:")
print(cursor.fetchone())


cursor.execute("""
SELECT id, name
FROM author
WHERE NOT EXISTS (
    SELECT 1 FROM book WHERE book.author_id = author.id
)
""")
result = cursor.fetchall()
print("\nAuthors without books:")
for row in result:
    print(row)


cursor.execute("""
SELECT author.id, author.name, COUNT(book.author_id) AS book_count
FROM author
JOIN book ON book.author_id = author.id
GROUP BY author.id, author.name
HAVING COUNT(book.author_id) > 3
LIMIT 5
""")
result = cursor.fetchall()
print("\nAuthors with more than 3 books:")
for row in result:
    print(row)


con.commit()
con.close()
