from puzzles.db import fetch_rating_bounds, fetch_unique_themes


ALL_THEMES: list[str] = fetch_unique_themes()
RATING_MIN, RATING_MAX = fetch_rating_bounds()