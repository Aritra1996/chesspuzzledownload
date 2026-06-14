from functools import lru_cache

from constants import RATING_DEFAULT_MIN, RATING_DEFAULT_MAX
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


def query_puzzles(theme: str, opening: str, min_r: int, max_r: int,
                  limit: int | None = None, offset: int = 0,
                  n_puzzles: int | None = None) -> list:
    if n_puzzles is not None:
        return _query_puzzles_sampled(theme, opening, min_r, max_r, n_puzzles)

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


_MAX_CTES = 30  # stay below Turso/libsql's compound-select limit

@lru_cache(maxsize=64)
def _query_puzzles_sampled(theme: str, opening: str, min_r: int, max_r: int,
                            n: int) -> list:
    n_ctes = min(n, _MAX_CTES)
    bucket_size = (max_r - min_r) // n_ctes
    if bucket_size == 0:
        # Range narrower than n_ctes: one bucket per distinct rating value.
        n_ctes = min(max_r - min_r + 1, n_ctes) or 1
        bucket_size = 1
    cte_defs: list[str] = []
    cte_refs: list[str] = []
    params: list = []
    for i in range(n_ctes):
        lo = min_r + i * bucket_size
        hi = (min_r + (i + 1) * bucket_size - 1) if i < n_ctes - 1 else max_r
        sel, p = _bucket_select(theme, opening, lo, hi)
        cte_defs.append(f"b{i} AS ({sel})")
        cte_refs.append(f"SELECT * FROM b{i}")
        params.extend(p)

    sql = ("WITH " + ", ".join(cte_defs) + "\n"
           + " UNION ALL ".join(cte_refs) + " ORDER BY Rating")
    results = fetch_all(sql, tuple(params))

    if len(results) < n:
        found_ids = tuple(r[0] for r in results)
        fill = _fill_up(theme, opening, min_r, max_r, n - len(results), found_ids)
        results = sorted(results + fill, key=lambda r: r[3])

    return results


def _bucket_select(theme: str, opening: str, lo: int, hi: int) -> tuple[str, tuple]:
    base = ("SELECT p.PuzzleId, p.FEN, p.Moves, p.Rating, p.Themes, p.OpeningTags"
            " FROM puzzles p")
    rating = f"p.Rating BETWEEN {lo} AND {hi}"
    order = " ORDER BY p.Rating LIMIT 1"
    if theme and opening:
        return (base
                + " JOIN puzzle_themes pt ON p.PuzzleId = pt.puzzle_id"
                + " JOIN puzzle_openings po ON p.PuzzleId = po.puzzle_id"
                + f" WHERE pt.theme = ? AND po.opening = ? AND {rating}" + order,
                (theme, opening))
    if theme:
        return (base
                + " JOIN puzzle_themes pt ON p.PuzzleId = pt.puzzle_id"
                + f" WHERE pt.theme = ? AND {rating}" + order,
                (theme,))
    if opening:
        return (base
                + " JOIN puzzle_openings po ON p.PuzzleId = po.puzzle_id"
                + f" WHERE po.opening = ? AND {rating}" + order,
                (opening,))
    return (f"SELECT PuzzleId, FEN, Moves, Rating, Themes, OpeningTags"
            f" FROM puzzles WHERE Rating BETWEEN {lo} AND {hi} ORDER BY Rating LIMIT 1",
            ())


def _fill_up(theme: str, opening: str, min_r: int, max_r: int,
             need: int, found_ids: tuple) -> list:
    not_in_p = (f" AND p.PuzzleId NOT IN ({','.join('?' * len(found_ids))})"
                if found_ids else "")
    not_in = (f" AND PuzzleId NOT IN ({','.join('?' * len(found_ids))})"
              if found_ids else "")
    base = ("SELECT p.PuzzleId, p.FEN, p.Moves, p.Rating, p.Themes, p.OpeningTags"
            " FROM puzzles p")
    tail = " ORDER BY p.Rating LIMIT ?"
    if theme and opening:
        sql = (base
               + " JOIN puzzle_themes pt ON p.PuzzleId = pt.puzzle_id"
               + " JOIN puzzle_openings po ON p.PuzzleId = po.puzzle_id"
               + " WHERE pt.theme = ? AND po.opening = ? AND p.Rating BETWEEN ? AND ?"
               + not_in_p + tail)
        return fetch_all(sql, (theme, opening, min_r, max_r) + found_ids + (need,))
    if theme:
        sql = (base
               + " JOIN puzzle_themes pt ON p.PuzzleId = pt.puzzle_id"
               + " WHERE pt.theme = ? AND p.Rating BETWEEN ? AND ?"
               + not_in_p + tail)
        return fetch_all(sql, (theme, min_r, max_r) + found_ids + (need,))
    if opening:
        sql = (base
               + " JOIN puzzle_openings po ON p.PuzzleId = po.puzzle_id"
               + " WHERE po.opening = ? AND p.Rating BETWEEN ? AND ?"
               + not_in_p + tail)
        return fetch_all(sql, (opening, min_r, max_r) + found_ids + (need,))
    sql = ("SELECT PuzzleId, FEN, Moves, Rating, Themes, OpeningTags FROM puzzles"
           " WHERE Rating BETWEEN ? AND ?" + not_in + " ORDER BY Rating LIMIT ?")
    return fetch_all(sql, (min_r, max_r) + found_ids + (need,))