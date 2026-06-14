"""
Add rating column to puzzle_themes and puzzle_openings, and create composite
indexes (theme, rating) and (opening, rating) for O(log N) bucket queries.

Idempotent: ALTER TABLE is wrapped in try/except; CREATE INDEX uses IF NOT EXISTS.
Runs against Turso first, then local.db.
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import libsql_experimental as libsql  # type: ignore

TURSO_DB_URL     = os.getenv("TURSO_DB_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
    raise ValueError("Missing TURSO_DB_URL or TURSO_AUTH_TOKEN in .env")

LOCAL_DB = os.path.join(os.path.dirname(__file__), "..", "local.db")


def _migrate(cur, commit_fn, label: str):
    for table, col_index in [("puzzle_themes", "idx_pt_theme_rating"),
                              ("puzzle_openings", "idx_po_opening_rating")]:
        tag_col = "theme" if table == "puzzle_themes" else "opening"

        print(f"[{label}] ALTER {table} ADD COLUMN rating ...")
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN rating INTEGER")
            commit_fn()
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print(f"[{label}]   already exists, skipping ALTER")
            else:
                raise

        print(f"[{label}] UPDATE {table} SET rating = puzzles.Rating ...")
        cur.execute(f"""
            UPDATE {table}
            SET rating = (SELECT Rating FROM puzzles WHERE PuzzleId = {table}.puzzle_id)
        """)
        commit_fn()

        print(f"[{label}] CREATE INDEX {col_index} ...")
        cur.execute(f"""
            CREATE INDEX IF NOT EXISTS {col_index}
            ON {table} ({tag_col}, rating)
        """)
        commit_fn()

        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE rating IS NOT NULL")
        (n,) = cur.fetchone()
        print(f"[{label}]   {n:,} rows now have rating")


# ── Turso ──────────────────────────────────────────────────────────────────
print("=== Turso ===")
tconn = libsql.connect(TURSO_DB_URL, auth_token=TURSO_AUTH_TOKEN)
tcur  = tconn.cursor()
_migrate(tcur, tconn.commit, "turso")
tconn.close()

# ── local.db ───────────────────────────────────────────────────────────────
print("\n=== local.db ===")
lconn = sqlite3.connect(LOCAL_DB)
lcur  = lconn.cursor()
_migrate(lcur, lconn.commit, "local")
lconn.close()

print("\nDone.")
