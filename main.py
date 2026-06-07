from fasthtml.common import *

from app import app, rt
from puzzles.views import css_link

import puzzles.routes  # importing this registers all @rt decorators inside it


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


serve()