from copy import deepcopy

import pytest

from src.board import Board


def make_board(arrow_grid):
    color_grid = [
        [None if cell is None else f"color-{row}-{col}" for col, cell in enumerate(line)]
        for row, line in enumerate(arrow_grid)
    ]
    return Board(arrow_grid, color_grid)


def test_board_copies_input_grids():
    arrows = [["R", "."]]
    colors = [["red", "blue"]]
    original_arrows = deepcopy(arrows)
    original_colors = deepcopy(colors)

    board = Board(arrows, colors)
    board.arrow_grid[0][0] = "."
    board.color_grid[0][0] = "changed"

    assert arrows == original_arrows
    assert colors == original_colors


def test_cell_queries_are_safe():
    board = make_board([[None, "U", "."]])

    assert board.in_bounds(0, 0) is True
    assert board.in_bounds(-1, 0) is False
    assert board.in_bounds(0, 3) is False
    assert board.in_bounds(True, 0) is False
    assert board.get_cell(0, 1) == "U"
    assert board.get_cell(-1, 1) is None
    assert board.is_arrow(0, 1) is True
    assert board.is_arrow(0, 0) is False
    assert board.is_arrow(0, 2) is False


@pytest.mark.parametrize(
    ("arrows", "colors"),
    [
        ([], []),
        ([[]], [[]]),
        ([["R"], ["L", "U"]], [["a"], ["b", "c"]]),
        ([["R"]], [["a"], ["b"]]),
        ([["X"]], [["a"]]),
        ([[None]], [["a"]]),
        ([["R"]], [[None]]),
    ],
)
def test_invalid_level_configuration_raises_value_error(arrows, colors):
    with pytest.raises(ValueError):
        Board(arrows, colors)
