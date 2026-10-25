# For: SQLite database connection management and transaction lifecycle
# Must never: Leave connections open or disable foreign key enforcement

import sqlite3
from contextlib import contextmanager
from typing import Generator
from engine.app.core.config import settings


def get_raw_connection() -> sqlite3.Connection:
    """Creates a raw SQLite connection with foreign keys and Row factory enabled."""
    conn = sqlite3.connect(
        str(settings.db_path),
        timeout=30.0,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite database transactions."""
    conn = get_raw_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
