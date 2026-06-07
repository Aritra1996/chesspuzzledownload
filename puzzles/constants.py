# puzzles/constants.py

# ── Page dimensions (A4) ─────────────────────────────────────────────────────
PAGE_W = 210
PAGE_H = 297

# ── Board rendering ──────────────────────────────────────────────────────────
BOARD_W        = 90    # board width in PDF (mm)
BOARD_SVG_SIZE = 400   # internal SVG pixel size
X_BOARD        = (PAGE_W - BOARD_W) / 2   # horizontally centred

# ── Layout ───────────────────────────────────────────────────────────────────
PUZZLES_PER_PAGE = 2
SLOT_H           = PAGE_H / PUZZLES_PER_PAGE

# ── PDF colours (RGB) ─────────────────────────────────────────────────────────
PDF_COLOR_DARK  = (26,  18,  9)    # near-black brown — header/badge background
PDF_COLOR_GOLD  = (201, 168, 76)   # gold — accent text
PDF_COLOR_LIGHT = (240, 230, 204)  # warm white — text on dark backgrounds
PDF_COLOR_RULE  = (180, 150, 90)   # muted gold — horizontal rules
PDF_COLOR_MUTED = (120, 100, 70)   # muted brown — secondary text

# ── PDF margins & spacing ─────────────────────────────────────────────────────
PDF_MARGIN       = 14   # left / right page margin (mm)
PDF_HEADER_H     = 16   # height of the top filter-summary band (mm)
PDF_BADGE_H      = 8    # height of each puzzle's number/rating badge row (mm)
PDF_BOARD_GAP    = 4    # vertical gap between badge bottom and board top (mm)
PDF_BELOW_BOARD  = 5    # vertical gap below board to "to move" line (mm)
PDF_CARD_SPACING = 6    # vertical gap between two puzzle cards on the same page (mm)

# ── PDF fonts & sizes ─────────────────────────────────────────────────────────
PDF_FONT        = "Helvetica"
PDF_SIZE_TITLE  = 13   # "CHESS PUZZLES" / "SOLUTIONS" in header band
PDF_SIZE_FILTER = 8    # filter summary sub-line in header band
PDF_SIZE_BADGE  = 10   # puzzle number + rating in badge
PDF_SIZE_BODY   = 9    # regular body text
PDF_SIZE_SMALL  = 7    # secondary labels (ID, "to move")

# ── Solutions-specific ────────────────────────────────────────────────────────
PDF_SOL_LINE_H  = 6    # line height for solution text rows
PDF_SOL_INDENT  = 8    # left indent for solution content under the header row
PDF_SOL_SPACING = 5    # vertical gap between solution entries

# ── Misc ──────────────────────────────────────────────────────────────────────
RATING_SYMBOL = "*"    # latin-1-safe replacement for the star glyph

# ── Display pagination ───────────────────────────────────────────────────────
PAGE_SIZE = 4

# ── PDF button re-enable delay (ms) after a download is triggered ─────────────
PDF_BTN_REENABLE_MS = 6000
