import chess

def puzzle_position(fen: str, moves: str) -> tuple[chess.Board, chess.Move | None]:
    """
    Apply the opponent's trigger move (first move in the sequence) and return:
      - the board at the puzzle start position
      - the trigger move itself (used for SVG highlighting)
    """
    board = chess.Board(fen)
    trigger: chess.Move | None = None
    move_list = moves.split()
    if move_list:
        trigger = chess.Move.from_uci(move_list[0])
        board.push(trigger)
    return board, trigger
 
 
def uci_to_san_sequence(board: chess.Board, uci_moves: list[str]) -> str:
    """
    Convert a list of UCI solution moves to human-readable SAN notation.
    Handles both White-first and Black-first puzzles correctly.
    """
    parts: list[str] = []
    b = board.copy()
    is_first = True
    for uci in uci_moves:
        move = chess.Move.from_uci(uci)
        if b.turn == chess.WHITE:
            parts.append(f"{b.fullmove_number}.")
        elif is_first:
            # Black moves first — show "N..." ellipsis notation
            parts.append(f"{b.fullmove_number}...")
        is_first = False
        parts.append(b.san(move))
        b.push(move)
    return " ".join(parts)