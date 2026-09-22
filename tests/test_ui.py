import pygame
import pytest

from src.animation import FlyOutAnimation, HeartLossAnimation, StarRevealAnimation
from src.board import Board
from src.game import Game
from src.levels import create_tree_board
from src.ui import (
    ARROW_CARD_ALPHA,
    ARROW_COLOR,
    ARROW_TILE,
    BACKGROUND,
    COLOR_MAP,
    COVER_START_RECT,
    HOVERED_ARROW_CARD_ALPHA,
    MENU_BACKGROUND_PATH,
    MENU_PANEL_COLOR,
    BUTTON_STATES_PATH,
    BUTTON_SPRITE_CROPS,
    HEARTS_PATH,
    PAUSE_BUTTON_PATH,
    PAUSE_PANEL_PATH,
    RATING_STARS_PATH,
    REVEAL_GLOW_DURATION,
    TOP_STATUS_BAR_PATH,
    WORK_MAT_RECT,
    WORK_MAT_COLOR,
    GridLayout,
    WINDOW_SIZE,
    format_elapsed_time,
    fit_surface,
    rating_star_points,
    remove_isolated_artifacts,
    reveal_glow_strength,
    countdown_color,
    format_countdown_time,
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


def test_arrow_cards_are_more_solid_but_hover_remains_more_transparent():
    assert ARROW_TILE == WORK_MAT_COLOR
    assert ARROW_CARD_ALPHA == 140
    assert HOVERED_ARROW_CARD_ALPHA == 105
    assert ARROW_CARD_ALPHA > HOVERED_ARROW_CARD_ALPHA


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [(0.0, "00:00.00"), (9.5, "00:09.50"), (65.125, "01:05.12")],
)
def test_format_elapsed_time(seconds, expected):
    assert format_elapsed_time(seconds) == expected


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [(0.0, "00:00"), (9.5, "00:09"), (65.125, "01:05")],
)
def test_format_countdown_time(seconds, expected):
    assert format_countdown_time(seconds) == expected


def test_countdown_color_steps_from_calm_to_urgent():
    assert countdown_color(40.0) == (114, 204, 132)
    assert countdown_color(20.0) == (248, 188, 81)
    assert countdown_color(10.0) == (241, 94, 100)


def test_reveal_glow_strength_is_immediate_then_fades_to_zero():
    animation = FlyOutAnimation(0, 0, "R")

    assert reveal_glow_strength(animation) == 1.0
    animation.update(REVEAL_GLOW_DURATION / 2)
    assert reveal_glow_strength(animation) == pytest.approx(0.5)
    animation.update(REVEAL_GLOW_DURATION / 2)
    assert reveal_glow_strength(animation) == 0.0


def test_successful_flyout_immediately_brightens_the_revealed_pixel():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R", "R"]], [["ball_red", "ball_red"]]))
    ui = UI(screen, game)

    game.click(0, 1)
    ui.draw()

    rect = ui.layout.cell_rect(0, 1)
    pixel = screen.get_at((rect.left + 5, rect.centery))[:3]
    assert sum(pixel) > sum(COLOR_MAP["ball_red"])


def test_hud_draws_the_heart_loss_feedback_above_the_static_life_icons(monkeypatch):
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R", "U"]], [["leaf", "leaf"]]))
    ui = UI(screen, game)
    game.click(0, 0)
    calls = []
    monkeypatch.setattr(ui, "_draw_heart_loss", lambda animation: calls.append(animation))

    ui.draw()

    assert len(calls) == 1
    assert isinstance(calls[0], HeartLossAnimation)


def test_result_panel_draws_the_staggered_star_feedback(monkeypatch):
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R"]], [["leaf"]]))
    ui = UI(screen, game)
    game.click(0, 0)
    calls = []
    monkeypatch.setattr(ui, "_draw_result_stars", lambda panel: calls.append(panel))

    ui.draw()

    assert len(calls) == 1
    assert any(isinstance(animation, StarRevealAnimation) for animation in game.animations)


def test_rating_star_points_create_a_five_point_polygon():
    points = rating_star_points((20, 20), outer_radius=10, inner_radius=4)

    assert len(points) == 10
    assert points[0] == (20, 10)
    assert points[1] != points[0]


def test_remove_isolated_artifacts_keeps_the_main_component_only():
    surface = pygame.Surface((40, 20), pygame.SRCALPHA)
    pygame.draw.rect(surface, (255, 255, 255, 255), (2, 2, 12, 12))
    surface.set_at((30, 10), (255, 220, 104, 255))

    cleaned = remove_isolated_artifacts(surface, minimum_pixels=16)

    assert cleaned.get_at((5, 5)).a == 255
    assert cleaned.get_at((30, 10)).a == 0


