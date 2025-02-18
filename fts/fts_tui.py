#!/usr/bin/env python
import asyncio
import sqlite3
from typing import Optional

from textual.app import App
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Input, Markdown

MAX_RESULTS = 50


class SearchResults(Markdown):
    results = reactive([])

    def __init__(self):
        super().__init__('')
        self.markup = True

    def watch_results(self, results: list[str]):
        if results:
            self.update('\n * '.join([f'{len(results)} results'] + results[:MAX_RESULTS]))
        else:
            self.update('No results')


class SearchApp(App):
    def __init__(self):
        super().__init__()
        self._search_task: Optional[asyncio.Task] = None
        self.conn = sqlite3.connect('demo.db')

    def compose(self):
        yield Container(
            Input(placeholder='Type to search...'),
            SearchResults(),
        )

    def on_input_changed(self, event: Input.Changed):
        """Handle input changes; delay running query until typing stops for 200ms"""

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
        try:
            query += '*'
            results = self.conn.execute(
                'SELECT name, desc FROM pkg_fts WHERE name MATCH ?', (query,)
            ).fetchall()
            self.query_one(SearchResults).results = [f'**{row[0]}** - {row[1]}' for row in results]
        except Exception as e:
            self.query_one(SearchResults).update(f'Error: {e}')


if __name__ == '__main__':
    SearchApp().run()
