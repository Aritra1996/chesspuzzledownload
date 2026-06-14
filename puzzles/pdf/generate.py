from io import BytesIO

import chess
import chess.svg
from fpdf import FPDF

from constants import RATING_DEFAULT_MIN, RATING_DEFAULT_MAX
from puzzles.chess import puzzle_position, uci_to_san_sequence
from puzzles.pdf.constants import (
    PAGE_W, PAGE_H,
    BOARD_W, BOARD_SVG_SIZE, X_BOARD,
    PUZZLES_PER_PAGE,
    PDF_COLOR_DARK, PDF_COLOR_GOLD, PDF_COLOR_LIGHT, PDF_COLOR_RULE, PDF_COLOR_MUTED,
    PDF_MARGIN, PDF_HEADER_H, PDF_BADGE_H,
    PDF_BOARD_GAP, PDF_BELOW_BOARD, PDF_CARD_SPACING,
    PDF_FONT, PDF_SIZE_TITLE, PDF_SIZE_FILTER, PDF_SIZE_BADGE, PDF_SIZE_BODY, PDF_SIZE_SMALL,
    PDF_SOL_LINE_H, PDF_SOL_INDENT, PDF_SOL_SPACING,
    RATING_SYMBOL,
)


def _filter_summary(theme: str, opening: str, min_rating: int, max_rating: int) -> str:
    theme_label   = theme   if theme   else "All themes"
    opening_label = opening if opening else "All openings"
    return f"{theme_label}  |  {opening_label}  |  Rating {min_rating} - {max_rating}"


def _board_svg_bytes(board: chess.Board, trigger: chess.Move | None) -> BytesIO:
    svg_str = chess.svg.board(board=board, lastmove=trigger, size=BOARD_SVG_SIZE, coordinates=True)
    return BytesIO(svg_str.encode())


class _BasePDF(FPDF):
    """FPDF subclass that draws a dark filter-summary header band on every page."""

    def __init__(self, title: str, filter_summary: str, **kwargs):
        super().__init__(**kwargs)
        self._title = title
        self._filter_summary = filter_summary

    def header(self):
        # Dark background band
        self.set_fill_color(*PDF_COLOR_DARK)
        self.rect(0, 0, PAGE_W, PDF_HEADER_H, "F")

        # Title — left, gold, bold
        self.set_font(PDF_FONT, "B", PDF_SIZE_TITLE)
        self.set_text_color(*PDF_COLOR_GOLD)
        self.set_xy(PDF_MARGIN, (PDF_HEADER_H - PDF_SIZE_TITLE * 0.35) / 2)
        self.cell(0, PDF_SIZE_TITLE * 0.35, self._title, ln=False)

        # Filter summary — right, light, normal
        self.set_font(PDF_FONT, "", PDF_SIZE_FILTER)
        self.set_text_color(*PDF_COLOR_LIGHT)
        self.set_xy(0, (PDF_HEADER_H - PDF_SIZE_FILTER * 0.35) / 2)
        self.cell(PAGE_W - PDF_MARGIN, PDF_SIZE_FILTER * 0.35, self._filter_summary, align="R", ln=False)

        # Reset text colour for body content
        self.set_text_color(0, 0, 0)