def test_gameplay_and_result_controls_have_distinct_hit_areas():
    pygame.font.init()
    ui = UI(pygame.Surface(WINDOW_SIZE), Game(create_tree_board))
    rects = [
        ui.restart_rect(),
        ui.menu_rect(),
        ui.result_primary_rect(),
        ui.result_retry_rect(),
        ui.result_menu_rect(),
    ]

    assert all(rect.width > 0 and rect.height > 0 for rect in rects)
    assert not ui.restart_rect().colliderect(ui.menu_rect())
    assert not ui.result_primary_rect().colliderect(ui.result_retry_rect())
    assert not ui.result_retry_rect().colliderect(ui.result_menu_rect())


def test_supplied_pixel_ui_assets_are_packaged_with_the_game():
    for asset_path in (
        TOP_STATUS_BAR_PATH,
        BUTTON_STATES_PATH,
        RATING_STARS_PATH,
        HEARTS_PATH,
        PAUSE_BUTTON_PATH,
        PAUSE_PANEL_PATH,
    ):
        assert asset_path.is_file()


def test_button_atlas_crops_include_the_full_hover_and_danger_caps():
    assert BUTTON_SPRITE_CROPS == {
        "normal": pygame.Rect(50, 230, 675, 240),
        "hover": pygame.Rect(750, 230, 675, 240),
        "danger": pygame.Rect(1450, 230, 675, 240),
    }


def test_loaded_ui_sprites_key_out_black_backgrounds_and_trim_their_bounds():
    pygame.font.init()
    ui = UI(pygame.Surface(WINDOW_SIZE), Game(create_tree_board))

    sprites = [
        *ui.button_skins.values(),
        ui.heart_full,
        ui.heart_empty,
        ui.star_full,
        ui.star_empty,
        ui.pause_icon,
        ui.pause_panel,
    ]

    for sprite in sprites:
        assert sprite.get_colorkey()[:3] == (0, 0, 0)
        bounds = sprite.get_bounding_rect()
        assert bounds.width >= sprite.get_width() - 2
        assert bounds.height >= sprite.get_height() - 2


def test_fit_surface_preserves_aspect_ratio_and_centers_the_sprite():
    source = pygame.Surface((300, 100), pygame.SRCALPHA)
    target = pygame.Rect(100, 200, 310, 54)

    fitted, rect = fit_surface(source, target)

    assert fitted.get_size() == (162, 54)
    assert rect.center == target.center
    assert rect.size == fitted.get_size()


def test_pause_controls_are_separate_and_render_for_a_paused_game():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(create_tree_board)
    ui = UI(screen, game)
    game.pause()

    ui.draw()

    assert not ui.pause_resume_rect().colliderect(ui.pause_restart_rect())
    assert not ui.pause_restart_rect().colliderect(ui.pause_menu_rect())
    assert ui.pause_rect().collidepoint(ui.pause_rect().center)


def test_pause_button_slots_follow_the_centers_of_the_supplied_pause_panel():
    pygame.font.init()
    ui = UI(pygame.Surface(WINDOW_SIZE), Game(create_tree_board))

    assert ui.pause_resume_rect().center == (600, 342)
    assert ui.pause_restart_rect().center == (600, 458)
    assert ui.pause_menu_rect().center == (600, 574)
    assert ui.pause_resume_rect().height == 100


def test_ui_exposes_start_and_result_action_buttons():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R"]], [["leaf"]]), start_in_menu=True)
    ui = UI(screen, game)

    assert ui.start_rect() == COVER_START_RECT
    assert ui.result_action_rect().size == (300, 70)


def test_result_button_slots_form_a_centered_stack_inside_the_result_panel():
    pygame.font.init()
    ui = UI(pygame.Surface(WINDOW_SIZE), Game(create_tree_board))

    assert ui.result_primary_rect().center == (600, 490)
    assert ui.result_retry_rect().center == (600, 565)
    assert ui.result_menu_rect().center == (600, 635)
    assert not ui.result_primary_rect().colliderect(ui.result_retry_rect())
    assert not ui.result_retry_rect().colliderect(ui.result_menu_rect())


def test_start_screen_draws_the_cover_without_a_programmatic_panel():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R"]], [["leaf"]]), start_in_menu=True)

    UI(screen, game).draw()

    assert screen.get_at((195, 130))[:3] != MENU_PANEL_COLOR
    assert screen.get_at((80, 80))[:3] != BACKGROUND


