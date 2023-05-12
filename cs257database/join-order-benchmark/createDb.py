"""
Filename: createDb.py
Author: Phuoc Le
Description: This script creates test database for CS257 project
"""
import sys
import csv
import sqlite3
from sqlite3 import Error

# Part 1: loading database
INSERT_QUERY = "INSERT INTO {} {} VALUES{}"
SELECT_ALL = "SELECT * from {}"

maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

connection = sqlite3.connect('test_database.db')
# connection = sqlite3.connect('backup_database.db')

cur = connection.cursor()

try:
    with open('schema.sql') as f:
        connection.executescript(f.read())
    with open('fkindexes.sql') as f_index:
        connection.executescript(f_index.read())
except Error as e:
    print(e)


def load_table(table_name, fields):
    print("Loading data for '{}' table...".format(table_name))
    table = open("imdb/{}.csv".format(table_name), errors='ignore')
    contents = csv.reader(table)
    scanned_content = []
    for row in contents:
        if len(row) == len(fields):
            scanned_content.append(row)
    columns = '(' + ", ".join(fields) + ')'
    values = '(' + ", ".join(['?' for i in range(0, len(fields))]) + ')'
    insert_records = INSERT_QUERY.format(table_name, columns, values)
    cur.executemany(insert_records, scanned_content)
    print("Loading completed!")


sql_query = """SELECT name FROM sqlite_master
    WHERE type='table';"""

tables = cur.execute(sql_query).fetchall()
print("List of tables")
for table in tables:
    table_name = table[0]
    data = cur.execute(SELECT_ALL.format(table_name))
    rows = data.fetchall()
    if rows:
        print(table_name, "table already loaded data, number of rows =", len(rows))
        print("First row: ", rows[0])
    else:
        columns_names = []
        for description in data.description:
            columns_names.append(description[0])
        print(columns_names)
        load_table(table_name, columns_names)


# Committing the changes
connection.commit()

# closing the database connection
connection.close()
