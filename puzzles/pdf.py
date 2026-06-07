from io import BytesIO

import chess
import chess.svg
from fpdf import FPDF

from puzzles.chess_utils import puzzle_position, uci_to_san_sequence
from puzzles.constants import (
    PAGE_W,
    BOARD_W, BOARD_SVG_SIZE, X_BOARD,
    PUZZLES_PER_PAGE, SLOT_H, SLOT_PADDING_TOP,
    BOARD_OFFSET_Y, BOARD_FOOTER_GAP, MARGIN_LEFT,
    FONT_FAMILY, FONT_SIZE_HEADER, FONT_SIZE_BODY, FONT_SIZE_FOOTER,
    CELL_H_SMALL,
    TRUNCATION_SUFFIX, RATING_SYMBOL,
    THEMES_MAX_CHARS, THEMES_MAX_CHARS_SOLUTION,
    SEPARATOR_COLOR,
    SOLUTIONS_PAGE_MARGIN, SOLUTIONS_TITLE_SIZE,
    SOLUTIONS_TITLE_LINE_H, SOLUTIONS_TITLE_SPACING,
    SOLUTIONS_COL1_W, SOLUTIONS_COL2_W, SOLUTIONS_COL3_W,
    SOLUTIONS_LINE_H, SOLUTIONS_MULTI_LINE_H,
    SOLUTIONS_INDENT, SOLUTIONS_SPACING,
)


def _board_svg_bytes(board: chess.Board, trigger: chess.Move | None) -> BytesIO:
    """Render the board to an SVG BytesIO with the trigger move highlighted."""
    svg_str = chess.svg.board(
        board=board,
        lastmove=trigger,
        size=BOARD_SVG_SIZE,
        coordinates=True,
    )
    return BytesIO(svg_str.encode())


def generate_puzzle_pdf(puzzles: list) -> bytes:
    """
    Puzzle PDF — 2 puzzles per A4 page.
    Each puzzle shows: board position + which colour is to move.
    Solutions are NOT included.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    for i, (puzzle_id, fen, moves, rating, themes, _) in enumerate(puzzles):
        slot = i % PUZZLES_PER_PAGE
        if slot == 0:
            pdf.add_page()

        y0 = slot * SLOT_H + SLOT_PADDING_TOP

        board, trigger = puzzle_position(fen, moves)
        to_move = "White" if board.turn == chess.WHITE else "Black"

        # ── header ───────────────────────────────────────────────────────────
        pdf.set_font(FONT_FAMILY, "B", FONT_SIZE_HEADER)
        pdf.set_xy(MARGIN_LEFT, y0)
        pdf.cell(
            0, 7,
            f"Puzzle #{i + 1}   .   Rating: {rating}   .   {to_move} to move",
            ln=True,
        )

        # ── board ─────────────────────────────────────────────────────────────
        svg_io = _board_svg_bytes(board, trigger)
        pdf.image(svg_io, x=X_BOARD, y=y0 + BOARD_OFFSET_Y, w=BOARD_W)

        # ── footer ────────────────────────────────────────────────────────────
        footer_y = y0 + BOARD_OFFSET_Y + BOARD_W + BOARD_FOOTER_GAP
        pdf.set_font(FONT_FAMILY, "I", FONT_SIZE_FOOTER)
        pdf.set_xy(MARGIN_LEFT, footer_y)
        short_themes = (
            themes[:THEMES_MAX_CHARS] + TRUNCATION_SUFFIX
            if len(themes) > THEMES_MAX_CHARS
            else themes
        )
        pdf.cell(0, CELL_H_SMALL, f"Themes: {short_themes}", ln=True)
        pdf.set_font(FONT_FAMILY, "", FONT_SIZE_FOOTER)
        pdf.set_x(MARGIN_LEFT)
        pdf.cell(0, CELL_H_SMALL, f"ID: {puzzle_id}", ln=True)

        # ── separator line between slots ──────────────────────────────────────
        if slot == 0:
            pdf.set_draw_color(*SEPARATOR_COLOR)
            pdf.line(MARGIN_LEFT, SLOT_H, PAGE_W - MARGIN_LEFT, SLOT_H)

    return bytes(pdf.output())


def generate_solutions_pdf(puzzles: list) -> bytes:
    """
    Solutions PDF — text only, no boards.
    Lists each puzzle's full solution line in SAN notation.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=SOLUTIONS_PAGE_MARGIN)
    pdf.add_page()

    # ── title ─────────────────────────────────────────────────────────────────
    pdf.set_font(FONT_FAMILY, "B", SOLUTIONS_TITLE_SIZE)
    pdf.cell(0, SOLUTIONS_TITLE_LINE_H, "Solutions", ln=True, align="C")
    pdf.set_font(FONT_FAMILY, "", FONT_SIZE_BODY)
    pdf.cell(0, SOLUTIONS_LINE_H, f"{len(puzzles)} puzzle(s)", ln=True, align="C")
    pdf.ln(SOLUTIONS_TITLE_SPACING)

    # ── one entry per puzzle ──────────────────────────────────────────────────
    for i, (puzzle_id, fen, moves, rating, themes, _) in enumerate(puzzles):
        move_list = moves.split()
        board, _ = puzzle_position(fen, moves)
        to_move = "White" if board.turn == chess.WHITE else "Black"

        solution_ucis = move_list[1:] if len(move_list) > 1 else []
        solution_san  = uci_to_san_sequence(board, solution_ucis) or "-"

        # Row 1: puzzle number, ID, rating, colour
        pdf.set_font(FONT_FAMILY, "B", FONT_SIZE_BODY)
        pdf.cell(SOLUTIONS_COL1_W, SOLUTIONS_LINE_H, f"#{i + 1}", border=0)
        pdf.cell(SOLUTIONS_COL2_W, SOLUTIONS_LINE_H, f"[{puzzle_id}]", border=0)
        pdf.cell(SOLUTIONS_COL3_W, SOLUTIONS_LINE_H, f"{RATING_SYMBOL} {rating}", border=0)
        pdf.cell(0, SOLUTIONS_LINE_H, f"{to_move} to move", ln=True)

        # Row 2: solution line
        pdf.set_font(FONT_FAMILY, "", FONT_SIZE_BODY)
        pdf.set_x(SOLUTIONS_INDENT)
        pdf.multi_cell(0, SOLUTIONS_MULTI_LINE_H, f"Solution:  {solution_san}")

        # Row 3: themes
        pdf.set_font(FONT_FAMILY, "I", FONT_SIZE_FOOTER)
        pdf.set_x(SOLUTIONS_INDENT)
        short_themes = (
            themes[:THEMES_MAX_CHARS_SOLUTION] + TRUNCATION_SUFFIX
            if len(themes) > THEMES_MAX_CHARS_SOLUTION
            else themes
        )
        pdf.cell(0, CELL_H_SMALL, f"Themes: {short_themes}", ln=True)

        pdf.ln(SOLUTIONS_SPACING)

    return bytes(pdf.output())