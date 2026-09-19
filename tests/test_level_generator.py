from src.board import Board
from src.level_generator import generate_solvable_arrow_grid


MASK = (
    (None, "pixel", None),
    ("pixel", "pixel", "pixel"),
    (None, "pixel", None),
)


def _clear_in_scan_order(grid):
    board = Board([list(row) for row in grid], [list(row) for row in MASK])
    moves = 0
    while not board.is_cleared():
        available = [
            (row, col)
            for row, values in enumerate(board.arrow_grid)
            for col, cell in enumerate(values)
            if cell in {"U", "D", "L", "R"} and board.can_fly(row, col)
        ]
        assert available
        assert board.click(*available[0]).success
        moves += 1
    return moves


def test_generator_is_deterministic_and_preserves_mask():
    first = generate_solvable_arrow_grid(MASK, seed=20260919)
    second = generate_solvable_arrow_grid(MASK, seed=20260919)

    assert first == second
    assert [cell is None for row in first for cell in row] == [
        cell is None for row in MASK for cell in row
    ]


def test_generated_grid_is_playable_and_uses_multiple_directions():
    grid = generate_solvable_arrow_grid(MASK, seed=9)

    assert _clear_in_scan_order(grid) == 5
    assert len({cell for row in grid for cell in row if cell is not None}) >= 3
