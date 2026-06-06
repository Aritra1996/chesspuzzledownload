from fasthtml.common import *

app, rt = fast_app()

@rt("/")
def get():
    return Titled("Chess Puzzles", P("Setup successful ♟️"))

serve()