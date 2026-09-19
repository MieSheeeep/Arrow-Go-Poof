import pygame
import pytest

from src.board import Board
from src.game import Game
from src.ui import BACKGROUND, COLOR_MAP, HUD_COLOR, MENU_BACKGROUND_PATH, GridLayout, WINDOW_SIZE
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

    assert screen.get_at((195, 130))[:3] == HUD_COLOR
    assert screen.get_at((600, 515))[:3] == (105, 181, 78)
    assert screen.get_at((80, 80))[:3] != BACKGROUND


def test_main_menu_background_is_packaged_with_the_project():
    assert MENU_BACKGROUND_PATH.is_file()
