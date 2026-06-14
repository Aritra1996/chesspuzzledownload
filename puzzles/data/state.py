from core.sqlite import fetch_all, fetch_one

ALL_THEMES   = sorted(r[0] for r in fetch_all("SELECT name FROM state_themes"))
ALL_OPENINGS = sorted(r[0] for r in fetch_all("SELECT name FROM state_openings"))
_bounds      = fetch_one("SELECT min_rating, max_rating FROM state_rating_bounds")
RATING_MIN, RATING_MAX = (_bounds[0] or 0), (_bounds[1] or 3000)
