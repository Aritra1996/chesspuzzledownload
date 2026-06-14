from fasthtml.common import *

from puzzles.data.state import ALL_OPENINGS, ALL_THEMES, RATING_MIN, RATING_MAX


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


def rating_slider(label_text: str, slider_id: str, input_id: str,
                  name: str, value: int) -> Div:
    return Div(
        Label(label_text),
        Div(
            Input(type="range", id=slider_id,
                  min=RATING_MIN, max=RATING_MAX, value=value,
                  cls="rating-slider"),
            Input(type="number", id=input_id, name=name,
                  min=RATING_MIN, max=RATING_MAX, value=value,
                  cls="rating-number-input"),
            cls="slider-with-input",
        ),
        cls="filter-group",
    )


def filter_bar() -> Form:
    return Form(
        Div(
            Div(Label("Theme"), theme_select(""), cls="filter-group"),
            Div(Label("Opening"), opening_select(""), cls="filter-group"),
            rating_slider("Min rating", "min-slider", "min-input", "min_rating", RATING_MIN),
            rating_slider("Max rating", "max-slider", "max-input", "max_rating", RATING_MAX),
            Div(
                Button("Load Puzzles", id="btn-load", type="button",
                       hx_get="/puzzles/load",
                       hx_include="closest form",
                       hx_target="#results-tbody",
                       hx_swap="afterbegin",
                       hx_indicator="#progress-bar",
                       cls="btn btn-primary"),
                cls="actions",
            ),
            cls="filters",
        ),
        Script(f"""
(function() {{
  var minS = document.getElementById('min-slider');
  var maxS = document.getElementById('max-slider');
  var minI = document.getElementById('min-input');
  var maxI = document.getElementById('max-input');
  var LO = {RATING_MIN}, HI = {RATING_MAX};

  function clamp(v, lo, hi) {{ return Math.max(lo, Math.min(v, hi)); }}

  // Slider → number input (live)
  minS.addEventListener('input', function() {{
    var v = +minS.value;
    minI.value = v;
    if (v > +maxS.value) {{ maxS.value = v; maxI.value = v; }}
  }});
  maxS.addEventListener('input', function() {{
    var v = +maxS.value;
    maxI.value = v;
    if (v < +minS.value) {{ minS.value = v; minI.value = v; }}
  }});

  // Number input → slider (live): only sync slider when value is complete and in range
  minI.addEventListener('input', function() {{
    var n = +minI.value;
    if (!minI.value || isNaN(n) || n < LO || n > HI) return;
    minS.value = n;
    if (n > +maxS.value) {{ maxS.value = n; maxI.value = n; }}
  }});
  maxI.addEventListener('input', function() {{
    var n = +maxI.value;
    if (!maxI.value || isNaN(n) || n < LO || n > HI) return;
    maxS.value = n;
    if (n < +minS.value) {{ minS.value = n; minI.value = n; }}
  }});

  // On blur: cross-validate against the other slider; empty min → LO, empty max → HI
  minI.addEventListener('blur', function() {{
    var n = +minI.value;
    var hi = Math.min(HI, +maxS.value);
    minI.value = minS.value = isNaN(n) ? LO : clamp(n, LO, hi);
  }});
  maxI.addEventListener('blur', function() {{
    var n = +maxI.value;
    var lo = Math.max(LO, +minS.value);
    maxI.value = maxS.value = isNaN(n) ? HI : clamp(n, lo, HI);
  }});
}})();
"""),
        method="get",
    )


def loading_indicator() -> Div:
    return Div(
        Div(Div(cls="progress-fill"), cls="progress-track"),
        P("Fetching puzzles...", cls="stage-text"),
        id="progress-bar",
        cls="htmx-indicator",
    )


