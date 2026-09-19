from src.levels import (
    FLOWER_ARROW_GRID,
    FLOWER_COLOR_GRID,
    FLOWER_LAYOUT_SEED,
    FLOWER_SOLUTION,
    LEVEL_FACTORIES,
    LEVEL_NAMES,
    SAMPLE_ARROW_GRID,
    SAMPLE_COLOR_GRID,
    SUN_ARROW_GRID,
    SUN_COLOR_GRID,
    SUN_LAYOUT_SEED,
    SUN_SOLUTION,
    TREE_ARROW_GRID,
    TREE_COLOR_GRID,
    create_sample_board,
    create_flower_board,
    create_sun_board,
    create_tree_board,
)
from src.level_generator import generate_solvable_layout


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


def test_tree_level_definitions_are_12_by_13_tuples():
    assert isinstance(TREE_ARROW_GRID, tuple)
    assert isinstance(TREE_COLOR_GRID, tuple)
    assert len(TREE_ARROW_GRID) == 12
    assert len(TREE_COLOR_GRID) == 12
    assert all(len(row) == 13 for row in TREE_ARROW_GRID)
    assert all(len(row) == 13 for row in TREE_COLOR_GRID)
    assert all(isinstance(row, tuple) for row in TREE_ARROW_GRID)
    assert all(isinstance(row, tuple) for row in TREE_COLOR_GRID)


def test_tree_level_arrow_and_color_masks_match():
    arrow_mask = tuple(cell is not None for row in TREE_ARROW_GRID for cell in row)
    color_mask = tuple(cell is not None for row in TREE_COLOR_GRID for cell in row)
    assert arrow_mask == color_mask


def test_tree_level_has_expected_top_and_trunk_cells():
    assert TREE_ARROW_GRID[0][6] == "U"
    assert TREE_COLOR_GRID[0][6] == "leaf_light"
    assert TREE_COLOR_GRID[8][6] == "trunk"


def test_tree_level_direction_layout_has_edges_and_internal_directions():
    assert TREE_ARROW_GRID[3][2] == "L"
    assert TREE_ARROW_GRID[3][10] == "R"
    assert TREE_ARROW_GRID[5][0] == "L"
    assert TREE_ARROW_GRID[5][12] == "R"
    assert TREE_ARROW_GRID[11][3] == "L"
    assert TREE_ARROW_GRID[11][4] == "D"
    assert TREE_ARROW_GRID[11][9] == "R"
    for row in TREE_ARROW_GRID[1:3]:
        assert all(cell == "U" for cell in row if cell is not None)
    for row in TREE_ARROW_GRID[3:8]:
        valid_cells = [cell for cell in row if cell is not None]
        assert valid_cells[0] == "L"
        assert valid_cells[-1] == "R"
        assert all(cell == "U" for cell in valid_cells[1:-1])
    assert TREE_ARROW_GRID[8][6] == "D"
    assert all(
        cell == "D"
        for row in TREE_ARROW_GRID[8:11]
        for cell in row
        if cell is not None
    )


def test_tree_board_factory_returns_independent_boards():
    first = create_tree_board()
    second = create_tree_board()
    first.arrow_grid[0][6] = "."
    first.color_grid[1][6] = "changed_leaf"
    first.color_grid[8][6] = "changed_trunk"
    assert second.arrow_grid[0][6] == "U"
    assert second.color_grid[1][6] == "leaf"
    assert second.color_grid[8][6] == "trunk"


def test_tree_factory_is_available_for_runtime_entry_point():
    board = create_tree_board()

    assert board.rows == 12
    assert board.cols == 13
    assert board.remaining_arrows() > 0


def _winning_sequence(factory):
    board = factory()
    path = []
    while True:
        available = [
            (row_index, col_index)
            for row_index, row in enumerate(board.arrow_grid)
            for col_index, cell in enumerate(row)
            if cell in {"U", "D", "L", "R"}
            and board.can_fly(row_index, col_index)
        ]
        if not available:
            return path if board.is_cleared() else None
        row_index, col_index = available[0]
        assert board.click(row_index, col_index).success
        path.append((row_index, col_index))


def _play_frozen_solution(factory, solution):
    board = factory()
    for row_index, col_index in solution:
        assert board.click(row_index, col_index).success
    return board.is_cleared()


def test_course_has_three_named_level_factories():
    assert len(LEVEL_FACTORIES) == 3
    assert len(LEVEL_NAMES) == 3
    assert all(factory().remaining_arrows() > 0 for factory in LEVEL_FACTORIES)


def test_extra_levels_use_all_four_arrow_directions():
    for grid in (FLOWER_ARROW_GRID, SUN_ARROW_GRID):
        arrows = {cell for row in grid for cell in row}
        assert {"U", "D", "L", "R"} <= arrows


def test_every_course_level_has_a_winning_sequence():
    sequence = _winning_sequence(create_tree_board)
    assert sequence is not None
    assert len(sequence) == create_tree_board().remaining_arrows()
    assert _play_frozen_solution(create_flower_board, FLOWER_SOLUTION)
    assert _play_frozen_solution(create_sun_board, SUN_SOLUTION)


def test_extra_level_factories_return_independent_boards():
    first = create_flower_board()
    second = create_flower_board()
    original_flower = second.arrow_grid[0][6]
    first.arrow_grid[0][6] = "."
    assert second.arrow_grid[0][6] == original_flower

    first = create_sun_board()
    second = create_sun_board()
    original_sun = second.arrow_grid[0][6]
    first.arrow_grid[0][6] = "."
    assert second.arrow_grid[0][6] == original_sun


def test_flower_and_sun_are_large_fixed_pixel_art_levels():
    flower = create_flower_board()
    sun = create_sun_board()

    assert flower.rows == flower.cols == 13
    assert sun.rows == sun.cols == 13
    assert flower.remaining_arrows() >= 70
    assert sun.remaining_arrows() >= 80
    assert FLOWER_COLOR_GRID[3][6] == "center"
    assert FLOWER_COLOR_GRID[10][6] == "stem"
    assert SUN_COLOR_GRID[4][6] == "sun"
    assert SUN_COLOR_GRID[11][0] == "grass"


def test_frozen_art_layouts_match_their_generation_seeds():
    flower = generate_solvable_layout(FLOWER_COLOR_GRID, FLOWER_LAYOUT_SEED)
    sun = generate_solvable_layout(SUN_COLOR_GRID, SUN_LAYOUT_SEED)
    assert FLOWER_ARROW_GRID == flower.arrow_grid
    assert FLOWER_SOLUTION == flower.solution
    assert SUN_ARROW_GRID == sun.arrow_grid
    assert SUN_SOLUTION == sun.solution
