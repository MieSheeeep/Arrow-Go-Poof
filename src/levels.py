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


# The supplied Diamond Sword project is a 16×16 canvas.  Its three sampled
# bead colours are used here in a fixed, recognizable sword silhouette.
DIAMOND_SWORD_LAYOUT_SEED = 2026092001
_DIAMOND_SWORD_PIXEL_COLORS = {
    "K": "sword_outline",
    "T": "sword_teal",
    "L": "sword_highlight",
}
_DIAMOND_SWORD_PIXEL_ROWS = (
    ".............K..",
    "............KTK.",
    "...........KLTTK",
    "..........KLTTK.",
    ".........KLTTK..",
    "........KLTTK...",
    ".......KLTTK....",
    "......KLTTK.....",
    ".....KLTTK......",
    "....KLTTK.......",
    "...KLTTK........",
    "..KLTTK.........",
    ".KLLLLLK........",
    "..KTTTK.........",
    "...KTTK.........",
    "....KK..........",
)
DIAMOND_SWORD_COLOR_GRID = tuple(
    tuple(None if pixel == "." else _DIAMOND_SWORD_PIXEL_COLORS[pixel] for pixel in row)
    for row in _DIAMOND_SWORD_PIXEL_ROWS
)
DIAMOND_SWORD_ARROW_GRID = (
    (None, None, None, None, None, None, None, None, None, None, None, None, None, "U", None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, "U", "L", "U", None),
    (None, None, None, None, None, None, None, None, None, None, None, "L", "L", "U", "R", "D"),
    (None, None, None, None, None, None, None, None, None, None, "U", "L", "U", "R", "R", None),
    (None, None, None, None, None, None, None, None, None, "L", "U", "R", "R", "R", None, None),
    (None, None, None, None, None, None, None, None, "L", "L", "D", "D", "U", None, None, None),
    (None, None, None, None, None, None, None, "D", "U", "L", "R", "R", None, None, None, None),
    (None, None, None, None, None, None, "U", "L", "L", "U", "R", None, None, None, None, None),
    (None, None, None, None, None, "U", "U", "L", "R", "R", None, None, None, None, None, None),
    (None, None, None, None, "L", "L", "D", "D", "R", None, None, None, None, None, None, None),
    (None, None, None, "L", "L", "R", "R", "D", None, None, None, None, None, None, None, None),
    (None, None, "U", "U", "U", "R", "R", None, None, None, None, None, None, None, None, None),
    (None, "D", "U", "D", "U", "D", "D", "R", None, None, None, None, None, None, None, None),
    (None, None, "D", "L", "D", "D", "D", None, None, None, None, None, None, None, None, None),
    (None, None, None, "L", "R", "D", "D", None, None, None, None, None, None, None, None, None),
    (None, None, None, None, "L", "D", None, None, None, None, None, None, None, None, None, None),
)
DIAMOND_SWORD_SOLUTION = (
    (15, 4), (12, 1), (3, 10), (6, 11), (5, 8), (7, 6), (15, 5), (12, 7),
    (9, 4), (1, 12), (14, 6), (11, 6), (6, 10), (0, 13), (2, 15), (7, 7),
    (7, 10), (10, 7), (8, 5), (10, 3), (13, 2), (1, 13), (3, 14), (4, 10),
    (2, 11), (14, 5), (11, 2), (10, 6), (9, 7), (1, 14), (13, 3), (3, 13),
    (2, 13), (13, 6), (2, 12), (2, 14), (14, 4), (12, 6), (11, 3), (14, 3),
    (4, 13), (8, 6), (10, 4), (12, 3), (8, 7), (11, 4), (8, 9), (13, 5),
    (12, 5), (3, 12), (10, 5), (3, 11), (4, 9), (12, 4), (5, 11), (4, 12),
    (11, 5), (13, 4), (5, 12), (5, 9), (6, 7), (9, 5), (6, 8), (4, 11),
    (5, 10), (12, 2), (6, 9), (9, 8), (9, 6), (7, 8), (7, 9), (8, 8),
)


def create_diamond_sword_board() -> Board:
    """Return a fresh Board for the Diamond Sword pixel pattern."""
    return Board(
        [list(row) for row in DIAMOND_SWORD_ARROW_GRID],
        [list(row) for row in DIAMOND_SWORD_COLOR_GRID],
    )


