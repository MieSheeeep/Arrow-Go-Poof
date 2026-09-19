import math

import pytest

from src.animation import CollisionAnimation, FlyOutAnimation
from src.board import Board
from src.game import Game, GameState


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