def generate_puzzle_pdf(puzzles: list, theme: str = "", opening: str = "",
                        min_rating: int = RATING_DEFAULT_MIN, max_rating: int = RATING_DEFAULT_MAX) -> bytes:
    """
    Puzzle PDF — 2 puzzles per A4 page.
    Dark header band on every page; all card body content on white background.
    """
    summary = _filter_summary(theme, opening, min_rating, max_rating)
    pdf = _BasePDF(title="CHESS PUZZLES", filter_summary=summary,
                   orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    # Available height per slot, correctly accounting for the header band
    slot_h = (PAGE_H - PDF_HEADER_H) / PUZZLES_PER_PAGE

    for i, (puzzle_id, fen, moves, rating, _, __) in enumerate(puzzles):
        slot = i % PUZZLES_PER_PAGE
        if slot == 0:
            pdf.add_page()

        y0 = PDF_HEADER_H + slot * slot_h + PDF_CARD_SPACING

        board, trigger = puzzle_position(fen, moves)
        to_move = "White to move" if board.turn == chess.WHITE else "Black to move"

        # ── ruled divider line above each card ───────────────────────────────
        pdf.set_draw_color(*PDF_COLOR_RULE)
        pdf.line(PDF_MARGIN, y0, PAGE_W - PDF_MARGIN, y0)

        # ── puzzle number (left) and rating (right) ───────────────────────────
        label_row_y = y0 + 2
        pdf.set_font(PDF_FONT, "B", PDF_SIZE_BADGE)
        pdf.set_text_color(*PDF_COLOR_GOLD)
        badge_w = PAGE_W - 2 * PDF_MARGIN

        pdf.set_xy(PDF_MARGIN + 2, label_row_y)
        pdf.cell(badge_w / 2, PDF_BADGE_H, f"# {i + 1}", ln=False)

        pdf.set_xy(PDF_MARGIN, label_row_y)
        pdf.cell(badge_w - 2, PDF_BADGE_H, f"{RATING_SYMBOL} {rating}", align="R", ln=False)

        pdf.set_text_color(0, 0, 0)

        # ── board ─────────────────────────────────────────────────────────────
        board_y = y0 + PDF_BADGE_H + PDF_BOARD_GAP
        svg_io = _board_svg_bytes(board, trigger)
        pdf.image(svg_io, x=X_BOARD, y=board_y, w=BOARD_W)

        # ── "to move" and ID lines ────────────────────────────────────────────
        label_y = board_y + BOARD_W + PDF_BELOW_BOARD
        pdf.set_font(PDF_FONT, "I", PDF_SIZE_SMALL)
        pdf.set_text_color(*PDF_COLOR_MUTED)
        pdf.set_xy(0, label_y)
        pdf.cell(PAGE_W, PDF_SIZE_SMALL * 0.35, to_move, align="C", ln=True)

        pdf.set_font(PDF_FONT, "", PDF_SIZE_SMALL)
        pdf.set_x(0)
        pdf.cell(PAGE_W, PDF_SIZE_SMALL * 0.35, f"ID: {puzzle_id}", align="C", ln=True)

        pdf.set_text_color(0, 0, 0)

        # ── separator between the two slots ───────────────────────────────────
        if slot == 0:
            sep_y = PDF_HEADER_H + slot_h
            pdf.set_draw_color(*PDF_COLOR_RULE)
            pdf.line(PDF_MARGIN, sep_y, PAGE_W - PDF_MARGIN, sep_y)

    return bytes(pdf.output())


def generate_solutions_pdf(puzzles: list, theme: str = "", opening: str = "",
                           min_rating: int = RATING_DEFAULT_MIN, max_rating: int = RATING_DEFAULT_MAX) -> bytes:
    """
    Solutions PDF — text only, no boards.
    Dark header band on every page; all entry content on white background.
    Each entry: thin gold rule, then puzzle info + solution on white.
    """
    summary = _filter_summary(theme, opening, min_rating, max_rating)
    pdf = _BasePDF(title="SOLUTIONS", filter_summary=summary,
                   orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Sub-title: puzzle count
    pdf.set_y(PDF_HEADER_H + 4)
    pdf.set_font(PDF_FONT, "", PDF_SIZE_BODY)
    pdf.set_text_color(*PDF_COLOR_MUTED)
    pdf.set_x(PDF_MARGIN)
    pdf.cell(0, PDF_SOL_LINE_H, f"{len(puzzles)} puzzle(s)", ln=True)
    pdf.ln(3)
    pdf.set_text_color(0, 0, 0)

    for i, (puzzle_id, fen, moves, rating, _, __) in enumerate(puzzles):
        move_list = moves.split()
        board, _ = puzzle_position(fen, moves)
        to_move = "White to move" if board.turn == chess.WHITE else "Black to move"

        solution_ucis = move_list[1:] if len(move_list) > 1 else []
        solution_san = uci_to_san_sequence(board, solution_ucis) or "-"

        # ── thin gold rule above each entry ──────────────────────────────────
        rule_y = pdf.get_y()
        pdf.set_draw_color(*PDF_COLOR_RULE)
        pdf.line(PDF_MARGIN, rule_y, PAGE_W - PDF_MARGIN, rule_y)
        pdf.ln(2)

        # ── entry header row (white background, no fill) ──────────────────────
        col1_w, col2_w, col3_w = 16, 36, 24

        pdf.set_font(PDF_FONT, "B", PDF_SIZE_BODY)
        pdf.set_text_color(*PDF_COLOR_GOLD)
        pdf.set_x(PDF_MARGIN + 2)
        pdf.cell(col1_w, PDF_SOL_LINE_H, f"#{i + 1}", ln=False)

        pdf.set_font(PDF_FONT, "", PDF_SIZE_BODY)
        pdf.set_text_color(*PDF_COLOR_DARK)
        pdf.cell(col2_w, PDF_SOL_LINE_H, f"[{puzzle_id}]", ln=False)
        pdf.cell(col3_w, PDF_SOL_LINE_H, f"{RATING_SYMBOL} {rating}", ln=False)
        pdf.cell(0, PDF_SOL_LINE_H, to_move, ln=True)

        pdf.set_text_color(0, 0, 0)

        # ── solution line ─────────────────────────────────────────────────────
        pdf.set_font(PDF_FONT, "", PDF_SIZE_BODY)
        pdf.set_x(PDF_MARGIN + PDF_SOL_INDENT)
        pdf.multi_cell(PAGE_W - 2 * PDF_MARGIN - PDF_SOL_INDENT, PDF_SOL_LINE_H,
                       f"Solution:  {solution_san}")

        pdf.ln(PDF_SOL_SPACING)

    return bytes(pdf.output())
