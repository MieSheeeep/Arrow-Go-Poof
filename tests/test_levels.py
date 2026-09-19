from src.levels import (
    ENCHANTED_APPLE_ARROW_GRID,
    ENCHANTED_APPLE_COLOR_GRID,
    ENCHANTED_APPLE_LAYOUT_SEED,
    ENCHANTED_APPLE_SOLUTION,
    HELLO_KITTY_ARROW_GRID,
    HELLO_KITTY_COLOR_GRID,
    HELLO_KITTY_LAYOUT_SEED,
    HELLO_KITTY_SOLUTION,
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
    TREE_LAYOUT_SEED,
    TREE_SOLUTION,
    create_sample_board,
    create_enchanted_apple_board,
    create_flower_board,
    create_hello_kitty_board,
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


def test_first_level_definitions_are_16_by_16_tuples():
    assert isinstance(TREE_ARROW_GRID, tuple)
    assert isinstance(TREE_COLOR_GRID, tuple)
    assert len(TREE_ARROW_GRID) == 16
    assert len(TREE_COLOR_GRID) == 16
    assert all(len(row) == 16 for row in TREE_ARROW_GRID)
    assert all(len(row) == 16 for row in TREE_COLOR_GRID)
    assert all(isinstance(row, tuple) for row in TREE_ARROW_GRID)
    assert all(isinstance(row, tuple) for row in TREE_COLOR_GRID)


def test_tree_level_arrow_and_color_masks_match():
    arrow_mask = tuple(cell is not None for row in TREE_ARROW_GRID for cell in row)
    color_mask = tuple(cell is not None for row in TREE_COLOR_GRID for cell in row)
    assert arrow_mask == color_mask


def test_first_level_uses_the_supplied_bead_ball_pixel_pattern():
    assert TREE_COLOR_GRID[2][6] == "ball_outline"
    assert TREE_COLOR_GRID[4][6] == "ball_shine"
    assert TREE_COLOR_GRID[8][7] == "ball_white"
    assert TREE_COLOR_GRID[9][7] == "ball_gray"


def test_first_level_uses_all_four_arrow_directions():
    arrows = {cell for row in TREE_ARROW_GRID for cell in row if cell is not None}
    assert arrows == {"U", "D", "L", "R"}


def test_tree_board_factory_returns_independent_boards():
    first = create_tree_board()
    second = create_tree_board()
    first.arrow_grid[2][6] = "."
    first.color_grid[2][6] = "changed_outline"
    assert second.arrow_grid[2][6] == "U"
    assert second.color_grid[2][6] == "ball_outline"


def test_tree_factory_is_available_for_runtime_entry_point():
    board = create_tree_board()

    assert board.rows == 16
    assert board.cols == 16
    assert board.remaining_arrows() == 112


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


def test_runtime_campaign_uses_apple_ball_and_hello_kitty_in_order():
    assert LEVEL_NAMES == ("ENCHANTED APPLE", "BEAD BALL", "MOON KITTY")
    assert LEVEL_FACTORIES == (
        create_enchanted_apple_board,
        create_tree_board,
        create_hello_kitty_board,
    )
    assert len(ENCHANTED_APPLE_COLOR_GRID) == len(ENCHANTED_APPLE_ARROW_GRID) == 16
    assert len(HELLO_KITTY_COLOR_GRID) == len(HELLO_KITTY_ARROW_GRID) == 17
    assert len(HELLO_KITTY_COLOR_GRID[0]) == len(HELLO_KITTY_ARROW_GRID[0]) == 18
    assert _play_frozen_solution(create_enchanted_apple_board, ENCHANTED_APPLE_SOLUTION)
    assert _play_frozen_solution(create_hello_kitty_board, HELLO_KITTY_SOLUTION)
    apple = generate_solvable_layout(ENCHANTED_APPLE_COLOR_GRID, ENCHANTED_APPLE_LAYOUT_SEED)
    kitty = generate_solvable_layout(HELLO_KITTY_COLOR_GRID, HELLO_KITTY_LAYOUT_SEED)
    assert apple.arrow_grid == ENCHANTED_APPLE_ARROW_GRID
    assert kitty.arrow_grid == HELLO_KITTY_ARROW_GRID


def test_extra_levels_use_all_four_arrow_directions():
    for grid in (FLOWER_ARROW_GRID, SUN_ARROW_GRID):
        arrows = {cell for row in grid for cell in row}
        assert {"U", "D", "L", "R"} <= arrows


def test_every_course_level_has_a_winning_sequence():
    assert _play_frozen_solution(create_tree_board, TREE_SOLUTION)
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
    tree = generate_solvable_layout(TREE_COLOR_GRID, TREE_LAYOUT_SEED)
    flower = generate_solvable_layout(FLOWER_COLOR_GRID, FLOWER_LAYOUT_SEED)
    sun = generate_solvable_layout(SUN_COLOR_GRID, SUN_LAYOUT_SEED)
    assert TREE_ARROW_GRID == tree.arrow_grid
    assert TREE_SOLUTION == tree.solution
    assert FLOWER_ARROW_GRID == flower.arrow_grid
    assert FLOWER_SOLUTION == flower.solution
    assert SUN_ARROW_GRID == sun.arrow_grid
    assert SUN_SOLUTION == sun.solution
