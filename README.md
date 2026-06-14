# Chess Puzzle Download

Browse, filter, and download [Lichess](https://lichess.org/) chess puzzles as PDFs.

**Live:** https://chesspuzzledownload.vercel.app/

---

## Features

- Filter 400k+ puzzles by **theme**, **opening**, and **rating range**
- Paginated puzzle browser with FEN board previews
- Download filtered puzzles as a **PDF** (boards + solutions on separate pages)
- Fast cold starts — filter metadata loads from a bundled SQLite file, not the cloud DB

---

## Tech stack

| Layer | Tool |
|---|---|
| Web framework | [FastHTML](https://fastht.ml/) |
| Cloud database | [Turso](https://turso.tech/) (libsql) |
| Local cache | SQLite (`local.db`, bundled in git) |
| PDF generation | [fpdf2](https://py-pdf.github.io/fpdf2/) |
| Chess logic | [python-chess](https://python-chess.readthedocs.io/) |
| Puzzle dataset | [Lichess/chess-puzzles](https://huggingface.co/datasets/Lichess/chess-puzzles) on HuggingFace |
| Hosting | [Vercel](https://vercel.com/) (Python serverless) |

---

## Project structure

```
.
├── api/
│   └── index.py          # Vercel entry point + local dev server
├── app.py                # FastHTML app/rt instances (circular-import firewall)
├── core/
│   ├── turso.py          # Turso/libsql connection layer (cloud DB)
│   └── sqlite.py         # SQLite connection layer (local cache)
├── puzzles/
│   ├── data/
│   │   ├── queries.py    # SQL queries against Turso (full 400k puzzle set)
│   │   └── state.py      # Module-level constants loaded from local.db at startup
│   ├── pdf/
│   │   ├── generate.py   # PDF generation (puzzles + solutions)
│   │   └── constants.py  # PDF layout constants
│   ├── chess.py          # FEN/UCI helpers via python-chess
│   ├── routes.py         # Route handlers (/puzzles, /puzzles/download/*)
│   ├── validators.py     # Input sanitisation
│   └── views.py          # HTML component builders
├── scripts/
│   ├── ingest.py         # HuggingFace → Turso ingestion (one-time / resumable)
│   ├── run_ingest.py     # Retry wrapper for ingest.py
│   └── sync_local.py     # Turso → local.db sync (run after new ingestion)
├── static/               # CSS
├── local.db              # Bundled SQLite cache (themes, openings, rating bounds, 1000 sample puzzles)
├── vercel.json           # Vercel routing config
└── requirements.txt      # Vercel runtime dependencies
```

---

## Local development

### Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
git clone <repo-url>
cd chesspuzzledownload

# Create virtualenv and install all dependencies
uv sync

# Copy the example env file and fill in real values
cp .env.example .env
```

### Run

```bash
uv run python api/index.py
```

The server starts at http://localhost:5001. `local.db` is already committed, so the filter dropdowns and rating range load instantly without hitting Turso. The app browses a 1000-puzzle sample locally; the full 400k+ set is only available through the deployed Turso DB.

---

## Environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```
TURSO_DB_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=your-auth-token

# Only needed when running scripts/ingest.py
HF_TOKEN=your-huggingface-token
```

`TURSO_DB_URL` and `TURSO_AUTH_TOKEN` are required at runtime (puzzle queries hit Turso). `HF_TOKEN` is only needed when running `scripts/ingest.py`.

---

## Ingesting puzzles (one-time setup)

Loads the full Lichess puzzle dataset from HuggingFace into Turso. The script resumes from the last successful batch if interrupted.

```bash
uv run python scripts/run_ingest.py
```

Progress is tracked in `scripts/ingest_progress.json` (git-ignored). The file is deleted automatically on completion.

---

## Syncing the local cache

After ingestion (or when Turso data changes), regenerate `local.db` and commit it:

```bash
uv run python scripts/sync_local.py
git add local.db
git commit -m "Sync local.db"
```

This re-scans all 400k+ Turso puzzles (in 5000-row batches) to extract unique themes, openings, and rating bounds, then writes them plus 1000 sample puzzles into `local.db`. Takes a few minutes.

---

## Deployment

The project deploys to Vercel automatically on push to `main`, or manually:

```bash
vercel --prod
```

`vercel.json` routes all requests to `api/index.py`. No build step required — Vercel runs the Python function directly.
