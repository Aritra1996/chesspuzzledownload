from puzzles.db import fetch_rating_bounds, fetch_total_puzzles, fetch_unique_themes


ALL_THEMES: list[str] = fetch_unique_themes()
RATING_MIN, RATING_MAX = fetch_rating_bounds()
TOTAL_PUZZLES: int = fetch_total_puzzles()