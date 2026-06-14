import time
from urllib.parse import urlencode

from fasthtml.common import *
from starlette.responses import Response

from app import rt
import core.cache as cache
from constants import N_PUZZLES_DEFAULT
from puzzles.data.queries import query_puzzles
from puzzles.pdf.generate import generate_puzzle_pdf, generate_solutions_pdf
from puzzles.data.state import RATING_MAX, RATING_MIN
from puzzles.validators import sanitise_n_puzzles, sanitise_rating
from puzzles.views import (css_link, filter_bar, load_history_row_pending,
                            load_history_status_cell,
                            load_history_table, loading_indicator, puzzle_css_link)


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
        min_rating: int = RATING_MIN, max_rating: int = RATING_MAX,
        n_puzzles: int = N_PUZZLES_DEFAULT):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    n_puzzles = sanitise_n_puzzles(n_puzzles)
    qs = urlencode({"theme": theme, "opening": opening,
                    "min_rating": min_rating, "max_rating": max_rating,
                    "n_puzzles": n_puzzles})
    row_id = str(int(time.time() * 1000))
    return load_history_row_pending(theme, opening, min_rating, max_rating, n_puzzles, qs, row_id)


@rt("/puzzles/load/data")
def get(theme: str = "", opening: str = "",
        min_rating: int = RATING_MIN, max_rating: int = RATING_MAX,
        n_puzzles: int = N_PUZZLES_DEFAULT, row_id: str = ""):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    n_puzzles = sanitise_n_puzzles(n_puzzles)
    qs = urlencode({"theme": theme, "opening": opening,
                    "min_rating": min_rating, "max_rating": max_rating,
                    "n_puzzles": n_puzzles})
    puzzles = query_puzzles(theme, opening, min_rating, max_rating, n_puzzles=n_puzzles)
    if not puzzles:
        return load_history_status_cell("No puzzles found for these filters",
                                        has_results=False, qs=qs, row_id=row_id)
    found = len(puzzles)
    status = (f"{found} of {n_puzzles} puzzles found"
              if found < n_puzzles else f"{found} puzzles selected")
    cache.put(row_id, puzzles)
    return load_history_status_cell(status, has_results=True, qs=qs, row_id=row_id)


@rt("/puzzles/download/puzzles")
def download_puzzles(theme: str = "", opening: str = "",
                     min_rating: int = RATING_MIN, max_rating: int = RATING_MAX,
                     n_puzzles: int = N_PUZZLES_DEFAULT, row_id: str = ""):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    n_puzzles = sanitise_n_puzzles(n_puzzles)
    puzzles = cache.get(row_id) if row_id else None
    if puzzles is None:
        puzzles = query_puzzles(theme, opening, min_rating, max_rating, n_puzzles=n_puzzles)
    pdf_bytes = generate_puzzle_pdf(puzzles, theme, opening, min_rating, max_rating)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=chess_puzzles.pdf"},
    )


@rt("/puzzles/download/solutions")
def download_solutions(theme: str = "", opening: str = "",
                       min_rating: int = RATING_MIN, max_rating: int = RATING_MAX,
                       n_puzzles: int = N_PUZZLES_DEFAULT, row_id: str = ""):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    n_puzzles = sanitise_n_puzzles(n_puzzles)
    puzzles = cache.get(row_id) if row_id else None
    if puzzles is None:
        puzzles = query_puzzles(theme, opening, min_rating, max_rating, n_puzzles=n_puzzles)
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
