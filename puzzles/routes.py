from math import ceil
from urllib.parse import urlencode

from fasthtml.common import *
from starlette.responses import Response

from app import rt
from puzzles.pdf.constants import PAGE_SIZE
from puzzles.data.queries import count_puzzles, query_puzzles
from puzzles.pdf.generate import generate_puzzle_pdf, generate_solutions_pdf
from puzzles.data.state import RATING_MAX, RATING_MIN
from puzzles.validators import sanitise_rating
from puzzles.views import (css_link, empty_state, filter_bar, meta_row,
                            puzzle_css_link, puzzle_section)


@rt("/puzzles")
def get(theme: str = "", opening: str = "",
        min_rating: int = RATING_MIN, max_rating: int = RATING_MAX,
        page: int = 1, loaded: bool = False):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)

    if not loaded:
        return (css_link(), puzzle_css_link(),
                filter_bar(theme, opening, min_rating, max_rating), empty_state())

    page = max(1, page)
    filtered_total = count_puzzles(theme, opening, min_rating, max_rating)
    total_pages = max(1, ceil(filtered_total / PAGE_SIZE))
    page = min(page, total_pages)
    offset = (page - 1) * PAGE_SIZE

    puzzles = query_puzzles(theme, opening, min_rating, max_rating,
                            limit=PAGE_SIZE, offset=offset)

    start = offset + 1
    end = offset + len(puzzles)
    meta = f"Showing {start}–{end} of {filtered_total} puzzle(s)  ·  ratings {min_rating}–{max_rating}"
    if theme:
        meta += f"  ·  theme: {theme}"
    if opening:
        meta += f"  ·  opening: {opening}"

    qs = urlencode({"theme": theme, "opening": opening,
                    "min_rating": min_rating, "max_rating": max_rating})
    puzzles_url = f"/puzzles/download/puzzles?{qs}"
    solutions_url = f"/puzzles/download/solutions?{qs}"

    return (
        css_link(),
        puzzle_css_link(),
        filter_bar(theme, opening, min_rating, max_rating),
        meta_row(meta, page, total_pages, theme, opening, min_rating, max_rating),
        puzzle_section(puzzles, puzzles_url, solutions_url),
    )


@rt("/puzzles/download/puzzles")
def download_puzzles(theme: str = "", opening: str = "",
                     min_rating: int = RATING_MIN, max_rating: int = RATING_MAX):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    puzzles = query_puzzles(theme, opening, min_rating, max_rating)
    pdf_bytes = generate_puzzle_pdf(puzzles, theme, opening, min_rating, max_rating)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=chess_puzzles.pdf"},
    )


@rt("/puzzles/download/solutions")
def download_solutions(theme: str = "", opening: str = "",
                       min_rating: int = RATING_MIN, max_rating: int = RATING_MAX):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    puzzles = query_puzzles(theme, opening, min_rating, max_rating)
    pdf_bytes = generate_solutions_pdf(puzzles, theme, opening, min_rating, max_rating)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=solutions.pdf"},
    )
