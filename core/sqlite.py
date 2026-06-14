import os
import sqlite3

_DB = os.path.join(os.path.dirname(__file__), "..", "local.db")


def fetch_all(sql: str, params: tuple = ()) -> list:
    conn = sqlite3.connect(_DB)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def fetch_one(sql: str, params: tuple = ()) -> tuple | None:
    conn = sqlite3.connect(_DB)
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return row
