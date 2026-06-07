# puzzles/constants.py

# ── Page dimensions (A4) ─────────────────────────────────────────────────────
PAGE_W = 210
PAGE_H = 297

# ── Board rendering ──────────────────────────────────────────────────────────
BOARD_W        = 88    # board width in PDF (mm)
BOARD_SVG_SIZE = 400   # internal SVG pixel size
X_BOARD        = (PAGE_W - BOARD_W) / 2   # horizontally centred

# ── Layout ───────────────────────────────────────────────────────────────────
PUZZLES_PER_PAGE = 2
SLOT_H           = PAGE_H / PUZZLES_PER_PAGE
SLOT_PADDING_TOP = 6
BOARD_OFFSET_Y   = 8
BOARD_FOOTER_GAP = 2
MARGIN_LEFT      = 10

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_FAMILY      = "Helvetica"
FONT_SIZE_HEADER = 10
FONT_SIZE_BODY   = 9
FONT_SIZE_FOOTER = 7

# ── Cell heights ─────────────────────────────────────────────────────────────
CELL_H_SMALL = 4   # used for footer/theme/ID rows

# ── Text formatting ──────────────────────────────────────────────────────────
TRUNCATION_SUFFIX = "..."   # appended when theme text is clipped
RATING_SYMBOL     = "*"     # latin-1-safe replacement for the star glyph

# ── Text truncation ──────────────────────────────────────────────────────────
THEMES_MAX_CHARS          = 72
THEMES_MAX_CHARS_SOLUTION = 90

# ── Display pagination ───────────────────────────────────────────────────────
PAGE_SIZE = 24

# ── Separator line ───────────────────────────────────────────────────────────
SEPARATOR_COLOR = (200, 200, 200)   # RGB grey

# ── Solutions PDF layout ─────────────────────────────────────────────────────
SOLUTIONS_PAGE_MARGIN   = 15
SOLUTIONS_TITLE_SIZE    = 18
SOLUTIONS_TITLE_LINE_H  = 12   # cell height for the "Solutions" title row
SOLUTIONS_TITLE_SPACING = 6    # vertical space after subtitle
SOLUTIONS_COL1_W        = 12   # puzzle number column
SOLUTIONS_COL2_W        = 30   # puzzle ID column
SOLUTIONS_COL3_W        = 22   # rating column
SOLUTIONS_LINE_H        = 6
SOLUTIONS_MULTI_LINE_H  = 5
SOLUTIONS_INDENT        = 12
SOLUTIONS_SPACING       = 3