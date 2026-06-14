import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from core.turso import fetch_all as turso_all, fetch_one as turso_one

DB = os.path.join(os.path.dirname(__file__), "..", "local.db")
BATCH = 5_000

conn = sqlite3.connect(DB)
conn.execute("CREATE TABLE IF NOT EXISTS state_themes (name TEXT PRIMARY KEY)")
conn.execute("CREATE TABLE IF NOT EXISTS state_openings (name TEXT PRIMARY KEY)")
conn.execute("CREATE TABLE IF NOT EXISTS state_rating_bounds (min_rating INTEGER, max_rating INTEGER)")
conn.execute("""
    CREATE TABLE IF NOT EXISTS puzzles (
        PuzzleId    TEXT PRIMARY KEY,
        FEN         TEXT,
        Moves       TEXT,
        Rating      INTEGER,
        Themes      TEXT,
        OpeningTags TEXT
    )
""")


def _collect_tokens(column: str) -> list[str]:
    """Scan all puzzles in batches, splitting the given column into unique tokens."""
    seen: set[str] = set()
    offset = 0
    while True:
        rows = turso_all(
            f"SELECT {column} FROM puzzles WHERE {column} != '' LIMIT ? OFFSET ?",
            (BATCH, offset),
        )
        if not rows:
            break
        for (val,) in rows:
            seen.update(val.split())
        offset += BATCH
        print(f"  {offset} rows scanned...", end="\r")
    print()
    return sorted(seen)


print("Syncing themes (batched)...")
themes = _collect_tokens("Themes")
conn.execute("DELETE FROM state_themes")
conn.executemany("INSERT INTO state_themes VALUES (?)", [(t,) for t in themes])

print("Syncing openings (batched)...")
openings = _collect_tokens("OpeningTags")
conn.execute("DELETE FROM state_openings")
conn.executemany("INSERT INTO state_openings VALUES (?)", [(o,) for o in openings])

print("Syncing rating bounds...")
lo, hi = turso_one("SELECT MIN(Rating), MAX(Rating) FROM puzzles")
conn.execute("DELETE FROM state_rating_bounds")
conn.execute("INSERT INTO state_rating_bounds VALUES (?, ?)", (lo or 0, hi or 3000))

print("Syncing 1000 sample puzzles...")
rows = turso_all(
    "SELECT PuzzleId, FEN, Moves, Rating, Themes, OpeningTags FROM puzzles ORDER BY Rating LIMIT 1000"
)
conn.execute("DELETE FROM puzzles")
conn.executemany("INSERT INTO puzzles VALUES (?,?,?,?,?,?)", rows)

conn.commit()
conn.close()
print(f"Done — {len(themes)} themes, {len(openings)} openings, {len(rows)} puzzles → local.db")
