from fasthtml.common import *
from starlette.responses import Response

from app import rt
from puzzles.constants import MAX_PDF_PUZZLES
from puzzles.db import query_puzzles
from puzzles.pdf import generate_puzzle_pdf, generate_solutions_pdf
from puzzles.state import RATING_MAX, RATING_MIN
from puzzles.validators import sanitise_rating
from puzzles.views import css_link, filter_bar


@rt("/puzzles")
def get(theme: str = "", min_rating: int = RATING_MIN, max_rating: int = RATING_MAX):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    puzzles = query_puzzles(theme, min_rating, max_rating, limit=24)

    meta = f"Showing {len(puzzles)} puzzle(s)  ·  ratings {min_rating}–{max_rating}"
    if theme:
        meta += f"  ·  theme: {theme}"

    return (
        css_link(),
        filter_bar(theme, min_rating, max_rating),
        P(meta, cls="meta"),
    )


@rt("/puzzles/download/puzzles")
def download_puzzles(theme: str = "", min_rating: int = RATING_MIN, max_rating: int = RATING_MAX):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    puzzles = query_puzzles(theme, min_rating, max_rating, limit=MAX_PDF_PUZZLES)
    pdf_bytes = generate_puzzle_pdf(puzzles)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=chess_puzzles.pdf"},
    )


@rt("/puzzles/download/solutions")
def download_solutions(theme: str = "", min_rating: int = RATING_MIN, max_rating: int = RATING_MAX):
    min_rating, max_rating = sanitise_rating(min_rating, max_rating)
    puzzles = query_puzzles(theme, min_rating, max_rating, limit=MAX_PDF_PUZZLES)
    pdf_bytes = generate_solutions_pdf(puzzles)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=solutions.pdf"},
    )