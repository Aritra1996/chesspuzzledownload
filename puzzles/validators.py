from constants import N_PUZZLES_MIN, N_PUZZLES_MAX
from puzzles.data.state import RATING_MIN, RATING_MAX


def sanitise_rating(min_rating: int, max_rating: int) -> tuple[int, int]:
    min_rating = max(RATING_MIN, min(min_rating, RATING_MAX))
    max_rating = max(RATING_MIN, min(max_rating, RATING_MAX))
    if min_rating > max_rating:
        min_rating, max_rating = max_rating, min_rating
    return min_rating, max_rating


def sanitise_n_puzzles(n: int) -> int:
    return max(N_PUZZLES_MIN, min(n, N_PUZZLES_MAX))