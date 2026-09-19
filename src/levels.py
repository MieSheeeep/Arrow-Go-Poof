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


FLOWER_ARROW_GRID = (
    (None, None, "U", None, None),
    (None, "L", "U", "R", None),
    ("L", "L", ".", "R", "R"),
    (None, "L", "D", "R", None),
    (None, None, "D", None, None),
)
FLOWER_COLOR_GRID = (
    (None, None, "flower", None, None),
    (None, "flower", "flower", "flower", None),
    ("leaf", "flower", "leaf_light", "flower", "leaf"),
    (None, "leaf", "trunk", "leaf", None),
    (None, None, "grass", None, None),
)

SUN_ARROW_GRID = (
    ("U", "U", "U", "U"),
    ("L", "U", "U", "R"),
    ("L", "D", "D", "R"),
    ("L", "D", "D", "R"),
)
SUN_COLOR_GRID = (
    ("flower", "flower", "flower", "flower"),
    ("flower", "leaf_light", "leaf_light", "flower"),
    ("grass", "leaf", "leaf", "grass"),
    ("grass", "trunk", "trunk", "grass"),
)


def create_flower_board() -> Board:
    """Return a fresh Board for the flower-shaped demo level."""
    return Board(
        [list(row) for row in FLOWER_ARROW_GRID],
        [list(row) for row in FLOWER_COLOR_GRID],
    )


def create_sun_board() -> Board:
    """Return a fresh Board for the sun-shaped demo level."""
    return Board(
        [list(row) for row in SUN_ARROW_GRID],
        [list(row) for row in SUN_COLOR_GRID],
    )


LEVEL_NAMES = ("TREE", "FLOWER", "SUN")
LEVEL_FACTORIES = (create_tree_board, create_flower_board, create_sun_board)
