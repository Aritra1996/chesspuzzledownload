from dotenv import load_dotenv
import json
import os


from datasets import load_dataset
import libsql_experimental as libsql # type: ignore


load_dotenv()  # reads .env into environment variables

TURSO_DB_URL     = os.getenv("TURSO_DB_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
HF_TOKEN         = os.getenv("HF_TOKEN")

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
cursor.execute("""
    CREATE TABLE IF NOT EXISTS puzzle_themes (
        puzzle_id TEXT NOT NULL,
        theme     TEXT NOT NULL,
        PRIMARY KEY (puzzle_id, theme)
    )
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_pt_theme ON puzzle_themes (theme)")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS puzzle_openings (
        puzzle_id TEXT NOT NULL,
        opening   TEXT NOT NULL,
        PRIMARY KEY (puzzle_id, opening)
    )
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_opening ON puzzle_openings (opening)")
conn.commit()

PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingest_progress.json")
resume_offset = 0
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE) as f:
        resume_offset = json.load(f).get("offset", 0)
if resume_offset:
    print(f"▶️  Resuming from offset {resume_offset}...")

print("🔄 Loading dataset (streaming)...")
ds = load_dataset("Lichess/chess-puzzles", split="train", streaming=True, token=HF_TOKEN)
if resume_offset:
    ds = ds.skip(resume_offset)

batch = []
count = resume_offset

UPSERT_SQL = """
    INSERT OR REPLACE INTO puzzles (PuzzleId, FEN, Moves, Rating, Themes, OpeningTags)
    VALUES (?, ?, ?, ?, ?, ?)
"""
THEME_SQL   = "INSERT OR IGNORE INTO puzzle_themes (puzzle_id, theme) VALUES (?, ?)"
OPENING_SQL = "INSERT OR IGNORE INTO puzzle_openings (puzzle_id, opening) VALUES (?, ?)"

print("🚀 Pushing all puzzles to Turso...")
for row in ds:
    batch.append((
        to_str(row["PuzzleId"]),
        to_str(row["FEN"]),
        to_str(row["Moves"]),
        int(row["Rating"]),
        to_str(row["Themes"]),
        to_str(row["OpeningTags"]),
    ))
    count += 1

    if len(batch) == 500:
        cursor.executemany(UPSERT_SQL, batch)
        theme_rows   = [(r[0], t) for r in batch if r[4] for t in r[4].split()]
        opening_rows = [(r[0], o) for r in batch if r[5] for o in r[5].split()]
        if theme_rows:
            cursor.executemany(THEME_SQL, theme_rows)
        if opening_rows:
            cursor.executemany(OPENING_SQL, opening_rows)
        conn.commit()
        with open(PROGRESS_FILE, "w") as f:
            json.dump({"offset": count}, f)
        print(f"✅ Inserted {count} rows...")
        batch = []

if batch:
    cursor.executemany(UPSERT_SQL, batch)
    theme_rows   = [(r[0], t) for r in batch if r[4] for t in r[4].split()]
    opening_rows = [(r[0], o) for r in batch if r[5] for o in r[5].split()]
    if theme_rows:
        cursor.executemany(THEME_SQL, theme_rows)
    if opening_rows:
        cursor.executemany(OPENING_SQL, opening_rows)
    conn.commit()

conn.close()
if os.path.exists(PROGRESS_FILE):
    os.remove(PROGRESS_FILE)
print("🎉 Ingestion complete!")
os._exit(0)   # hard exit — skips Python's GC/shutdown, kills dangling threads cleanly
