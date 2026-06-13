import os
import libsql_experimental as libsql


def get_conn():
    TURSO_DB_URL = os.getenv("TURSO_DB_URL")
    TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        raise ValueError("Missing TURSO_DB_URL or TURSO_AUTH_TOKEN in .env")
    return libsql.connect(TURSO_DB_URL, auth_token=TURSO_AUTH_TOKEN)


def fetch_all(sql: str, params: tuple = ()) -> list:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_one(sql: str, params: tuple = ()) -> tuple | None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    conn.close()
    return row