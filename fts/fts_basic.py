#!/usr/bin/env python
# Example FTS search using sqlite3 from python stdlib
import sqlite3
from time import perf_counter as time

connection = sqlite3.connect('demo.db')
while True:
    query = input('Search query: ')
    start = time()
    results = connection.execute(
        'SELECT name, desc FROM pkg_fts WHERE name MATCH ?', (query,)
    ).fetchall()
    elapsed = time() - start
    for row in results:
        print(f'{row[0]} - {row[1]}')
    print(f'{len(results)} results in {elapsed:.4f}s')
