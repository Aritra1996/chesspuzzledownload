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
    return (lo or 0, hi or 3000)
 
 
def count_puzzles(theme: str, opening: str, min_r: int, max_r: int) -> int:
    sql = "SELECT COUNT(*) FROM puzzles WHERE Rating BETWEEN ? AND ?"
    params: list = [min_r, max_r]
    if theme:
        sql += " AND instr(' ' || Themes || ' ', ' ' || ? || ' ') > 0"
        params.append(theme)
    if opening:
        sql += " AND instr(' ' || OpeningTags || ' ', ' ' || ? || ' ') > 0"
        params.append(opening)
    (count,) = fetch_one(sql, tuple(params))
    return count


_CAP = 100


def query_puzzles_capped(theme: str, opening: str,
                         min_r: int, max_r: int) -> tuple[list, int]:
    """Returns (puzzles, total). If total > _CAP, puzzles is [] and caller shows the count."""
    base = "Rating BETWEEN ? AND ?"
    params: list = [min_r, max_r]
    if theme:
        base += " AND instr(' ' || Themes || ' ', ' ' || ? || ' ') > 0"
        params.append(theme)
    if opening:
        base += " AND instr(' ' || OpeningTags || ' ', ' ' || ? || ' ') > 0"
        params.append(opening)

    # Count first — cheap (no ORDER BY, no row data transfer)
    (total,) = fetch_one(f"SELECT COUNT(*) FROM puzzles WHERE {base}", tuple(params))

    if total == 0:
        return [], 0

    if total > _CAP:
        return [], total

    # Only fetch full rows when we know the result fits within the cap
    rows = fetch_all(
        f"SELECT PuzzleId, FEN, Moves, Rating, Themes, OpeningTags"
        f" FROM puzzles WHERE {base} ORDER BY Rating LIMIT ?",
        tuple(params + [_CAP]),
    )
    return list(rows), total


def query_puzzles(theme: str, opening: str, min_r: int, max_r: int,
                  limit: int | None = None, offset: int = 0) -> list:
    sql = """
        SELECT PuzzleId, FEN, Moves, Rating, Themes, OpeningTags
        FROM puzzles
        WHERE Rating BETWEEN ? AND ?
    """
    params: list = [min_r, max_r]
    if theme:
        sql += " AND instr(' ' || Themes || ' ', ' ' || ? || ' ') > 0"
        params.append(theme)
    if opening:
        sql += " AND instr(' ' || OpeningTags || ' ', ' ' || ? || ' ') > 0"
        params.append(opening)
    sql += " ORDER BY Rating"
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params += [limit, offset]
    rows = fetch_all(sql, tuple(params))
    return rows