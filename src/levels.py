"""Built-in level definitions for development and tests."""
from src.board import Board

SAMPLE_ARROW_GRID = (
    (None, None, "U", None, None),
    (None, "L", "D", "R", None),
    ("R", "U", "L", "D", "L"),
)
SAMPLE_COLOR_GRID = (
    (None, None, "leaf_light", None, None),
    (None, "leaf", "leaf", "leaf", None),
    ("grass", "trunk", "trunk", "grass", "flower"),
)


def create_sample_board() -> Board:
    """Return a fresh Board for the built-in sample level."""
    arrow_grid = [list(row) for row in SAMPLE_ARROW_GRID]
    color_grid = [list(row) for row in SAMPLE_COLOR_GRID]
    return Board(arrow_grid, color_grid)
