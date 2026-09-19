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

    def result_action_rect(self):
        return self.restart_rect()

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
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (10, 10)})

    assert process_event(event, game, ui) is True
    assert game.level_index == 1
    assert game.state is GameState.PLAYING
