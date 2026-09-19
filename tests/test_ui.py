import pygame
import pytest

from src.ui import COLOR_MAP, GridLayout, WINDOW_SIZE


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
