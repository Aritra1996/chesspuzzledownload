from fasthtml.common import *

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
                       formaction="/puzzles",              cls="btn btn-primary"),
                Button("⬇ Puzzles PDF",   type="submit",
                       formaction="/puzzles/download/puzzles",   cls="btn btn-success"),
                Button("⬇ Solutions PDF", type="submit",
                       formaction="/puzzles/download/solutions", cls="btn btn-outline"),
                cls="actions",
            ),
            cls="filters",
        ),
        method="get",
    )


def css_link() -> Link:
    return Link(rel="stylesheet", href="/static/styles.css")