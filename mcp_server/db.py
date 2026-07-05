"""
db.py — local persistence layer for the LifeFlow Concierge Agent.

Uses a local SQLite file so the whole project runs with zero external
services and zero API keys other than the Gemini key needed by the LLM.
This keeps the "concierge" data (habits, schedule, budget) private and
on-device, which matters for the Concierge Agents track's "keep personal
information safe and secure" requirement.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "lifeflow.db"


def init_db() -> None:
    """Create tables if they don't already exist. Safe to call every startup."""
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                logged_at TEXT NOT NULL DEFAULT (datetime('now')),
                note TEXT
            );

            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                category TEXT
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                logged_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def seed_demo_data() -> None:
    """Optional: populate a few rows so the demo video has something to show."""
    with get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]
        if count > 0:
            return
        conn.executemany(
            "INSERT INTO schedule (title, start_time, end_time, category) VALUES (?, ?, ?, ?)",
            [
                ("Morning workout", "07:00", "07:45", "health"),
                ("Deep work block", "09:00", "11:30", "work"),
                ("Team standup", "11:30", "11:45", "work"),
                ("Lunch", "12:30", "13:15", "personal"),
            ],
        )
        conn.executemany(
            "INSERT INTO expenses (label, amount, category) VALUES (?, ?, ?)",
            [
                ("Groceries", 62.40, "food"),
                ("Ride share", 18.00, "transport"),
                ("Coffee subscription", 12.00, "food"),
            ],
        )
        conn.commit()
