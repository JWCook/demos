#!/usr/bin/env python
# Example FTS search TUI with live update
import asyncio
import sqlite3
from typing import Optional

from textual.app import App
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Input, Markdown

DB_PATH = 'demo.db'
FTS_TABLE = 'pkg_fts'
MAX_RESULTS = 50


class SearchResults(Markdown):
    results = reactive([])

    def __init__(self):
        super().__init__('')
        self.markup = True
        self.count = 0

    def watch_results(self, results: list[str]):
        if results:
            self.update('\n * '.join([f'{self.count} results'] + results))
        else:
            self.update('No results')


class SearchApp(App):
    def __init__(self):
        super().__init__()

        self._search_task: Optional[asyncio.Task] = None
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def compose(self):
        yield Container(
            Input(placeholder='Type to search...'),
            SearchResults(),
        )

    def on_input_changed(self, event: Input.Changed):
        """Handle input changes; delay running query until typing stops for 200ms"""
        # Non-delayed version:
        # self.autocomplete(event.value)

        async def _delayed_search(query: str):
            await asyncio.sleep(0.2)
            self.autocomplete(query)

        if self._search_task and not self._search_task.done():
            self._search_task.cancel()
        if event.value:
            self._search_task = asyncio.create_task(_delayed_search(event.value))
        else:
            self.query_one(SearchResults).results = []

    def autocomplete(self, query: str):
        results_widget = self.query_one(SearchResults)
        try:
            query += '*'

            # Run count query separately to avoid fetching all results
            count_result = self.cursor.execute(
                f'SELECT COUNT(*) FROM {FTS_TABLE} WHERE name MATCH ?', (query,)
            ).fetchall()
            results_widget.count = count_result[0][0]

            results = self.cursor.execute(
                f'SELECT * FROM {FTS_TABLE} WHERE name MATCH ? LIMIT ?', (query, MAX_RESULTS)
            ).fetchall()
            results_widget.results = [f'**{row[0]}** - {row[1]}' for row in results]
        except Exception as e:
            results_widget.update(f'Error: {e}')


if __name__ == '__main__':
    SearchApp().run()
