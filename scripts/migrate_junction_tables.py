"""
Additive-safe migration: populate puzzle_themes and puzzle_openings from the
existing puzzles table in Turso using server-side SQL (no Python-level batching).

Re-running is safe: INSERT OR IGNORE skips existing rows and picks up any
new puzzles added since the last run.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import libsql_experimental as libsql  # type: ignore

TURSO_DB_URL     = os.getenv("TURSO_DB_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
    raise ValueError("Missing TURSO_DB_URL or TURSO_AUTH_TOKEN in .env")

print("Connecting to Turso...")
conn = libsql.connect(TURSO_DB_URL, auth_token=TURSO_AUTH_TOKEN)
cur  = conn.cursor()

print("Creating junction tables...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS puzzle_themes (
        puzzle_id TEXT NOT NULL,
        theme     TEXT NOT NULL,
        PRIMARY KEY (puzzle_id, theme)
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_pt_theme ON puzzle_themes (theme)")
cur.execute("""
    CREATE TABLE IF NOT EXISTS puzzle_openings (
        puzzle_id TEXT NOT NULL,
        opening   TEXT NOT NULL,
        PRIMARY KEY (puzzle_id, opening)
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_po_opening ON puzzle_openings (opening)")
conn.commit()

# Use server-side INSERT...SELECT with json_each() to split space-separated
# strings into rows without fetching any data back to Python. libsql_experimental
# hangs on SELECT + fetchall() for remote connections; pure INSERT avoids that.
print("Populating puzzle_themes...")
cur.execute("""
    INSERT OR IGNORE INTO puzzle_themes (puzzle_id, theme)
    SELECT p.PuzzleId, j.value
    FROM puzzles p, json_each('["' || replace(trim(p.Themes), ' ', '","') || '"]') j
    WHERE p.Themes IS NOT NULL AND p.Themes != '' AND j.value != ''
""")
conn.commit()
cur.execute("SELECT COUNT(*) FROM puzzle_themes")
(theme_count,) = cur.fetchone()
print(f"puzzle_themes: {theme_count:,} rows")

print("Populating puzzle_openings...")
cur.execute("""
    INSERT OR IGNORE INTO puzzle_openings (puzzle_id, opening)
    SELECT p.PuzzleId, j.value
    FROM puzzles p, json_each('["' || replace(trim(p.OpeningTags), ' ', '","') || '"]') j
    WHERE p.OpeningTags IS NOT NULL AND p.OpeningTags != '' AND j.value != ''
""")
conn.commit()
cur.execute("SELECT COUNT(*) FROM puzzle_openings")
(opening_count,) = cur.fetchone()
print(f"puzzle_openings: {opening_count:,} rows")

conn.close()
print("Done.")
