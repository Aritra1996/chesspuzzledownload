import time
from urllib.parse import urlencode

from fasthtml.common import *
from starlette.responses import Response

from app import rt
import core.cache as cache
from puzzles.data.queries import query_puzzles, query_puzzles_capped
from puzzles.pdf.generate import generate_puzzle_pdf, generate_solutions_pdf
from puzzles.data.state import RATING_MAX, RATING_MIN
from puzzles.validators import sanitise_rating
from puzzles.views import (css_link, filter_bar, load_history_row_pending,
                            load_history_status_cell, load_history_table,
                            loading_indicator, puzzle_css_link)


@rt("/puzzles")
def get():
    return (
        css_link(), puzzle_css_link(),
        filter_bar(),
        loading_indicator(),
        load_history_table(),
    )


@rt("/puzzles/load")
def get(theme: str = "", opening: str = "",
        min_rating: int = RATING_MIN, max_rating: int = RATING_MAX):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    qs = urlencode({"theme": theme, "opening": opening,
                    "min_rating": min_rating, "max_rating": max_rating})
    row_id = str(int(time.time() * 1000))
    return load_history_row_pending(theme, opening, min_rating, max_rating, qs, row_id)


@rt("/puzzles/load/fetch")
def get(theme: str = "", opening: str = "",
        min_rating: int = RATING_MIN, max_rating: int = RATING_MAX, row_id: str = ""):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    qs = urlencode({"theme": theme, "opening": opening,
                    "min_rating": min_rating, "max_rating": max_rating})

    puzzles, total = query_puzzles_capped(theme, opening, min_rating, max_rating)

    if total == 0:
        return load_history_status_cell("No puzzles found for these filters",
                                        has_results=False, qs=qs, row_id=row_id)

    if total > 100:
        status = f"{total:,} puzzles found — too many to download"
        return load_history_status_cell(status, has_results=False, qs=qs,
                                        row_id=row_id, too_many=True)

    cache.put(row_id, puzzles)
    return load_history_status_cell(f"{total:,} puzzles found",
                                    has_results=True, qs=qs, row_id=row_id)


@rt("/puzzles/download/puzzles")
def download_puzzles(theme: str = "", opening: str = "",
                     min_rating: int = RATING_MIN, max_rating: int = RATING_MAX,
                     row_id: str = ""):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    puzzles = cache.get(row_id) if row_id else None
    if puzzles is None:
        puzzles = query_puzzles(theme, opening, min_rating, max_rating, limit=100)
    pdf_bytes = generate_puzzle_pdf(puzzles, theme, opening, min_rating, max_rating)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=chess_puzzles.pdf"},
    )


@rt("/puzzles/download/solutions")
def download_solutions(theme: str = "", opening: str = "",
                       min_rating: int = RATING_MIN, max_rating: int = RATING_MAX,
                       row_id: str = ""):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    puzzles = cache.get(row_id) if row_id else None
    if puzzles is None:
        puzzles = query_puzzles(theme, opening, min_rating, max_rating, limit=100)
    pdf_bytes = generate_solutions_pdf(puzzles, theme, opening, min_rating, max_rating)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=solutions.pdf"},
    )


@rt("/puzzles/row/{row_id}")
def delete(row_id: str):
    cache.delete(row_id)
    return ""
