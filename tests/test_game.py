import math

import pytest

from src.animation import CollisionAnimation, FlyOutAnimation
from src.board import Board
from src.game import Game, GameState, LevelSummary
from src.levels import LEVEL_FACTORIES, LEVEL_NAMES


def board_factory(arrows):
    def create():
        colors = [
            [None if cell is None else f"cell-{row}-{col}" for col, cell in enumerate(line)]
            for row, line in enumerate(arrows)
        ]
        return Board([list(line) for line in arrows], colors)

    return create


def test_game_starts_in_playing_with_three_lives():
    game = Game(board_factory([["R"]]))

    assert game.state is GameState.PLAYING
    assert game.lives == 3
    assert game.mistakes == 0
    assert game.board.remaining_arrows() == 1
    assert game.animations == []
    assert game.error_cells == set()


def test_level_timer_advances_only_while_playing_and_freezes_on_clear():
    game = Game(board_factory([["R"]]))

    game.update(4.25)
    game.click(0, 0)
    game.update(8.0)

    assert game.elapsed_seconds == pytest.approx(4.25)
    assert game.level_summary is not None
    assert game.level_summary.elapsed_seconds == pytest.approx(4.25)


def test_timer_does_not_start_in_menu_and_restart_resets_it():
    game = Game(board_factory([["R"]]), start_in_menu=True)

    game.update(5.0)
    game.start()
    game.update(2.5)
    game.restart()

    assert game.elapsed_seconds == 0.0
    assert game.level_summary is None


@pytest.mark.parametrize(
    ("elapsed", "mistakes", "expected_stars"),
    [(9.5, 0, 3), (15.0, 1, 2), (25.0, 0, 1), (9.5, 2, 1)],
)
def test_clear_summary_uses_time_and_mistake_star_rules(
    elapsed, mistakes, expected_stars
):
    game = Game(board_factory([["R"]]), star_thresholds=((10.0, 20.0),))
    game.elapsed_seconds = elapsed
    game.mistakes = mistakes

    game.click(0, 0)

    assert game.level_summary == LevelSummary(elapsed, mistakes, expected_stars)


def test_game_starts_cleared_when_factory_returns_empty_board():
    game = Game(board_factory([["."]]))

    assert game.state is GameState.CLEARED


@pytest.mark.parametrize("delta_time", [-0.01, math.nan, math.inf])
def test_update_rejects_invalid_delta_time_without_active_animations(delta_time):
    game = Game(board_factory([["R"]]))

    with pytest.raises(ValueError):
        game.update(delta_time)


def test_successful_click_clears_board_and_creates_fly_out_animation():
    game = Game(board_factory([["R"]]))

    result = game.click(0, 0)

    assert result is not None and result.success is True
    assert game.board.get_cell(0, 0) == "."
    assert game.animations and isinstance(game.animations[0], FlyOutAnimation)
    assert game.state is GameState.CLEARED
    assert game.lives == 3


def test_blocked_click_deducts_life_and_creates_collision_animation():
    game = Game(board_factory([["R", "U"]]))

    result = game.click(0, 0)

    assert result is not None and result.reason == "blocked"
    assert result.blocker == (0, 1)
    assert game.lives == 2
    assert game.mistakes == 1
    assert game.state is GameState.PLAYING
    assert isinstance(game.animations[0], CollisionAnimation)
    assert game.error_cells == set()


def test_collision_error_cell_is_persisted_only_after_animation_finishes():
    game = Game(board_factory([["R", "U"]]))
    game.click(0, 0)

    game.update(0.12)
    assert game.error_cells == set()
    assert game.animations[0].color_state == "error"

    game.update(0.24)
    assert game.animations == []
    assert game.error_cells == {(0, 0)}


def test_invalid_click_does_not_change_game_state():
    game = Game(board_factory([[None, ".", "R"]]))

    for position in [(-1, 0), (0, 0), (0, 1)]:
        before = (game.lives, game.mistakes, len(game.animations))
        result = game.click(*position)
        assert result is not None and result.success is False
        assert (game.lives, game.mistakes, len(game.animations)) == before


def test_three_blocked_clicks_enter_failed_and_stop_future_clicks():
    game = Game(board_factory([["R", "U"]]))

    for _ in range(3):
        game.click(0, 0)

    assert game.lives == 0
    assert game.mistakes == 3
    assert game.state is GameState.FAILED
    animation_count = len(game.animations)
    assert game.click(0, 0) is None
    assert len(game.animations) == animation_count


def test_restart_restores_board_and_runtime_state():
    game = Game(board_factory([["R"]]))
    game.click(0, 0)
    game.update(1.0)
    game.restart()

    assert game.state is GameState.PLAYING
    assert game.lives == 3
    assert game.mistakes == 0
    assert game.board.get_cell(0, 0) == "R"
    assert game.animations == []
    assert game.error_cells == set()


def test_campaign_can_start_from_menu_and_reports_level_count():
    game = Game(LEVEL_FACTORIES, start_in_menu=True)

    assert game.state is GameState.START
    assert game.level_count == 3
    assert game.level_index == 0
    assert game.level_number == 1


def test_start_enters_first_level_and_next_level_replaces_board():
    game = Game(LEVEL_FACTORIES, start_in_menu=True, level_names=LEVEL_NAMES)

    game.start()
    first_board = game.board
    assert game.state is GameState.PLAYING
    assert game.level_name == "ENCHANTED APPLE"

    game.state = GameState.CLEARED
    assert game.next_level() is True
    assert game.level_index == 1
    assert game.level_name == "BEAD BALL"
    assert game.board is not first_board
    assert game.state is GameState.PLAYING


def test_last_level_reports_no_next_level_and_campaign_restart_returns_to_first():
    game = Game(LEVEL_FACTORIES)

    game.level_index = 2
    game.restart()
    game.state = GameState.CLEARED
    assert game.has_next_level is False
    assert game.next_level() is False

    game.restart_campaign()
    assert game.level_index == 0
    assert game.state is GameState.PLAYING
