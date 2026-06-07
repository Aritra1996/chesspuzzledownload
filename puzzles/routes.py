from math import ceil

from fasthtml.common import *
from starlette.responses import Response

from app import rt
from puzzles.constants import PAGE_SIZE
from puzzles.db import count_puzzles, query_puzzles
from puzzles.pdf import generate_puzzle_pdf, generate_solutions_pdf
from puzzles.state import RATING_MAX, RATING_MIN, TOTAL_PUZZLES
from puzzles.validators import sanitise_rating
from puzzles.views import css_link, filter_bar, pagination_bar, puzzle_css_link, puzzle_grid


@rt("/puzzles")
def get(theme: str = "", min_rating: int = RATING_MIN, max_rating: int = RATING_MAX, page: int = 1):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    page = max(1, page)

    filtered_total = count_puzzles(theme, min_rating, max_rating)
    total_pages = max(1, ceil(filtered_total / PAGE_SIZE))
    page = min(page, total_pages)
    offset = (page - 1) * PAGE_SIZE

    puzzles = query_puzzles(theme, min_rating, max_rating, limit=PAGE_SIZE, offset=offset)

    meta = f"Showing {len(puzzles)} of {TOTAL_PUZZLES} puzzle(s)  ·  ratings {min_rating}–{max_rating}"
    if theme:
        meta += f"  ·  theme: {theme}"

    return (
        css_link(),
        puzzle_css_link(),
        filter_bar(theme, min_rating, max_rating),
        P(meta, cls="meta"),
        puzzle_grid(puzzles),
        pagination_bar(page, total_pages, theme, min_rating, max_rating),
    )


@rt("/puzzles/download/puzzles")
def download_puzzles(theme: str = "", min_rating: int = RATING_MIN, max_rating: int = RATING_MAX):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    puzzles = query_puzzles(theme, min_rating, max_rating)
    pdf_bytes = generate_puzzle_pdf(puzzles)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=chess_puzzles.pdf"},
    )


@rt("/puzzles/download/solutions")
def download_solutions(theme: str = "", min_rating: int = RATING_MIN, max_rating: int = RATING_MAX):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    puzzles = query_puzzles(theme, min_rating, max_rating)
    pdf_bytes = generate_solutions_pdf(puzzles)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=solutions.pdf"},
    )
