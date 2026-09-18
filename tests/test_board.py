from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest

from src.board import Board, MoveResult


class UnhashableStr(str):
    __hash__ = None


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


def test_move_result_is_frozen():
    result = MoveResult(True, 0, 0, "R", "clear")

    with pytest.raises(FrozenInstanceError):
        result.success = False


@pytest.mark.parametrize(
    ("arrows", "colors"),
    [
        ([], []),
        ([[]], [[]]),
        ([["R"], ["L", "U"]], [["a"], ["b", "c"]]),
        ([["R"]], [["a"], ["b"]]),
        ([["X"]], [["a"]]),
        ([[[]]], [["red"]]),
        ([[UnhashableStr("R")]], [["red"]]),
        ([[None]], [["a"]]),
        ([["R"]], [[None]]),
    ],
)
def test_invalid_level_configuration_raises_value_error(arrows, colors):
    with pytest.raises(ValueError):
        Board(arrows, colors)


def test_arrow_can_fly_across_open_cells_to_boundary():
    board = make_board([["R", ".", "."]])

    assert board.can_fly(0, 0) is True


def test_adjacent_arrow_blocks_flight():
    board = make_board([["R", "U"]])

    assert board.can_fly(0, 0) is False


def test_distant_arrow_blocks_flight_across_cleared_cells():
    board = make_board([["R", ".", ".", "U"]])

    assert board.can_fly(0, 0) is False


def test_up_arrow_at_top_edge_does_not_wrap_to_last_row():
    board = make_board([["U"], ["D"]])

    assert board.can_fly(0, 0) is True


def test_none_cell_ends_irregular_puzzle_region():
    board = make_board([["R", None, "U"]])

    assert board.can_fly(0, 0) is True


def test_cleared_cell_is_traversable():
    board = make_board([["R", ".", "."]])

    assert board.can_fly(0, 0) is True


@pytest.mark.parametrize("row, col", [(-1, 0), (0, 3), (0, 0), (0, 1)])
def test_non_arrow_positions_cannot_fly(row, col):
    board = make_board([[None, ".", "R"]])

    assert board.can_fly(row, col) is False
