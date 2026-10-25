# For: User authentication, role retrieval, and credential lockout management
# Must never: Return password hashes or bypass account lockout limits

import sqlite3
import uuid
from datetime import datetime, timezone
from engine.app.core.security import verify_password, hash_password


def get_user_by_username(conn: sqlite3.Connection, username: str) -> dict | None:
    """Retrieves user record by username."""
    cursor = conn.execute(
        "SELECT id, username, full_name, password_hash, role, is_active, failed_logins, locked_until, created_at, last_login_at "
        "FROM users WHERE username = ?;",
        (username,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def get_user_by_id(conn: sqlite3.Connection, user_id: str) -> dict | None:
    """Retrieves user profile by primary key id."""
    cursor = conn.execute(
        "SELECT id, username, full_name, role, is_active, created_at, last_login_at "
        "FROM users WHERE id = ?;",
        (user_id,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def list_users(conn: sqlite3.Connection) -> list[dict]:
    """Lists all users without exposing password hashes."""
    cursor = conn.execute(
        "SELECT id, username, full_name, role, is_active, failed_logins, created_at, last_login_at "
        "FROM users ORDER BY created_at DESC;"
    )
    return [dict(r) for r in cursor.fetchall()]


def record_successful_login(conn: sqlite3.Connection, user_id: str) -> None:
    """Resets failed attempts and updates last_login_at timestamp."""
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE users SET failed_logins = 0, locked_until = NULL, last_login_at = ? WHERE id = ?;",
        (now, user_id)
    )


def record_failed_login(conn: sqlite3.Connection, username: str) -> int:
    """Increments failed logins and locks account for 15 minutes after 5 failures."""
    user = get_user_by_username(conn, username)
    if not user:
        return 0
    new_fails = user["failed_logins"] + 1
    locked_until = None
    if new_fails >= 5:
        now = datetime.now(timezone.utc).timestamp()
        locked_until = datetime.fromtimestamp(now + 900, timezone.utc).isoformat()
    conn.execute(
        "UPDATE users SET failed_logins = ?, locked_until = ? WHERE id = ?;",
        (new_fails, locked_until, user["id"])
    )
    return new_fails


def create_user(conn: sqlite3.Connection, data: dict) -> dict:
    """Creates a new user record with hashed credentials."""
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    p_hash = hash_password(data["password"])
    conn.execute(
        "INSERT INTO users (id, username, full_name, password_hash, role, is_active, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?);",
        (user_id, data["username"], data["full_name"], p_hash, data["role"], 1, now)
    )
    return get_user_by_id(conn, user_id) or {}
