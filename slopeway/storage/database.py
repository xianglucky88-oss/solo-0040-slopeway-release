import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

SCHEMA = Path(__file__).with_name('schema.sql')


class Database:
    def __init__(self, path):
        self.path = Path(path)

    def _connect(self):
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys = ON')
        return connection

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            connection.execute('PRAGMA journal_mode = WAL')
            connection.executescript(SCHEMA.read_text(encoding='utf-8'))

    @contextmanager
    def transaction(self, *, write=False):
        connection = self._connect()
        try:
            connection.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()
