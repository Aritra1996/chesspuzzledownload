from fasthtml.common import *

from app import app, rt
from puzzles.views import css_link
from puzzles.data.state import (
    ALL_THEMES, ALL_OPENINGS, RATING_MIN, RATING_MAX, PUZZLE_COUNT,
)

import puzzles.routes  # importing registers all @rt handlers


def _fmt_count(n: int) -> str:
    return f"{n // 1000}K+" if n >= 1000 else str(n)


@rt("/")
def index():
    puzzle_count = _fmt_count(PUZZLE_COUNT)
    theme_count  = str(len(ALL_THEMES))
    opening_count = f"{len(ALL_OPENINGS):,}"
    rating_range  = f"{RATING_MIN} – {RATING_MAX}"

    return (
        css_link(),
        Main(
            # ── Hero ────────────────────────────────────────────────────────
            Section(
                H1("Chess Puzzles ♟"),
                P(
                    "Browse Lichess puzzles filtered by theme, opening, and "
                    "difficulty rating. Download as a printable PDF."
                ),
                A("Browse Puzzles →", href="/puzzles", cls="btn btn-primary"),
                cls="hero",
            ),

            # ── Stats bar ────────────────────────────────────────────────
            Div(
                Div(
                    Span(puzzle_count, cls="stat-number"),
                    Span("Puzzles", cls="stat-label"),
                    cls="stat",
                ),
                Div(
                    Span(theme_count, cls="stat-number"),
                    Span("Themes", cls="stat-label"),
                    cls="stat",
                ),
                Div(
                    Span(opening_count, cls="stat-number"),
                    Span("Openings", cls="stat-label"),
                    cls="stat",
                ),
                Div(
                    Span(rating_range, cls="stat-number"),
                    Span("Rating range", cls="stat-label"),
                    cls="stat",
                ),
                cls="stats-bar",
            ),

            # ── Feature cards ────────────────────────────────────────────
            Div(
                Div(
                    Span("♟", cls="feature-icon"),
                    H3("Filter by Theme & Opening"),
                    P(
                        f"Choose from {theme_count} tactical themes — forks, "
                        f"pins, mates — and narrow by {opening_count} openings "
                        "to practice the lines you actually play."
                    ),
                    cls="feature-card",
                ),
                Div(
                    Span("★", cls="feature-icon"),
                    H3("Set Your Difficulty"),
                    P(
                        f"Slide the rating range from {RATING_MIN} to "
                        f"{RATING_MAX} to match your level. Puzzles are "
                        "sampled evenly across the range so you get variety, "
                        "not just the easiest ones."
                    ),
                    cls="feature-card",
                ),
                Div(
                    Span("⬇", cls="feature-icon"),
                    H3("Download as PDF"),
                    P(
                        "Export your selection as two PDFs: one with puzzle "
                        "positions to solve, and a separate solutions sheet "
                        "with the move sequences. Ready to print."
                    ),
                    cls="feature-card",
                ),
                cls="feature-grid",
            ),
        ),
    )


if __name__ == "__main__":
    serve()
