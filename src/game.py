"""Application state and rule-to-animation coordination for one level."""

from __future__ import annotations

import math
from enum import Enum
from typing import Callable

from src.animation import CollisionAnimation, FlyOutAnimation
from src.board import Board, MoveResult


class GameState(Enum):
    PLAYING = "playing"
    CLEARED = "cleared"
    FAILED = "failed"
    PAUSED = "paused"


Animation = FlyOutAnimation | CollisionAnimation


class Game:
    def __init__(self, board_factory: Callable[[], Board], max_lives: int = 3) -> None:
        if type(max_lives) is not int or max_lives <= 0:
            raise ValueError("max_lives must be a positive integer")
        self.board_factory = board_factory
        self.max_lives = max_lives
        self.restart()

    def restart(self) -> None:
        self.board = self.board_factory()
        self.lives = self.max_lives
        self.mistakes = 0
        self.state = GameState.CLEARED if self.board.is_cleared() else GameState.PLAYING
        self.animations: list[Animation] = []
        self.error_cells: set[tuple[int, int]] = set()

    def click(self, row: int, col: int) -> MoveResult | None:
        if self.state is not GameState.PLAYING:
            return None

        result = self.board.click(row, col)
        if result.reason == "clear":
            assert result.direction is not None
            self.animations.append(FlyOutAnimation(row, col, result.direction))
            if self.board.is_cleared():
                self.state = GameState.CLEARED
        elif result.reason == "blocked":
            assert result.direction is not None
            assert result.blocker is not None
            self.lives -= 1
            self.mistakes += 1
            self.animations.append(
                CollisionAnimation(row, col, result.blocker, result.direction)
            )
            if self.lives == 0:
                self.state = GameState.FAILED
        return result

    def update(self, delta_time: float) -> None:
        if not math.isfinite(delta_time) or delta_time < 0:
            raise ValueError("delta_time must be a finite non-negative number")
        remaining: list[Animation] = []
        for animation in self.animations:
            animation.update(delta_time)
            if animation.is_finished:
                if isinstance(animation, CollisionAnimation):
                    self.error_cells.add((animation.row, animation.col))
            else:
                remaining.append(animation)
        self.animations = remaining
