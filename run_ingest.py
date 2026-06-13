import subprocess
import sys
import time
from datetime import datetime

RETRY_WAIT = 30  # seconds to wait after a failure before restarting

attempt = 1
while True:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{ts}] --- Attempt {attempt} ---", flush=True)
    result = subprocess.run([sys.executable, "ingest.py"])

    if result.returncode == 0:
        print("All puzzles loaded successfully.")
        break

    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] ingest.py exited with code {result.returncode}. Retrying in {RETRY_WAIT}s...", flush=True)
    time.sleep(RETRY_WAIT)
    attempt += 1
