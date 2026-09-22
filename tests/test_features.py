"""Tests for the optional features: hint, undo, combo/score, auto-solve, save/load."""

from src.board import Board
from src.game import Game, GameState
from src.levels import create_random_level_board


def board_factory(arrows):
    def create():
        colors = [
            [None if cell is None else f"cell-{row}-{col}" for col, cell in enumerate(line)]
            for row, line in enumerate(arrows)
        ]
        return Board([list(line) for line in arrows], colors)

    return create


def test_hint_returns_a_clearable_arrow():
    game = Game(board_factory([["R", "U"]]))

    # R 被右侧的 U 阻挡，U 朝上无阻挡，因此提示应指向 U。
    assert game.hint() == (0, 1)


def test_hint_is_none_when_not_playing():
    game = Game(board_factory([["R"]]), start_in_menu=True)

    assert game.state is GameState.START
    assert game.hint() is None


def test_undo_restores_cleared_arrow_after_animations_finish():
    game = Game(board_factory([["R"]]))

    game.click(0, 0)
    assert game.animations  # 动画未结束前不允许撤销
    assert game.undo() is False

    game.update(1.0)
    assert game.state is GameState.CLEARED
    assert game.undo() is True
    assert game.board.get_cell(0, 0) == "R"
    assert game.state is GameState.PLAYING
    assert game.level_summary is None


def test_undo_restores_combo_and_score():
    game = Game(board_factory([["R"], ["R"]]))

    game.click(0, 0)
    game.click(1, 0)
    assert game.combo == 2
    assert game.score == 30

    game.update(1.0)
    assert game.undo() is True
    assert game.combo == 1
    assert game.score == 10
    assert game.board.get_cell(1, 0) == "R"


def test_undo_returns_false_when_nothing_to_undo():
    game = Game(board_factory([["R"]]))

    assert game.undo() is False


def test_combo_resets_on_blocked_click():
    game = Game(board_factory([["R", "U"], ["L", None]]))

    game.click(1, 0)  # L 可飞出，连击 +1
    assert game.combo == 1

    game.click(0, 0)  # R 被 U 阻挡
    assert game.combo == 0
    assert game.lives == 2


def test_score_and_max_combo_accumulate():
    game = Game(board_factory([["R"], ["R"]]))

    game.click(0, 0)
    game.click(1, 0)

    assert game.score == 30  # 10 * 1 + 10 * 2
    assert game.max_combo == 2


def test_auto_solve_step_clears_board():
    game = Game(board_factory([["R"], ["R"]]))

    assert game.auto_solve_step() is True
    assert game.board.remaining_arrows() == 1
    assert game.auto_solve_step() is True
    assert game.board.remaining_arrows() == 0
    assert game.state is GameState.CLEARED


def test_auto_mode_advances_one_arrow_per_animation_cycle():
    game = Game(board_factory([["R"], ["R"]]))
    game.auto_mode = True

    for _ in range(10):
        game.update(1.0)

    assert game.state is GameState.CLEARED
    assert game.board.remaining_arrows() == 0


def test_save_load_roundtrip_restores_state():
    game = Game(board_factory([["R"], ["R"]]))
    game.click(0, 0)

    restored = Game(board_factory([["R"], ["R"]]))
    restored.load_state(game.to_dict())

    assert restored.board.get_cell(0, 0) == "."
    assert restored.board.get_cell(1, 0) == "R"
    assert restored.lives == game.lives
    assert restored.mistakes == game.mistakes
    assert restored.combo == game.combo
    assert restored.score == game.score


def test_save_load_file_roundtrip(tmp_path):
    path = tmp_path / "save.json"
    game = Game(board_factory([["R"], ["R"]]))
    game.click(0, 0)
    game.save(path)

    restored = Game(board_factory([["R"], ["R"]]))
    restored.load(path)

    assert restored.board.get_cell(0, 0) == "."
    assert restored.board.get_cell(1, 0) == "R"
    assert restored.score == game.score


def test_random_level_board_is_solvable_and_reproducible():
    first = create_random_level_board(seed=42)
    second = create_random_level_board(seed=42)

    assert first.arrow_grid == second.arrow_grid

    board = create_random_level_board(seed=42)
    while board.first_clearable_arrow() is not None:
        row, col = board.first_clearable_arrow()
        assert board.click(row, col).success
    assert board.is_cleared()


def test_load_custom_board_starts_fresh_attempt():
    game = Game(board_factory([["R"]]))
    game.click(0, 0)

    custom = create_random_level_board(seed=7)
    game.load_custom_board(custom)

    assert game.board is custom
    assert game.custom_level is True
    assert game.state is GameState.PLAYING
    assert game.lives == 3
    assert game.mistakes == 0
    assert game.elapsed_seconds == 0.0
