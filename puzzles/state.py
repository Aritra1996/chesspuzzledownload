from puzzles.db import fetch_rating_bounds, fetch_unique_openings, fetch_unique_themes


ALL_THEMES:   list[str] = fetch_unique_themes()
ALL_OPENINGS: list[str] = fetch_unique_openings()
RATING_MIN, RATING_MAX = fetch_rating_bounds()