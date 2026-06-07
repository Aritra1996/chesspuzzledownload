from core.db import fetch_all, fetch_one


def fetch_unique_themes() -> list[str]:
    """Pull every Themes string, split on spaces, return sorted unique tokens."""
    sql="SELECT Themes FROM puzzles WHERE Themes != ''"
    rows = fetch_all(sql)
    seen: set[str] = set()
    for (theme_str,) in rows:
        seen.update(theme_str.split())
    return sorted(seen)
 
 
def fetch_rating_bounds() -> tuple[int, int]:
    sql = "SELECT MIN(Rating), MAX(Rating) FROM puzzles"
    lo, hi = fetch_one(sql)
    return (lo or 0, hi or 3000)
 
 
def query_puzzles(theme: str, min_r: int, max_r: int, limit: int = 24) -> list:
    """Shared query used by both the display route and PDF download routes."""
    sql = """
        SELECT PuzzleId, FEN, Moves, Rating, Themes, OpeningTags
        FROM puzzles
        WHERE Rating BETWEEN ? AND ?
    """
    params: list = [min_r, max_r]
    if theme:
        sql += " AND instr(' ' || Themes || ' ', ' ' || ? || ' ') > 0"
        params.append(theme)
    sql += " ORDER BY Rating LIMIT ?"
    params.append(limit)
    rows = fetch_all(sql, tuple(params))   # libsql_experimental requires a tuple
    return rows