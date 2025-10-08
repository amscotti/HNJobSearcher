import sqlite3
from sqlite3 import Connection
from typing import TypeAlias, Self
from datetime import datetime, timedelta

from hackerjobs.Posting import Posting

ResultList: TypeAlias = list[Posting]


class JobPostingIndex:
    def __init__(self, index_file: str):
        self.index_file = index_file
        self.conn: Connection | None = None

    def connect(self) -> Self:
        self.conn = sqlite3.connect(self.index_file)
        return self

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self) -> Self:
        return self.connect()

    def __exit__(
        self, exc_type: type | None, exc_val: Exception | None, exc_tb: object | None
    ) -> None:
        self.close()

    def table_exists(self) -> bool:
        assert self.conn is not None
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='postings'"
        )
        result = cursor.fetchone()
        return result is not None

    def initialize(self) -> None:
        """Initialize database schema - only creates if tables don't exist"""
        assert self.conn is not None

        # Check if we already have the enhanced schema
        if self._has_enhanced_schema():
            return  # Schema is already up to date

        # Create main postings table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS postings (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                by TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create FTS virtual table for search
        self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS postings_fts USING fts5(
                id, text, by,
                content=postings,
                content_rowid=rowid
            )
        """)

        # Create triggers to keep FTS in sync
        self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS postings_fts_insert
            AFTER INSERT ON postings BEGIN
                INSERT INTO postings_fts(rowid, id, text, by)
                VALUES (new.rowid, new.id, new.text, new.by);
            END
        """)

        self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS postings_fts_delete
            AFTER DELETE ON postings BEGIN
                DELETE FROM postings_fts WHERE rowid = old.rowid;
            END
        """)

        self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS postings_fts_update
            AFTER UPDATE ON postings BEGIN
                UPDATE postings_fts SET id = new.id, text = new.text,
                by = new.by WHERE rowid = new.rowid;
            END
        """)

        # Create indexes for performance
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_postings_timestamp ON postings(timestamp)"
        )
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_postings_by ON postings(by)")
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_postings_created_at ON postings(created_at)"
        )

        self.conn.commit()

    def _has_enhanced_schema(self) -> bool:
        """Check if we have the enhanced schema with timestamp column"""
        assert self.conn is not None

        # Check if postings table exists
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='postings'"
        )
        if not cursor.fetchone():
            return False

        # Check if timestamp column exists
        cursor = self.conn.execute("PRAGMA table_info(postings)")
        columns = [row[1] for row in cursor.fetchall()]
        return "timestamp" in columns

    def drop_table(self) -> None:
        """Drop all tables - use with caution as this deletes all data"""
        assert self.conn is not None
        # Drop FTS table first (due to triggers)
        self.conn.execute("DROP TABLE IF EXISTS postings_fts")
        self.conn.execute("DROP TABLE IF EXISTS postings")
        self.conn.commit()

    def index_postings(self, postings: list[Posting]) -> None:
        assert self.conn is not None

        valid_postings = [job for job in postings if job]

        sql = (
            "INSERT OR REPLACE INTO postings "
            "(id, text, by, timestamp) VALUES (?, ?, ?, ?)"
        )
        self.conn.executemany(
            sql,
            ((job.id, job.text, job.by, job.timestamp) for job in valid_postings),
        )

        self.conn.commit()

    def search(
        self,
        query_text: str,
        days: int = 30,
        limit: int = 100,
        sort_by_time: bool = True,
    ) -> ResultList:
        """Enhanced search with date filtering and time sorting"""
        assert self.conn is not None

        # Calculate timestamp cutoff
        cutoff_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())

        # Build query with date filtering and sorting
        if sort_by_time:
            order_by = "ORDER BY p.timestamp DESC"
        else:
            order_by = ""

        query = f"""
        SELECT p.id, p.text, p.by, p.timestamp FROM postings p
        JOIN postings_fts fts ON p.rowid = fts.rowid
        WHERE fts.text MATCH ? AND p.timestamp >= ? {order_by} LIMIT ?
        """

        cursor = self.conn.execute(query, (query_text, cutoff_timestamp, limit))
        results = cursor.fetchall()

        return [
            Posting(id=result[0], text=result[1], by=result[2], timestamp=result[3])
            for result in results
        ]
