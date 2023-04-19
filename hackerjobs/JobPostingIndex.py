import sqlite3
from sqlite3 import Connection
from typing import TypeAlias

from hackerjobs.Posting import Posting

ResultList: TypeAlias = list[Posting]


class JobPostingIndex:
    def __init__(self, index_file: str):
        self.index_file = index_file
        self.conn: Connection | None = None

    def connect(self):
        self.conn = sqlite3.connect(self.index_file)
        return self

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def table_exists(self) -> bool:
        assert self.conn is not None
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='documents'"
        )
        result = cursor.fetchone()
        return result is not None

    def initialize(self) -> None:
        assert self.conn is not None
        self.conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(id, text, by)"
        )

    def drop_table(self) -> None:
        assert self.conn is not None
        self.conn.execute("DROP TABLE IF EXISTS documents")
        self.conn.commit()

    def index_postings(self, postings: list[Posting]) -> None:
        assert self.conn is not None

        valid_postings = [job for job in postings if job]

        self.conn.executemany(
            "INSERT INTO documents (id, text, by) VALUES (?, ?, ?)",
            ((job["id"], job["text"], job["by"]) for job in valid_postings)
        )

        self.conn.commit()

    def search(self, query_text: str, search_count: int) -> ResultList:
        assert self.conn is not None
        cursor = self.conn.execute(
            "SELECT id, text, by FROM documents WHERE text MATCH ? LIMIT ?",
            (query_text, search_count)
        )
        results = cursor.fetchall()

        return [
            {"id": result[0], "text": result[1], "by": result[2]} for result in results
        ]
