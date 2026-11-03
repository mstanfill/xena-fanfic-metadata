import pathlib
import sqlite3


class QueueDB:
    def __init__(self, db_path):
        self.db_path = pathlib.Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS queue (
                url TEXT PRIMARY KEY,
                host TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                last_attempt_at TEXT
            )
            """
        )
        self.conn.commit()

    def enqueue(self, url: str, host: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO queue (url, host, status) VALUES (?, ?, 'pending')",
            (url, host),
        )
        self.conn.commit()

    def get_status(self, url: str) -> str | None:
        row = self.conn.execute("SELECT status FROM queue WHERE url = ?", (url,)).fetchone()
        return row[0] if row else None

    def mark_fetched(self, url: str, when: str) -> None:
        self.conn.execute(
            "UPDATE queue SET status='fetched', last_attempt_at=? WHERE url=?", (when, url)
        )
        self.conn.commit()

    def mark_failed(self, url: str, error: str, when: str) -> None:
        self.conn.execute(
            "UPDATE queue SET status='failed', attempts=attempts+1, last_error=?, "
            "last_attempt_at=? WHERE url=?",
            (error, when, url),
        )
        self.conn.commit()

    def mark_skipped_by_robots(self, url: str, when: str) -> None:
        self.conn.execute(
            "UPDATE queue SET status='skipped_by_robots', last_attempt_at=? WHERE url=?",
            (when, url),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
