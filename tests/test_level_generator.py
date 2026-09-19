from src.board import Board
from src.level_generator import generate_solvable_arrow_grid, generate_solvable_layout


MASK = (
    (None, "pixel", None),
    ("pixel", "pixel", "pixel"),
    (None, "pixel", None),
)
LARGE_MASK = tuple(tuple("pixel" for _ in range(13)) for _ in range(13))


def _clear_in_solution_order(layout, mask=MASK):
    board = Board([list(row) for row in layout.arrow_grid], [list(row) for row in mask])
    for row, col in layout.solution:
        assert board.click(row, col).success
    assert board.is_cleared()
    return len(layout.solution)


def test_generator_is_deterministic_and_preserves_mask():
    first = generate_solvable_arrow_grid(MASK, seed=20260919)
    second = generate_solvable_arrow_grid(MASK, seed=20260919)

    assert first == second
    assert [cell is None for row in first for cell in row] == [
        cell is None for row in MASK for cell in row
    ]


def test_generated_grid_is_playable_and_uses_multiple_directions():
    layout = generate_solvable_layout(MASK, seed=9)

    assert _clear_in_solution_order(layout) == 5
    assert len({cell for row in layout.arrow_grid for cell in row if cell is not None}) >= 3


def test_large_mask_has_a_solvable_and_visibly_varied_layout():
    layout = generate_solvable_layout(LARGE_MASK, seed=2026091901)
    directions = [cell for row in layout.arrow_grid for cell in row if cell is not None]

    assert _clear_in_solution_order(layout, LARGE_MASK) == 169
    assert all(directions.count(direction) >= 5 for direction in {"U", "D", "L", "R"})
