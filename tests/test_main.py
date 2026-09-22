import pygame
import pytest

from src.board import Board
from src.game import Game, GameState
from src.ui import GridLayout
from main import process_event


class StubUI:
    def __init__(self):
        self.cell_at_calls = 0
        self.layout = GridLayout((260, 130), 48)

    def cell_at(self, position):
        self.cell_at_calls += 1
        return 0, 0

    def restart_rect(self):
        return pygame.Rect(0, 0, 100, 40)

    def menu_rect(self):
        return pygame.Rect(110, 0, 100, 40)

    def pause_rect(self):
        return pygame.Rect(220, 0, 100, 40)

    def result_primary_rect(self):
        return pygame.Rect(330, 0, 100, 40)

    def result_retry_rect(self):
        return pygame.Rect(440, 0, 100, 40)

    def result_menu_rect(self):
        return pygame.Rect(550, 0, 100, 40)

    def pause_resume_rect(self):
        return pygame.Rect(660, 0, 100, 40)

    def pause_restart_rect(self):
        return pygame.Rect(770, 0, 100, 40)

    def pause_menu_rect(self):
        return pygame.Rect(880, 0, 100, 40)

    def hint_rect(self):
        return pygame.Rect(0, 200, 100, 40)

    def undo_rect(self):
        return pygame.Rect(110, 200, 100, 40)

    def auto_rect(self):
        return pygame.Rect(220, 200, 100, 40)

    def save_rect(self):
        return pygame.Rect(330, 200, 100, 40)

    def load_rect(self):
        return pygame.Rect(440, 200, 100, 40)

    def start_rect(self):
        return self.restart_rect()


def make_game():
    return Game(lambda: Board([["R"]], [["leaf"]]))


@pytest.mark.parametrize("state", [GameState.CLEARED, GameState.FAILED])
def test_terminal_state_does_not_route_normal_click_to_board(state, monkeypatch):
    game = make_game()
    game.state = state
    ui = StubUI()
    monkeypatch.setattr(game, "click", lambda *_: pytest.fail("terminal click routed"))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (260, 130)})

    assert process_event(event, game, ui) is True
    assert ui.cell_at_calls == 0


def test_playing_left_click_routes_through_ui_to_game(monkeypatch):
    game = make_game()
    ui = StubUI()
    clicked = []
    monkeypatch.setattr(game, "click", lambda row, col: clicked.append((row, col)))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (260, 130)})

    assert process_event(event, game, ui) is True
    assert clicked == [(0, 0)]
    assert ui.cell_at_calls == 1


def test_paused_restart_button_resets_level_without_routing_to_board(monkeypatch):
    game = Game(lambda: Board([["R", "U"]], [["leaf", "leaf"]]))
    ui = StubUI()
    game.click(0, 0)
    game.pause()
    monkeypatch.setattr(game, "click", lambda *_: pytest.fail("restart routed to board"))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (780, 10)})

    assert process_event(event, game, ui) is True
    assert game.board.get_cell(0, 0) == "R"
    assert game.lives == 3
    assert ui.cell_at_calls == 0


def test_paused_menu_button_returns_to_start_state_without_routing_to_board(monkeypatch):
    game, ui = make_game(), StubUI()
    game.pause()
    monkeypatch.setattr(game, "click", lambda *_: pytest.fail("menu routed to board"))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (890, 10)})

    assert process_event(event, game, ui) is True
    assert game.state is GameState.START
    assert ui.cell_at_calls == 0


def test_pause_button_enters_paused_state_without_routing_to_board(monkeypatch):
    game, ui = make_game(), StubUI()
    monkeypatch.setattr(game, "click", lambda *_: pytest.fail("pause routed to board"))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (230, 10)})

    assert process_event(event, game, ui) is True
    assert game.state is GameState.PAUSED
    assert ui.cell_at_calls == 0


def test_paused_resume_button_returns_to_playing_state():
    game, ui = make_game(), StubUI()
    game.state = GameState.PAUSED
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (670, 10)})

    assert process_event(event, game, ui) is True
    assert game.state is GameState.PLAYING


def test_start_button_enters_playing_state():
    game = Game(lambda: Board([["R"]], [["leaf"]]), start_in_menu=True)
    ui = StubUI()
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (10, 10)})

    assert process_event(event, game, ui) is True
    assert game.state is GameState.PLAYING


def test_cleared_action_button_advances_to_next_level():
    game = Game(
        [
            lambda: Board([["."]], [["leaf"]]),
            lambda: Board([["R"]], [["leaf"]]),
        ]
    )
    game.state = GameState.CLEARED
    ui = StubUI()
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (340, 10)})

    assert process_event(event, game, ui) is True
    assert game.level_index == 1
    assert game.state is GameState.PLAYING


def test_clear_retry_button_restarts_current_level():
    game, ui = make_game(), StubUI()
    game.state = GameState.CLEARED
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (340, 10)})

    assert process_event(event, game, ui) is True
    assert game.state is GameState.PLAYING
    assert game.board.get_cell(0, 0) == "R"


def test_hint_button_sets_hint_cell(monkeypatch):
    game, ui = make_game(), StubUI()
    monkeypatch.setattr(game, "hint", lambda: (0, 0))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (10, 210)})

    assert process_event(event, game, ui) is True
    assert ui.hint_cell == (0, 0)


def test_undo_button_calls_undo(monkeypatch):
    game, ui = make_game(), StubUI()
    calls = []
    monkeypatch.setattr(game, "undo", lambda: calls.append(True) or True)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (120, 210)})

    assert process_event(event, game, ui) is True
    assert calls == [True]


def test_auto_button_toggles_auto_mode():
    game, ui = make_game(), StubUI()
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (230, 210)})

    assert process_event(event, game, ui) is True
    assert game.auto_mode is True
    assert process_event(event, game, ui) is True
    assert game.auto_mode is False


def test_save_button_writes_savegame(monkeypatch):
    game, ui = make_game(), StubUI()
    saved = []
    monkeypatch.setattr(game, "save", lambda path: saved.append(path))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (340, 210)})

    assert process_event(event, game, ui) is True
    assert saved == ["savegame.json"]


def test_load_button_reads_savegame(monkeypatch):
    game, ui = make_game(), StubUI()
    loaded = []
    monkeypatch.setattr(game, "load", lambda path: loaded.append(path))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (450, 210)})

    assert process_event(event, game, ui) is True
    assert loaded == ["savegame.json"]


def test_load_button_swallows_missing_savegame(monkeypatch):
    game, ui = make_game(), StubUI()

    def boom(path):
        raise FileNotFoundError(path)

    monkeypatch.setattr(game, "load", boom)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (450, 210)})

    assert process_event(event, game, ui) is True


def test_r_key_loads_a_random_level(monkeypatch):
    game, ui = make_game(), StubUI()
    monkeypatch.setattr(
        "main.create_random_level_board",
        lambda: Board([["R"]], [["leaf"]]),
    )
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_r})

    assert process_event(event, game, ui) is True
    assert game.custom_level is True
    assert game.state is GameState.PLAYING
