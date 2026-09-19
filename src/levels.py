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

TREE_ARROW_GRID = (
    (None, None, None, None, None, None, "U", None, None, None, None, None, None),
    (None, None, None, None, "U", "U", "U", "U", "U", None, None, None, None),
    (None, None, None, "U", "U", "U", "U", "U", "U", "U", "U", None, None),
    (None, None, "L", "U", "U", "U", "U", "U", "U", "U", "R", None, None),
    (None, "L", "U", "U", "U", "U", "U", "U", "U", "U", "U", "R", None),
    ("L", "U", "U", "U", "U", "U", "U", "U", "U", "U", "U", "U", "R"),
    (None, "L", "U", "U", "U", "U", "U", "U", "U", "U", "U", "R", None),
    (None, None, "L", "U", "U", "U", "U", "U", "U", "U", "R", None, None),
    (None, None, None, None, "D", "D", "D", "D", "D", None, None, None, None),
    (None, None, None, None, "D", "D", "D", "D", "D", None, None, None, None),
    (None, None, None, None, "D", "D", "D", "D", "D", None, None, None, None),
    (None, None, None, "L", "D", "D", "D", "D", "D", "R", None, None, None),
)
TREE_COLOR_GRID = (
    (None, None, None, None, None, None, "leaf_light", None, None, None, None, None, None),
    (None, None, None, None, "leaf", "leaf", "leaf", "leaf", "leaf", None, None, None, None),
    (None, None, None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None, None),
    (None, None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None, None),
    (None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None),
    ("leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf"),
    (None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None),
    (None, None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None, None),
    (None, None, None, None, "trunk", "trunk", "trunk", "trunk", "trunk", None, None, None, None),
    (None, None, None, None, "trunk", "trunk", "trunk", "trunk", "trunk", None, None, None, None),
    (None, None, None, None, "trunk", "trunk", "trunk", "trunk", "trunk", None, None, None, None),
    (None, None, None, "grass", "grass", "grass", "grass", "grass", "grass", "grass", None, None, None),
)


def create_sample_board() -> Board:
    """Return a fresh Board for the built-in sample level."""
    arrow_grid = [list(row) for row in SAMPLE_ARROW_GRID]
    color_grid = [list(row) for row in SAMPLE_COLOR_GRID]
    return Board(arrow_grid, color_grid)


def create_tree_board() -> Board:
    """Return a fresh Board for the tree-shaped demo level."""
    arrow_grid = [list(row) for row in TREE_ARROW_GRID]
    color_grid = [list(row) for row in TREE_COLOR_GRID]
    return Board(arrow_grid, color_grid)
