import chess
import chess.svg
from fasthtml.common import *

from puzzles.chess_utils import puzzle_position
from puzzles.state import ALL_THEMES, RATING_MIN, RATING_MAX


def theme_select(current: str) -> Select:
    options = [Option("All themes", value="", selected=(current == ""))]
    for t in ALL_THEMES:
        options.append(Option(t, value=t, selected=(t == current)))
    return Select(*options, id="theme-select", name="theme")


def rating_slider(label_text: str, slider_id: str, val_id: str,
                  name: str, value: int) -> Div:
    return Div(
        Label(label_text, Span(str(value), id=val_id, cls="slider-val")),
        Input(
            type="range", id=slider_id, name=name,
            min=RATING_MIN, max=RATING_MAX, value=value,
            oninput=f"document.getElementById('{val_id}').textContent=this.value",
        ),
        Div(Span(str(RATING_MIN)), Span(str(RATING_MAX)), cls="rating-row"),
        cls="filter-group",
    )


def filter_bar(theme: str, min_rating: int, max_rating: int) -> Form:
    return Form(
        Div(
            Div(Label("Theme"), theme_select(theme), cls="filter-group"),
            rating_slider("Min rating: ", "min-slider", "min-val", "min_rating", min_rating),
            rating_slider("Max rating: ", "max-slider", "max-val", "max_rating", max_rating),
            Div(
                Button("Apply",            type="submit",
                       formaction="/puzzles",                      cls="btn btn-primary"),
                Button("⬇ Puzzles PDF",   type="submit",
                       formaction="/puzzles/download/puzzles",     cls="btn btn-success"),
                Button("⬇ Solutions PDF", type="submit",
                       formaction="/puzzles/download/solutions",   cls="btn btn-outline"),
                cls="actions",
            ),
            cls="filters",
        ),
        method="get",
        enctype="multipart/form-data",
    )


def puzzle_card(row) -> Div:
    puzzle_id, fen, moves, rating, themes, opening_tags = row
    board, trigger = puzzle_position(fen, moves)
    svg_str = chess.svg.board(board, lastmove=trigger, size=220)
    to_move = "♔ White to move" if board.turn == chess.WHITE else "♚ Black to move"
    theme_list = " · ".join(themes.split()[:3]) if themes else ""
    return Div(
        NotStr(svg_str),
        Div(
            Span(str(rating), cls="rating-badge"),
            Span(to_move, cls="to-move"),
            cls="puzzle-meta",
        ),
        Div(theme_list, cls="theme-tags"),
        cls="puzzle-card",
    )


def puzzle_grid(puzzles: list) -> Div:
    return Div(*[puzzle_card(row) for row in puzzles], cls="puzzle-grid")


def pagination_bar(page: int, total_pages: int,
                   theme: str, min_rating: int, max_rating: int) -> Div:
    def page_href(p: int) -> str:
        return f"/puzzles?theme={theme}&min_rating={min_rating}&max_rating={max_rating}&page={p}"
    prev_attrs = {"href": page_href(page - 1)} if page > 1 else {"aria_disabled": "true"}
    next_attrs = {"href": page_href(page + 1)} if page < total_pages else {"aria_disabled": "true"}
    return Div(
        A("← Prev", **prev_attrs, cls="btn btn-outline"),
        Span(f"Page {page} of {total_pages}"),
        A("Next →", **next_attrs, cls="btn btn-outline"),
        cls="pagination",
    )


def css_link() -> Link:
    return Link(rel="stylesheet", href="/static/styles.css")


def puzzle_css_link() -> Link:
    return Link(rel="stylesheet", href="/static/puzzles/styles.css")