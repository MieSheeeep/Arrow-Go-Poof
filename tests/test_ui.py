import pygame
import pytest

from src.board import Board
from src.game import Game
from src.levels import create_tree_board
from src.ui import (
    BACKGROUND,
    ARROW_SPRITES_PATH,
    COLOR_MAP,
    MENU_BACKGROUND_PATH,
    MENU_PANEL_COLOR,
    WORK_MAT_RECT,
    GridLayout,
    WINDOW_SIZE,
)
from src.ui import UI


def test_window_and_grid_layout_match_mvp_design():
    assert WINDOW_SIZE == (1200, 800)
    layout = GridLayout(origin=(260, 130), cell_size=48)

    assert layout.cell_at((260, 130), rows=12, cols=13) == (0, 0)
    assert layout.cell_at((307, 177), rows=12, cols=13) == (0, 0)
    assert layout.cell_at((308, 178), rows=12, cols=13) == (1, 1)
    assert layout.cell_at((259, 130), rows=12, cols=13) is None
    assert layout.cell_at((260 + 13 * 48, 130), rows=12, cols=13) is None


def test_grid_layout_returns_pixel_rect_for_cell():
    layout = GridLayout(origin=(260, 130), cell_size=48)
    rect = layout.cell_rect(2, 3)

    assert isinstance(rect, pygame.Rect)
    assert rect.topleft == (404, 226)
    assert rect.size == (48, 48)


@pytest.mark.parametrize("cell_size", [0, -1, 1.5, True, 801, 1201])
def test_grid_layout_rejects_invalid_cell_sizes(cell_size):
    with pytest.raises(ValueError):
        GridLayout(origin=(0, 0), cell_size=cell_size)


def test_known_material_colors_are_distinct():
    assert COLOR_MAP["flower"] != COLOR_MAP["leaf"]
    assert COLOR_MAP["leaf_light"] != COLOR_MAP["leaf"]


def test_ui_exposes_start_and_result_action_buttons():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R"]], [["leaf"]]), start_in_menu=True)
    ui = UI(screen, game)

    assert ui.start_rect().size == (260, 64)
    assert ui.result_action_rect().size == (220, 52)


def test_start_screen_draws_a_distinct_title_panel_and_start_button():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R"]], [["leaf"]]), start_in_menu=True)

    UI(screen, game).draw()

    assert screen.get_at((195, 130))[:3] == MENU_PANEL_COLOR
    assert screen.get_at((600, 515))[:3] == (105, 181, 78)
    assert screen.get_at((80, 80))[:3] != BACKGROUND


def test_main_menu_background_is_packaged_with_the_project():
    assert MENU_BACKGROUND_PATH.is_file()


def test_pixel_arrow_sprite_sheet_is_packaged_and_split_by_direction():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    ui = UI(screen, Game(create_tree_board))

    assert ARROW_SPRITES_PATH.is_file()
    assert set(ui.arrow_sprites) == {"U", "D", "L", "R"}
    assert all(sprite.get_size() == (40, 40) for sprite in ui.arrow_sprites.values())


def test_ui_scales_the_16_by_16_first_level_to_fit_the_play_area():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    ui = UI(screen, Game(create_tree_board))

    assert ui.layout.cell_size == 36
    assert ui.layout.origin == (312, 162)
    assert ui.cell_at((887, 737)) == (15, 15)
    assert ui.cell_at((888, 738)) is None
    assert WORK_MAT_RECT.contains(
        ui.layout.cell_rect(0, 0).union(ui.layout.cell_rect(15, 15))
    )


def test_gameplay_uses_the_same_desk_background_as_the_start_screen():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    ui = UI(screen, Game(create_tree_board))

    ui.draw()

    assert screen.get_at((20, 400))[:3] == ui.menu_background.get_at((20, 400))[:3]


def test_arrow_tiles_leave_their_rounded_corner_transparent():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    ui = UI(screen, Game(create_tree_board))
    ui.draw()
    row, col = next(
        (row, col)
        for row, grid_row in enumerate(ui.game.board.arrow_grid)
        for col, cell in enumerate(grid_row)
        if cell is not None
    )
    tile = ui.layout.cell_rect(row, col)

    assert screen.get_at(tile.topleft)[:3] == ui.menu_background.get_at(tile.topleft)[:3]


def test_hovered_arrow_tile_uses_a_bright_cyan_outline(monkeypatch):
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    ui = UI(screen, Game(create_tree_board))
    row, col = next(
        (row, col)
        for row, grid_row in enumerate(ui.game.board.arrow_grid)
        for col, cell in enumerate(grid_row)
        if cell is not None
    )
    tile = ui.layout.cell_rect(row, col)
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: tile.center)

    ui.draw()

    assert screen.get_at((tile.left + 1, tile.centery)).b > 220