# The supplied Enchanted Golden Apple project is already a complete 16×16
# bead image.  Its palette is reduced to seven readable in-game materials.
ENCHANTED_APPLE_LAYOUT_SEED = 2026092005
_ENCHANTED_APPLE_PIXEL_COLORS = {
    "A": "apple_gold",
    "B": "apple_peach",
    "C": "apple_gold",
    "D": "apple_shadow",
    "E": "apple_light",
    "F": "apple_red",
    "G": "apple_light",
    "H": "apple_purple",
    "I": "apple_white",
    "J": "apple_red",
    "K": "apple_purple",
    "L": "apple_purple",
    "M": "apple_outline",
    "N": "apple_red",
    "O": "apple_peach",
    "P": "apple_peach",
    "Q": "apple_gold",
    "R": "apple_purple",
    "S": "apple_red",
    "T": "apple_peach",
    "U": "apple_light",
    "V": "apple_gold",
    "W": "apple_gold",
    "X": "apple_outline",
    "Y": "apple_gold",
    "Z": "apple_red",
}
_ENCHANTED_APPLE_PIXEL_ROWS = (
    "................",
    "........K.......",
    ".......NL.......",
    ".......F........",
    "....DDFHHH......",
    "..DAIAMSBTHF....",
    ".DAEGIIIGGOFF...",
    ".DAEEEEEUBGAF...",
    ".DCVEBEBBBGPF...",
    ".JCCBECABWGPH...",
    ".XQCCCABAAGAR...",
    "..JQCEAAABOL....",
    "..JDCACBBYNR....",
    "...MDCDDAZL.....",
    "....MJFFKK......",
    "................",
)
ENCHANTED_APPLE_COLOR_GRID = tuple(
    tuple(None if pixel == "." else _ENCHANTED_APPLE_PIXEL_COLORS[pixel] for pixel in row)
    for row in _ENCHANTED_APPLE_PIXEL_ROWS
)
ENCHANTED_APPLE_ARROW_GRID = (
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, "L", None, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, "L", "R", None, None, None, None, None, None, None),
    (None, None, None, None, None, None, None, "U", None, None, None, None, None, None, None, None),
    (None, None, None, None, "U", "U", "R", "U", "U", "R", None, None, None, None, None, None),
    (None, None, "L", "U", "L", "U", "L", "U", "U", "U", "U", "U", None, None, None, None),
    (None, "L", "L", "U", "L", "L", "U", "L", "U", "R", "U", "R", "U", None, None, None),
    (None, "U", "L", "U", "U", "U", "R", "D", "R", "U", "U", "R", "R", None, None, None),
    (None, "L", "D", "L", "U", "U", "U", "D", "R", "R", "U", "R", "R", None, None, None),
    (None, "L", "L", "R", "U", "U", "D", "D", "R", "R", "D", "D", "D", None, None, None),
    (None, "L", "L", "L", "L", "D", "R", "R", "D", "R", "R", "D", "R", None, None, None),
    (None, None, "L", "L", "L", "D", "L", "D", "R", "R", "D", "R", None, None, None, None),
    (None, None, "D", "L", "L", "D", "D", "L", "R", "R", "D", "D", None, None, None, None),
    (None, None, None, "L", "D", "D", "D", "D", "R", "D", "R", None, None, None, None, None),
    (None, None, None, None, "L", "D", "D", "D", "R", "D", None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
)
ENCHANTED_APPLE_SOLUTION = (
    (6, 1), (14, 7), (4, 5), (10, 12), (13, 10), (2, 7), (5, 3), (14, 9),
    (14, 6), (14, 4), (5, 5), (7, 12), (5, 2), (6, 12), (7, 11), (13, 7),
    (13, 3), (7, 1), (13, 6), (14, 8), (6, 2), (2, 8), (4, 4), (14, 5),
    (4, 9), (5, 10), (5, 4), (13, 9), (11, 2), (13, 8), (13, 5), (3, 7),
    (12, 2), (8, 12), (5, 11), (9, 1), (9, 12), (6, 11), (6, 3), (1, 8),
    (8, 11), (7, 2), (4, 8), (12, 10), (6, 10), (11, 10), (11, 11), (10, 1),
    (7, 10), (5, 6), (12, 11), (11, 9), (6, 4), (7, 4), (10, 11), (10, 10),
    (8, 4), (8, 1), (6, 9), (13, 4), (12, 9), (6, 5), (4, 7), (9, 10),
    (9, 4), (9, 2), (12, 6), (11, 8), (4, 6), (9, 11), (12, 3), (8, 10),
    (12, 8), (6, 6), (10, 2), (8, 2), (10, 3), (12, 5), (8, 9), (5, 9),
    (9, 9), (5, 8), (10, 8), (11, 3), (12, 4), (7, 9), (10, 9), (11, 5),
    (12, 7), (10, 5), (7, 8), (5, 7), (10, 7), (6, 8), (11, 7), (8, 3),
    (6, 7), (9, 7), (9, 8), (7, 5), (11, 4), (8, 5), (8, 7), (10, 6),
    (7, 7), (7, 6), (8, 6), (11, 6), (10, 4), (9, 6), (8, 8), (9, 5),
    (9, 3), (7, 3),
)