_HISTORY_JS = """
(function () {
  var HISTORY_MAX_ROWS = 5;

  document.body.addEventListener('htmx:afterSwap', function (e) {
    if (e.detail.target.id !== 'results-tbody') return;
    document.getElementById('results-wrapper').classList.remove('hidden');

    // Auto-evict oldest row (bottom) when more than HISTORY_MAX_ROWS exist
    var rows = document.querySelectorAll('#results-tbody tr');
    if (rows.length > HISTORY_MAX_ROWS) {
      var oldest = rows[rows.length - 1];
      oldest.style.transition = 'opacity 0.28s ease, transform 0.28s ease';
      oldest.style.opacity = '0';
      oldest.style.transform = 'translateX(30px)';
      setTimeout(function () { oldest.remove(); }, 300);
    }
  });

  // PDF download via fetch() — spinner lasts exactly as long as generation
  window.downloadPdf = function (btn, url, filename) {
    btn.disabled = true;
    var orig = btn.textContent;
    btn.textContent = 'Generating PDF…';
    fetch(url)
      .then(function (r) { return r.blob(); })
      .then(function (blob) {
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
      })
      .finally(function () {
        btn.disabled = false;
        btn.textContent = orig;
      });
  };
}());
"""


def load_history_table() -> Div:
    return Div(
        Script(_HISTORY_JS),
        P("Recent searches · oldest entry auto-removed after 5", cls="table-caption"),
        Table(
            Thead(Tr(
                Th("#", cls="col-num"),
                Th("Theme"),
                Th("Opening"),
                Th("Rating"),
                Th("Status"),
                Th("Download"),
                Th(""),
            )),
            Tbody(id="results-tbody"),
            cls="puzzle-table",
        ),
        id="results-wrapper",
        cls="results-wrapper hidden",
    )


def load_history_row_pending(theme: str, opening: str, min_rating: int,
                              max_rating: int, qs: str, row_id: str) -> Tr:
    fetch_url = f"/puzzles/load/fetch?{qs}&row_id={row_id}"
    return Tr(
        Td(cls="col-num"),
        Td(theme or "All themes", data_label="Theme"),
        Td(opening or "All openings", data_label="Opening"),
        Td(f"{min_rating}–{max_rating}", data_label="Rating"),
        Td(
            Span("Fetching puzzles...", cls="status-pending"),
            id=f"status-{row_id}",
            hx_get=fetch_url,
            hx_trigger="load",
            hx_target=f"#status-{row_id}",
            hx_swap="outerHTML",
            data_label="Status",
        ),
        Td(id=f"dl-{row_id}", data_label="Download"),
        Td(
            Button("×",
                   hx_delete=f"/puzzles/row/{row_id}",
                   hx_target="closest tr",
                   hx_swap="outerHTML swap:280ms",
                   cls="btn-delete"),
        ),
    )


def load_history_status_cell_counting(total: int, qs: str, row_id: str):
    data_url = f"/puzzles/load/data?{qs}&row_id={row_id}"
    return (
        Td(
            f"{total:,} puzzles found",
            Span(" — getting puzzles…", cls="status-pending"),
            id=f"status-{row_id}",
            cls="status-cell",
            hx_get=data_url,
            hx_trigger="load",
            hx_target=f"#status-{row_id}",
            hx_swap="outerHTML",
            data_label="Status",
        ),
        Td(id=f"dl-{row_id}", hx_swap_oob="true", data_label="Download"),
    )


def load_history_status_cell(status_text: str, has_results: bool,
                              qs: str, row_id: str, too_many: bool = False):
    if too_many:
        dl_content = P(
            "Select a theme or opening, or tighten the rating range to get ≤100 results",
            cls="dl-hint",
        )
        status_cls = "status-too-many"
    else:
        puzzles_url   = f"/puzzles/download/puzzles?{qs}&row_id={row_id}"
        solutions_url = f"/puzzles/download/solutions?{qs}&row_id={row_id}"

        def dl_btn(label: str, url: str, filename: str):
            if has_results:
                return Button(label,
                              onclick=f"downloadPdf(this,'{url}','{filename}')",
                              cls="btn btn-sm btn-outline")
            return Button(label, cls="btn btn-sm btn-outline", disabled=True)

        dl_content = Div(
            dl_btn("Puzzles PDF",   puzzles_url,   "chess_puzzles.pdf"),
            dl_btn("Solutions PDF", solutions_url, "solutions.pdf"),
            cls="dl-buttons",
        )
        status_cls = "status-cell" if has_results else "status-empty"

    return (
        Td(status_text, id=f"status-{row_id}", cls=status_cls, data_label="Status"),
        Td(dl_content, id=f"dl-{row_id}", hx_swap_oob="true", data_label="Download"),
    )


def css_link() -> Link:
    return Link(rel="stylesheet", href="/static/styles.css")


def puzzle_css_link() -> Link:
    return Link(rel="stylesheet", href="/static/puzzles/styles.css")
