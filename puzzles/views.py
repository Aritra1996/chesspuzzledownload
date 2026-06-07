import chess
import chess.svg
from fasthtml.common import *

from puzzles.chess_utils import puzzle_position
from puzzles.constants import PDF_BTN_REENABLE_MS
from puzzles.state import ALL_OPENINGS, ALL_THEMES, RATING_MIN, RATING_MAX


def theme_select(current: str) -> Select:
    options = [Option("All themes", value="", selected=(current == ""))]
    for t in ALL_THEMES:
        options.append(Option(t, value=t, selected=(t == current)))
    return Select(*options, id="theme-select", name="theme")


def opening_select(current: str) -> Select:
    options = [Option("All openings", value="", selected=(current == ""))]
    for o in ALL_OPENINGS:
        options.append(Option(o, value=o, selected=(o == current)))
    return Select(*options, id="opening-select", name="opening")


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


def filter_bar(theme: str, opening: str, min_rating: int, max_rating: int) -> Form:
    return Form(
        Div(
            Div(Label("Theme"), theme_select(theme), cls="filter-group"),
            Div(Label("Opening"), opening_select(opening), cls="filter-group"),
            rating_slider("Min rating: ", "min-slider", "min-val", "min_rating", min_rating),
            rating_slider("Max rating: ", "max-slider", "max-val", "max_rating", max_rating),
            Div(
                Button("Load Puzzles", id="btn-load", type="submit",
                       formaction="/puzzles", cls="btn btn-primary"),
                cls="actions",
            ),
            cls="filters",
        ),
        Input(type="hidden", name="loaded", value="true"),
        Script("""
(function() {
  var minS = document.getElementById('min-slider');
  var maxS = document.getElementById('max-slider');
  var minV = document.getElementById('min-val');
  var maxV = document.getElementById('max-val');
  minS.addEventListener('input', function() {
    if (parseInt(minS.value) > parseInt(maxS.value)) {
      maxS.value = minS.value;
      maxV.textContent = minS.value;
    }
  });
  maxS.addEventListener('input', function() {
    if (parseInt(maxS.value) < parseInt(minS.value)) {
      minS.value = maxS.value;
      minV.textContent = maxS.value;
    }
  });
})();
"""),
        method="get",
        enctype="multipart/form-data",
    )


def empty_state() -> Div:
    return Div(
        P("Configure filters above and click Load Puzzles to view puzzles.", cls="empty-hint"),
        cls="empty-state",
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


def pdf_panel(puzzles_url: str, solutions_url: str) -> Div:
    return Div(
        A("⬇ Puzzles PDF",   id="btn-puzzles-pdf",  href=puzzles_url,   cls="btn btn-success"),
        A("⬇ Solutions PDF", id="btn-solutions-pdf", href=solutions_url, cls="btn btn-outline"),
        Script(f"""
(function() {{
  ['btn-puzzles-pdf', 'btn-solutions-pdf'].forEach(function(id) {{
    document.getElementById(id).addEventListener('click', function() {{
      var p = document.getElementById('btn-puzzles-pdf');
      var r = document.getElementById('btn-solutions-pdf');
      p.classList.add('btn-disabled'); r.classList.add('btn-disabled');
      setTimeout(function() {{
        p.classList.remove('btn-disabled'); r.classList.remove('btn-disabled');
      }}, {PDF_BTN_REENABLE_MS});
    }});
  }});
}})();
"""),
        cls="pdf-panel",
    )


def puzzle_section(puzzles: list, puzzles_url: str, solutions_url: str) -> Div:
    return Div(
        puzzle_grid(puzzles),
        pdf_panel(puzzles_url, solutions_url),
        cls="puzzle-section",
    )


def meta_row(meta: str, page: int, total_pages: int,
             theme: str, opening: str, min_rating: int, max_rating: int) -> Div:
    def page_href(p: int) -> str:
        return (f"/puzzles?theme={theme}&opening={opening}&min_rating={min_rating}"
                f"&max_rating={max_rating}&page={p}&loaded=true")
    prev_attrs = {"href": page_href(page - 1)} if page > 1 else {"aria_disabled": "true"}
    next_attrs = {"href": page_href(page + 1)} if page < total_pages else {"aria_disabled": "true"}
    return Div(
        P(meta, cls="meta"),
        Div(
            A("← Prev", **prev_attrs, cls="btn btn-outline"),
            Span(f"Page {page} of {total_pages}", cls="page-info"),
            A("Next →", **next_attrs, cls="btn btn-outline"),
            cls="pagination",
        ),
        cls="meta-row",
    )


def css_link() -> Link:
    return Link(rel="stylesheet", href="/static/styles.css")


def puzzle_css_link() -> Link:
    return Link(rel="stylesheet", href="/static/puzzles/styles.css")