def test_start_screen_uses_the_cover_art_without_a_programmatic_panel(monkeypatch):
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R"]], [["leaf"]]), start_in_menu=True)
    ui = UI(screen, game)

    monkeypatch.setattr(
        ui,
        "_draw_action_button",
        lambda: pytest.fail("the cover already contains its own start button"),
    )

    ui.draw()


def test_main_menu_background_is_packaged_with_the_project():
    assert MENU_BACKGROUND_PATH.is_file()


def test_normal_arrow_is_a_compact_centered_boomerang_marker():
    pygame.font.init()
    screen = pygame.Surface((100, 100))
    screen.fill((0, 0, 0))
    ui = UI(screen, Game(create_tree_board))
    ui.layout = GridLayout(origin=(0, 0), cell_size=36)
    rect = pygame.Rect(32, 32, 36, 36)

    ui._draw_arrow(rect, "U", ARROW_COLOR)

    occupied = [
        (x, y)
        for x in range(rect.left, rect.right)
        for y in range(rect.top, rect.bottom)
        if screen.get_at((x, y))[:3] != (0, 0, 0)
    ]
    assert min(x for x, _ in occupied) > rect.left + 8
    assert max(x for x, _ in occupied) < rect.right - 8
    assert min(y for _, y in occupied) > rect.top + 8
    assert max(y for _, y in occupied) < rect.bottom - 8
    # A boomerang is two short arms, not a filled triangle.
    assert screen.get_at((rect.centerx, rect.centery + 4))[:3] == (0, 0, 0)


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


def test_cover_is_used_only_for_the_start_screen():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(create_tree_board, start_in_menu=True)
    ui = UI(screen, game)
    ui.cover_background.fill((210, 40, 60))
    ui.gameplay_background.fill((30, 70, 200))

    ui.draw()
    assert screen.get_at((20, 400))[:3] == (210, 40, 60)

    game.start()
    ui.draw()

    assert screen.get_at((20, 400))[:3] == (30, 70, 200)


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

    assert screen.get_at(tile.topleft)[:3] == ui.gameplay_background.get_at(tile.topleft)[:3]


def test_cleared_pixel_uses_its_unmodified_picture_colour():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    ui = UI(screen, Game(create_tree_board))
    row, col = next(
        (row, col)
        for row, grid_row in enumerate(ui.game.board.arrow_grid)
        for col, cell in enumerate(grid_row)
        if cell is not None
    )
    colour_name = ui.game.board.color_grid[row][col]
    ui.game.board.arrow_grid[row][col] = None

    ui.draw()

    assert screen.get_at(ui.layout.cell_rect(row, col).center)[:3] == COLOR_MAP[colour_name]


def test_hovered_arrow_tile_uses_a_soft_cyan_glow(monkeypatch):
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

    glow_pixel = screen.get_at((tile.left + 1, tile.centery))
    assert glow_pixel.b > glow_pixel.r + 25


def test_pause_panel_uses_text_buttons_without_button_skins(monkeypatch):
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    ui = UI(screen, Game(create_tree_board))
    calls = []

    monkeypatch.setattr(
        ui,
        "_draw_text_button",
        lambda rect, label: calls.append((rect, label)),
    )
    monkeypatch.setattr(
        ui,
        "_draw_action_button",
        lambda *args, **kwargs: pytest.fail("pause buttons must not use skins"),
    )

    ui._draw_pause_panel()

    assert calls == [
        (ui.pause_resume_rect(), "CONTINUE"),
        (ui.pause_restart_rect(), "RESTART LEVEL"),
        (ui.pause_menu_rect(), "MAIN MENU"),
    ]


def test_feature_buttons_have_distinct_hit_areas():
    pygame.font.init()
    ui = UI(pygame.Surface(WINDOW_SIZE), Game(create_tree_board))
    rects = [
        ui.hint_rect(),
        ui.undo_rect(),
        ui.auto_rect(),
        ui.save_rect(),
        ui.load_rect(),
    ]

    assert all(rect.width > 0 and rect.height > 0 for rect in rects)
    for index, left in enumerate(rects):
        for right in rects[index + 1 :]:
            assert not left.colliderect(right)
    assert not ui.pause_rect().colliderect(ui.hint_rect())


def test_feature_bar_renders_buttons_and_readouts(monkeypatch):
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R"]], [["leaf"]]))
    ui = UI(screen, game)
    calls = []
    monkeypatch.setattr(ui, "_draw_text_button", lambda rect, label: calls.append(label))

    ui._draw_feature_bar()

    assert calls == ["HINT", "UNDO", "AUTO", "SAVE", "LOAD"]


def test_hint_highlight_is_skipped_without_hint_cell():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    ui = UI(screen, Game(create_tree_board))
    ui.hint_cell = None

    ui._draw_hint_highlight()
