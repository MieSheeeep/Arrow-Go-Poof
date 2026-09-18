from src.levels import SAMPLE_ARROW_GRID, SAMPLE_COLOR_GRID, create_sample_board


def test_sample_board_factory_returns_independent_boards():
    first = create_sample_board()
    second = create_sample_board()
    first.arrow_grid[0][2] = "."
    assert second.arrow_grid[0][2] == "U"
    assert first.color_grid == second.color_grid
    first.color_grid[0][2] = "changed"
    assert second.color_grid[0][2] == "leaf_light"


def test_sample_level_definitions_are_tuples_of_tuples():
    assert isinstance(SAMPLE_ARROW_GRID, tuple)
    assert all(isinstance(row, tuple) for row in SAMPLE_ARROW_GRID)
    assert isinstance(SAMPLE_COLOR_GRID, tuple)
    assert all(isinstance(row, tuple) for row in SAMPLE_COLOR_GRID)
