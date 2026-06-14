from constants import PUZZLE_CAP as CAP, RATING_DEFAULT_MIN, RATING_DEFAULT_MAX
from core.turso import fetch_all, fetch_one


def fetch_unique_themes() -> list[str]:
    """Pull every Themes string, split on spaces, return sorted unique tokens."""
    sql="SELECT Themes FROM puzzles WHERE Themes != ''"
    rows = fetch_all(sql)
    seen: set[str] = set()
    for (theme_str,) in rows:
        seen.update(theme_str.split())
    return sorted(seen)
 
 
def fetch_unique_openings() -> list[str]:
    sql = "SELECT OpeningTags FROM puzzles WHERE OpeningTags != ''"
    rows = fetch_all(sql)
    seen: set[str] = set()
    for (tag_str,) in rows:
        seen.update(tag_str.split())
    return sorted(seen)


def fetch_rating_bounds() -> tuple[int, int]:
    sql = "SELECT MIN(Rating), MAX(Rating) FROM puzzles"
    lo, hi = fetch_one(sql)
    return (lo or RATING_DEFAULT_MIN, hi or RATING_DEFAULT_MAX)
 
 
def count_puzzles(theme: str, opening: str, min_r: int, max_r: int) -> int:
    if theme and opening:
        sql = """SELECT COUNT(*) FROM puzzles p
                 JOIN puzzle_themes pt ON p.PuzzleId = pt.puzzle_id
                 JOIN puzzle_openings po ON p.PuzzleId = po.puzzle_id
                 WHERE pt.theme = ? AND po.opening = ?
                 AND p.Rating BETWEEN ? AND ?"""
        params = (theme, opening, min_r, max_r)
    elif theme:
        sql = """SELECT COUNT(*) FROM puzzles p
                 JOIN puzzle_themes pt ON p.PuzzleId = pt.puzzle_id
                 WHERE pt.theme = ? AND p.Rating BETWEEN ? AND ?"""
        params = (theme, min_r, max_r)
    elif opening:
        sql = """SELECT COUNT(*) FROM puzzles p
                 JOIN puzzle_openings po ON p.PuzzleId = po.puzzle_id
                 WHERE po.opening = ? AND p.Rating BETWEEN ? AND ?"""
        params = (opening, min_r, max_r)
    else:
        sql = "SELECT COUNT(*) FROM puzzles WHERE Rating BETWEEN ? AND ?"
        params = (min_r, max_r)
    (count,) = fetch_one(sql, params)
    return count


def query_puzzles(theme: str, opening: str, min_r: int, max_r: int,
                  limit: int | None = None, offset: int = 0) -> list:
    select = "SELECT p.PuzzleId, p.FEN, p.Moves, p.Rating, p.Themes, p.OpeningTags FROM puzzles p"
    order  = " ORDER BY p.Rating"
    page   = " LIMIT ? OFFSET ?" if limit is not None else ""

    if theme and opening:
        sql = (select
               + " JOIN puzzle_themes pt ON p.PuzzleId = pt.puzzle_id"
               + " JOIN puzzle_openings po ON p.PuzzleId = po.puzzle_id"
               + " WHERE pt.theme = ? AND po.opening = ? AND p.Rating BETWEEN ? AND ?"
               + order + page)
        params: list = [theme, opening, min_r, max_r]
    elif theme:
        sql = (select
               + " JOIN puzzle_themes pt ON p.PuzzleId = pt.puzzle_id"
               + " WHERE pt.theme = ? AND p.Rating BETWEEN ? AND ?"
               + order + page)
        params = [theme, min_r, max_r]
    elif opening:
        sql = (select
               + " JOIN puzzle_openings po ON p.PuzzleId = po.puzzle_id"
               + " WHERE po.opening = ? AND p.Rating BETWEEN ? AND ?"
               + order + page)
        params = [opening, min_r, max_r]
    else:
        sql = ("SELECT PuzzleId, FEN, Moves, Rating, Themes, OpeningTags FROM puzzles"
               + " WHERE Rating BETWEEN ? AND ?" + order + page)
        params = [min_r, max_r]

    if limit is not None:
        params += [limit, offset]
    return fetch_all(sql, tuple(params))