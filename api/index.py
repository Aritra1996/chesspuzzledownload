from fasthtml.common import *

from app import app, rt
from puzzles.views import css_link

import puzzles.routes  # importing registers all @rt handlers


@rt("/")
def index():
    return (
        css_link(),
        Main(
            Div(
                H1("Chess Puzzles ♟️"),
                P("Filter puzzles by theme and difficulty. Download boards and solutions as PDF."),
                A("Browse Puzzles →", href="/puzzles", cls="btn btn-primary"),
                cls="hero",
            )
        ),
    )


if __name__ == "__main__":
    serve()
