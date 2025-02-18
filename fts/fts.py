#!/usr/bin/env python
import sqlite3

connection = sqlite3.connect('demo.db')
query = input('Search query: ')
results = connection.execute(
    'SELECT name, desc FROM pkg_fts WHERE name MATCH ?', (query,)
).fetchall()
for row in results:
    print(f'{row[0]} - {row[1]}')
