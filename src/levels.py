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

TREE_LAYOUT_SEED = 2026091921
_TREE_PIXEL_COLORS = {
    "K": "ball_outline",
    "H": "ball_highlight",
    "R": "ball_red",
    "S": "ball_shine",
    "W": "ball_white",
    "G": "ball_gray",
}
_TREE_PIXEL_ROWS = (
    "................",
    "................",
    "......KKKK......",
    "....KKHRRRKK....",
    "...KHHSHRRRRK...",
    "...KHSHHHHRRK...",
    "..KHHHHHRRRRRK..",
    "..KHHHHKKRRRRK..",
    "..KKHHKWGKRRKK..",
    "..KWKKKGGKKKGK..",
    "...KWWWKKGGGK...",
    "...KWWWWGGGGK...",
    "....KKWGGGKK....",
    "......KKKK......",
    "................",
    "................",
)
TREE_COLOR_GRID = tuple(
    tuple(None if pixel == "." else _TREE_PIXEL_COLORS[pixel] for pixel in row)
    for row in _TREE_PIXEL_ROWS
)
TREE_ARROW_GRID = (
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (None, None, None, None, None, None, "U", "L", "R", "U", None, None, None, None, None, None),
    (None, None, None, None, "L", "U", "L", "L", "U", "U", "U", "U", None, None, None, None),
    (None, None, None, "U", "D", "U", "L", "R", "R", "U", "U", "U", "R", None, None, None),
    (None, None, None, "U", "L", "U", "R", "R", "U", "U", "U", "R", "R", None, None, None),
    (None, None, "L", "L", "D", "U", "D", "L", "U", "U", "U", "U", "R", "R", None, None),
    (None, None, "L", "L", "D", "U", "D", "U", "U", "U", "R", "R", "R", "R", None, None),
    (None, None, "L", "L", "L", "L", "D", "L", "L", "R", "D", "R", "R", "R", None, None),
    (None, None, "D", "U", "L", "D", "L", "R", "D", "R", "D", "R", "D", "D", None, None),
    (None, None, None, "D", "L", "L", "L", "D", "D", "U", "D", "L", "R", None, None, None),
    (None, None, None, "D", "L", "L", "D", "L", "D", "R", "D", "R", "D", None, None, None),
    (None, None, None, None, "L", "D", "D", "L", "D", "D", "D", "R", None, None, None, None),
    (None, None, None, None, None, None, "D", "R", "R", "R", None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
)
TREE_SOLUTION = (
    (3, 10), (8, 2), (13, 9), (9, 13), (12, 10), (6, 13), (12, 4), (3, 5),
    (9, 2), (4, 10), (6, 2), (8, 13), (11, 3), (4, 5), (5, 12), (3, 4),
    (11, 12), (4, 12), (2, 6), (8, 3), (7, 13), (11, 10), (8, 4), (2, 9),
    (2, 8), (3, 11), (13, 6), (7, 2), (7, 3), (4, 3), (10, 10), (10, 12),
    (5, 3), (10, 3), (13, 8), (6, 3), (12, 6), (13, 7), (3, 9), (10, 4),
    (9, 12), (5, 5), (3, 6), (7, 12), (11, 4), (5, 10), (6, 12), (12, 8),
    (11, 6), (11, 11), (11, 5), (9, 3), (12, 5), (10, 5), (11, 9), (3, 8),
    (9, 4), (4, 9), (8, 12), (7, 4), (5, 9), (9, 5), (9, 11), (9, 6),
    (7, 11), (9, 10), (2, 7), (4, 11), (12, 11), (12, 9), (6, 5), (8, 5),
    (3, 7), (4, 8), (6, 4), (7, 5), (5, 8), (5, 11), (11, 7), (8, 10),
    (9, 9), (5, 4), (6, 10), (4, 4), (8, 11), (6, 9), (10, 6), (8, 6),
    (8, 9), (12, 7), (7, 6), (7, 9), (6, 8), (4, 7), (8, 7), (6, 6),
    (11, 8), (7, 10), (4, 6), (10, 9), (8, 8), (5, 7), (10, 8), (7, 8),
    (5, 6), (10, 7), (6, 7), (6, 11), (7, 7), (9, 8), (9, 7), (10, 11),
)


def create_sample_board() -> Board:
    """Return a fresh Board for the built-in sample level."""
    arrow_grid = [list(row) for row in SAMPLE_ARROW_GRID]
    color_grid = [list(row) for row in SAMPLE_COLOR_GRID]
    return Board(arrow_grid, color_grid)


def create_tree_board() -> Board:
    """Return a fresh Board for the supplied bead-ball pixel pattern."""
    arrow_grid = [list(row) for row in TREE_ARROW_GRID]
    color_grid = [list(row) for row in TREE_COLOR_GRID]
    return Board(arrow_grid, color_grid)


FLOWER_LAYOUT_SEED = 2026091901
FLOWER_COLOR_GRID = (
    (None, None, None, None, None, "petal_light", "petal_light", "petal_light", None, None, None, None, None),
    (None, None, None, "petal_light", "petal_light", "petal_light", "petal_light", "petal_light", "petal_light", "petal_light", None, None, None),
    (None, None, "petal", "petal", "petal", "petal", "petal", "petal", "petal", "petal", "petal", None, None),
    (None, "petal", "petal", "petal", "center", "center", "center", "center", "center", "petal", "petal", "petal", None),
    (None, "petal", "petal", "petal", "center", "center", "center", "center", "center", "petal", "petal", "petal", None),
    (None, None, "petal", "petal", "center", "center", "center", "center", "center", "petal", "petal", None, None),
    (None, None, None, "petal", "petal", "petal", "petal", "petal", "petal", "petal", None, None, None),
    (None, None, None, None, None, "leaf", "stem", "leaf", None, None, None, None, None),
    (None, None, None, None, None, None, "stem", None, None, None, None, None, None),
    (None, None, None, None, "leaf", "leaf", "stem", "leaf", "leaf", None, None, None, None),
    (None, None, None, "leaf", "leaf", "leaf", "stem", "leaf", "leaf", "leaf", None, None, None),
    (None, None, None, None, None, "leaf", "stem", "leaf", None, None, None, None, None),
    (None, None, None, None, None, None, "stem", None, None, None, None, None, None),
)
FLOWER_ARROW_GRID = (
    (None, None, None, None, None, "U", "U", "R", None, None, None, None, None),
    (None, None, None, "L", "L", "U", "U", "R", "U", "U", None, None, None),
    (None, None, "L", "L", "U", "U", "U", "R", "R", "R", "R", None, None),
    (None, "U", "D", "U", "D", "L", "U", "R", "U", "R", "R", "U", None),
    (None, "D", "L", "L", "D", "L", "R", "R", "U", "U", "U", "R", None),
    (None, None, "D", "L", "L", "U", "D", "D", "D", "U", "D", None, None),
    (None, None, None, "L", "D", "R", "D", "R", "R", "D", None, None, None),
    (None, None, None, None, None, "L", "D", "R", None, None, None, None, None),
    (None, None, None, None, None, None, "L", None, None, None, None, None, None),
    (None, None, None, None, "L", "L", "D", "R", "D", None, None, None, None),
    (None, None, None, "L", "D", "R", "D", "R", "D", "D", None, None, None),
    (None, None, None, None, None, "L", "L", "R", None, None, None, None, None),
    (None, None, None, None, None, None, "L", None, None, None, None, None, None),
)
FLOWER_SOLUTION = (
    (11, 5), (5, 2), (1, 9), (4, 11), (2, 10), (1, 3), (10, 9), (3, 11),
    (4, 1), (0, 5), (11, 7), (4, 2), (2, 9), (11, 6), (10, 4), (1, 8),
    (9, 4), (10, 8), (3, 10), (4, 10), (3, 9), (12, 6), (9, 8), (0, 6),
    (5, 10), (10, 3), (0, 7), (3, 1), (2, 8), (9, 5), (3, 8), (10, 6),
    (9, 7), (2, 2), (6, 9), (4, 9), (1, 6), (5, 3), (7, 7), (9, 6),
    (3, 2), (2, 3), (4, 8), (6, 8), (10, 7), (3, 3), (5, 8), (7, 5),
    (8, 6), (2, 6), (7, 6), (1, 7), (5, 4), (1, 5), (3, 7), (6, 4),
    (6, 7), (5, 9), (4, 4), (4, 3), (2, 5), (4, 5), (2, 7), (5, 7),
    (1, 4), (3, 6), (6, 6), (4, 7), (2, 4), (10, 5), (3, 4), (3, 5),
    (6, 3), (5, 6), (5, 5), (4, 6), (6, 5),
)

SUN_LAYOUT_SEED = 2026091902
SUN_COLOR_GRID = (
    (None, None, None, None, None, None, "ray", None, None, None, None, None, None),
    (None, None, None, "ray", None, None, "ray", None, None, "ray", None, None, None),
    (None, "ray", None, None, "ray", "ray", "ray", "ray", "ray", None, None, "ray", None),
    (None, None, None, "sun", "sun", "sun", "sun", "sun", "sun", "sun", None, None, None),
    (None, None, "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", None, None),
    (None, None, "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", None, None),
    (None, "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", None),
    (None, None, "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", "sun", None, None),
    (None, None, None, "sun", "sun", "sun", "sun", "sun", "sun", "sun", None, None, None),
    ("sky", "sky", "sky", "sky", "sky", "sky", "sky", "sky", "sky", "sky", "sky", "sky", "sky"),
    ("grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"),
    ("grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"),
    ("grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"),
)
SUN_ARROW_GRID = (
    (None, None, None, None, None, None, "L", None, None, None, None, None, None),
    (None, None, None, "L", None, None, "L", None, None, "L", None, None, None),
    (None, "U", None, None, "R", "R", "U", "R", "U", None, None, "R", None),
    (None, None, None, "U", "R", "U", "U", "U", "U", "R", None, None, None),
    (None, None, "U", "U", "U", "U", "U", "U", "U", "R", "U", None, None),
    (None, None, "U", "L", "L", "U", "L", "L", "R", "R", "R", None, None),
    (None, "L", "U", "L", "U", "D", "L", "L", "U", "R", "R", "U", None),
    (None, None, "L", "L", "L", "L", "L", "L", "R", "R", "R", None, None),
    (None, None, None, "L", "U", "D", "D", "R", "D", "R", None, None, None),
    ("L", "U", "U", "D", "U", "D", "D", "R", "R", "R", "D", "U", "R"),
    ("L", "L", "D", "L", "L", "L", "D", "D", "D", "R", "R", "U", "D"),
    ("L", "D", "D", "L", "D", "D", "D", "D", "L", "R", "D", "R", "R"),
    ("U", "D", "D", "L", "D", "D", "D", "D", "R", "D", "R", "D", "D"),
)
SUN_SOLUTION = (
    (12, 2), (8, 9), (2, 8), (0, 6), (11, 0), (7, 10), (3, 8), (12, 11),
    (12, 1), (1, 3), (4, 2), (5, 10), (1, 6), (12, 7), (3, 9), (5, 2),
    (10, 0), (2, 11), (4, 10), (12, 12), (2, 7), (12, 4), (9, 0), (2, 6),
    (6, 11), (11, 12), (11, 7), (1, 9), (12, 0), (2, 5), (7, 2), (11, 2),
    (3, 3), (7, 9), (12, 3), (12, 9), (5, 3), (2, 1), (12, 5), (2, 4),
    (11, 1), (9, 12), (3, 7), (11, 3), (7, 3), (12, 10), (10, 2), (3, 6),
    (10, 1), (12, 8), (3, 5), (12, 6), (10, 3), (7, 8), (10, 12), (6, 2),
    (4, 5), (10, 4), (11, 10), (5, 9), (9, 11), (11, 6), (5, 4), (3, 4),
    (11, 4), (10, 11), (11, 11), (10, 5), (5, 5), (11, 5), (10, 10), (7, 4),
    (4, 8), (4, 9), (9, 10), (6, 1), (7, 5), (4, 4), (10, 6), (9, 9),
    (9, 8), (9, 5), (11, 8), (6, 4), (4, 3), (9, 6), (8, 3), (6, 10),
    (9, 1), (8, 5), (5, 8), (6, 3), (10, 9), (7, 6), (8, 4), (10, 7),
    (10, 8), (6, 9), (9, 2), (7, 7), (5, 6), (11, 9), (4, 6), (8, 8),
    (4, 7), (9, 7), (5, 7), (6, 5), (8, 7), (8, 6), (6, 8), (6, 6),
    (9, 3), (9, 4), (6, 7),
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


LEVEL_NAMES = ("BEAD BALL", "FLOWER", "SUN")
LEVEL_FACTORIES = (create_tree_board, create_flower_board, create_sun_board)
