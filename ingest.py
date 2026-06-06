from dotenv import load_dotenv
import os


from datasets import load_dataset
import libsql_experimental as libsql # type: ignore


load_dotenv()  # reads .env into environment variables

TURSO_DB_URL     = os.getenv("TURSO_DB_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

# Safety check — fail loudly if credentials are missing
if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
    raise ValueError("Missing TURSO_DB_URL or TURSO_AUTH_TOKEN in .env file")

# ✅ FIX: HF dataset returns Moves/Themes/OpeningTags as List[str], not str
def to_str(val):
    if isinstance(val, list):
        return " ".join(val)
    return val or ""

print("🔌 Connecting to Turso...")
conn   = libsql.connect(TURSO_DB_URL, auth_token=TURSO_AUTH_TOKEN)
cursor = conn.cursor()

print("🛠️ Creating table and indexes...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS puzzles (
        PuzzleId    TEXT PRIMARY KEY,
        FEN         TEXT,
        Moves       TEXT,
        Rating      INTEGER,
        Themes      TEXT,
        OpeningTags TEXT
    )
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_rating ON puzzles (Rating)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_themes ON puzzles (Themes)")
conn.commit()

print("🔄 Loading dataset (streaming)...")
ds = load_dataset("Lichess/chess-puzzles", split="train", streaming=True)

batch      = []
TEST_LIMIT = 1000

UPSERT_SQL = """
    INSERT OR REPLACE INTO puzzles (PuzzleId, FEN, Moves, Rating, Themes, OpeningTags)
    VALUES (?, ?, ?, ?, ?, ?)
"""

print(f"🚀 Pushing {TEST_LIMIT} test rows to Turso...")
for i, row in enumerate(ds):
    if i >= TEST_LIMIT:
        break

    batch.append((
        to_str(row["PuzzleId"]),
        to_str(row["FEN"]),
        to_str(row["Moves"]),        # ✅ ["e2e4", "d7d5"] → "e2e4 d7d5"
        int(row["Rating"]),
        to_str(row["Themes"]),       # ✅ ["fork", "mate"] → "fork mate"
        to_str(row["OpeningTags"]),  # ✅ [] → ""
    ))

    if len(batch) == 500:
        cursor.executemany(UPSERT_SQL, batch)
        conn.commit()
        print(f"✅ Inserted {i + 1} rows...")
        batch = []

if batch:
    cursor.executemany(UPSERT_SQL, batch)
    conn.commit()

conn.close()
print("🎉 Test ingestion complete!")
os._exit(0)   # ✅ hard exit — skips Python's GC/shutdown, kills dangling threads cleanly