def create_enchanted_apple_board() -> Board:
    """Return a fresh Board for the supplied Enchanted Golden Apple pattern."""
    return Board(
        [list(row) for row in ENCHANTED_APPLE_ARROW_GRID],
        [list(row) for row in ENCHANTED_APPLE_COLOR_GRID],
    )


# The supplied Moon Hello Kitty bead project is downsampled at design time to
# an 18×17 grid.  Normal play uses these frozen rows, never runtime sampling.
HELLO_KITTY_LAYOUT_SEED = 2026092003
_HELLO_KITTY_PIXEL_COLORS = {
    "W": "kitty_white",
    "Y": "moon_gold",
    "K": "kitty_outline",
    "D": "moon_shadow",
    "G": "kitty_gray",
    "R": "kitty_bow",
    "P": "kitty_pink",
}
_HELLO_KITTY_PIXEL_ROWS = (
    "........DDDD......",
    "..........DYYD....",
    "............YYYD..",
    "....K.....K..KDY..",
    "...KGWKKKKRKKWKYY.",
    "...KWWWGGGKKKWKKYD",
    "...KGWWWWWGGKRRKYY",
    "...KWWWWWWWWWRRKYY",
    "D..KWWWWWWWWWGGKYY",
    "D.KGWWKWWWWWKWWKYY",
    "DDKKWWKWWYWKKWKKYY",
    "DYDKWWPWWWWWPWKKYY",
    ".YYYKWWWWKKWWWKYYY",
    ".DYYYDKWWKWWDYYYY.",
    "..DYYYYKKYKYYYYY..",
    "...DYYYYYYYYYYY...",
    ".....YYYYYYYYY....",
)
HELLO_KITTY_COLOR_GRID = tuple(
    tuple(None if pixel == "." else _HELLO_KITTY_PIXEL_COLORS[pixel] for pixel in row)
    for row in _HELLO_KITTY_PIXEL_ROWS
)
HELLO_KITTY_ARROW_GRID = (
    (None, None, None, None, None, None, None, None, "U", "L", "R", "R", None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, "R", "U", "R", "R", None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None, None, None, "U", "U", "U", "R", None, None),
    (None, None, None, None, "L", None, None, None, None, None, "U", None, None, "U", "U", "L", None, None),
    (None, None, None, "L", "U", "U", "U", "L", "U", "R", "U", "U", "U", "U", "U", "R", "U", None),
    (None, None, None, "U", "L", "U", "U", "L", "U", "U", "R", "U", "R", "R", "R", "U", "R", "R"),
    (None, None, None, "L", "L", "U", "U", "L", "L", "L", "U", "R", "U", "U", "U", "D", "R", "R"),
    (None, None, None, "L", "U", "U", "U", "L", "U", "U", "U", "L", "U", "R", "R", "R", "R", "D"),
    ("L", None, None, "U", "D", "L", "U", "L", "U", "L", "U", "R", "U", "R", "R", "D", "R", "R"),
    ("L", None, "U", "L", "L", "U", "U", "L", "L", "L", "U", "U", "U", "R", "R", "R", "R", "R"),
    ("L", "D", "L", "L", "L", "D", "U", "L", "D", "D", "U", "L", "U", "R", "U", "R", "R", "D"),
    ("D", "L", "U", "D", "L", "L", "L", "D", "D", "D", "R", "D", "D", "D", "R", "D", "D", "R"),
    (None, "L", "L", "L", "D", "L", "D", "L", "L", "R", "R", "R", "D", "R", "R", "D", "R", "D"),
    (None, "L", "D", "D", "L", "L", "D", "L", "L", "D", "R", "D", "D", "D", "D", "R", "D", None),
    (None, None, "D", "L", "D", "L", "L", "L", "D", "R", "D", "D", "R", "R", "R", "D", None, None),
    (None, None, None, "L", "D", "D", "D", "D", "D", "D", "D", "D", "D", "R", "R", None, None, None),
    (None, None, None, None, None, "L", "D", "D", "L", "D", "R", "D", "R", "D", None, None, None, None),
)
HELLO_KITTY_SOLUTION = (
    (8, 17), (2, 14), (12, 1), (13, 16), (4, 3), (16, 11), (3, 14), (1, 13),
    (14, 15), (11, 17), (6, 3), (2, 13), (0, 8), (0, 11), (10, 0), (16, 13),
    (3, 13), (9, 0), (16, 12), (15, 11), (15, 4), (7, 3), (2, 15), (9, 2),
    (9, 17), (14, 2), (14, 3), (4, 6), (11, 0), (13, 1), (14, 14), (5, 6),
    (1, 12), (11, 1), (1, 11), (12, 17), (10, 1), (5, 3), (10, 2), (1, 10),
    (0, 9), (4, 8), (10, 17), (9, 16), (4, 5), (14, 4), (0, 10), (10, 3),
    (7, 17), (16, 5), (3, 10), (6, 17), (9, 3), (14, 13), (13, 2), (6, 6),
    (12, 2), (11, 2), (7, 16), (16, 6), (5, 17), (5, 5), (16, 9), (12, 3),
    (3, 4), (16, 7), (6, 5), (16, 10), (15, 3), (2, 12), (13, 15), (12, 15),
    (16, 8), (7, 6), (7, 15), (15, 9), (13, 3), (3, 15), (8, 6), (12, 16),
    (13, 4), (11, 15), (12, 14), (4, 16), (8, 3), (10, 16), (11, 3), (6, 4),
    (9, 6), (15, 12), (15, 14), (8, 0), (4, 4), (15, 5), (9, 15), (13, 5),
    (10, 6), (11, 16), (11, 4), (10, 15), (14, 5), (4, 10), (15, 7), (5, 16),
    (15, 6), (6, 16), (4, 13), (5, 4), (7, 4), (9, 4), (15, 10), (4, 15),
    (7, 5), (15, 8), (6, 7), (9, 14), (5, 15), (15, 13), (14, 6), (13, 6),
    (12, 4), (10, 4), (14, 12), (4, 12), (4, 7), (5, 14), (14, 10), (5, 8),
    (8, 4), (8, 16), (4, 14), (11, 5), (5, 13), (4, 11), (13, 12), (14, 7),
    (5, 11), (12, 12), (8, 5), (5, 12), (6, 8), (7, 8), (8, 15), (4, 9),
    (12, 13), (7, 7), (12, 6), (8, 8), (14, 11), (5, 10), (6, 14), (13, 7),
    (6, 10), (14, 8), (8, 14), (12, 5), (8, 7), (14, 9), (13, 11), (9, 5),
    (6, 15), (7, 10), (12, 7), (9, 13), (8, 13), (5, 7), (6, 13), (10, 5),
    (11, 14), (8, 10), (12, 8), (13, 14), (6, 9), (12, 11), (9, 10), (13, 9),
    (11, 6), (12, 10), (5, 9), (13, 13), (9, 7), (13, 10), (11, 12), (6, 12),
    (7, 9), (11, 7), (10, 7), (6, 11), (13, 8), (7, 12), (11, 8), (12, 9),
    (7, 14), (10, 14), (10, 8), (8, 9), (7, 13), (8, 12), (7, 11), (11, 9),
    (8, 11), (10, 10), (9, 8), (11, 13), (9, 11), (9, 9), (10, 9), (10, 13),
    (9, 12), (11, 11), (11, 10), (10, 11), (10, 12),
)


def create_hello_kitty_board() -> Board:
    """Return a fresh Board for the Moon Hello Kitty pixel pattern."""
    return Board(
        [list(row) for row in HELLO_KITTY_ARROW_GRID],
        [list(row) for row in HELLO_KITTY_COLOR_GRID],
    )


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


LEVEL_STAR_THRESHOLDS = (
    (90.0, 150.0),  # ENCHANTED APPLE
    (80.0, 130.0),  # BEAD BALL
    (150.0, 240.0),  # MOON KITTY
)

LEVEL_NAMES = ("ENCHANTED APPLE", "BEAD BALL", "MOON KITTY")
LEVEL_FACTORIES = (
    create_enchanted_apple_board,
    create_tree_board,
    create_hello_kitty_board,
)
