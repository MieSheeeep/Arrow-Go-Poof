"""Application state and rule-to-animation coordination for one level."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from collections.abc import Callable, Sequence

from src.animation import CollisionAnimation, FlyOutAnimation
from src.board import Board, MoveResult


class GameState(Enum):
    START = "start"
    PLAYING = "playing"
    CLEARED = "cleared"
    FAILED = "failed"
    PAUSED = "paused"


Animation = FlyOutAnimation | CollisionAnimation


@dataclass(frozen=True)
class LevelSummary:
    """The frozen runtime facts shown after a level has been cleared."""

    elapsed_seconds: float
    mistakes: int
    stars: int


class Game:
    def __init__(
        self,
        board_factory: Callable[[], Board] | Sequence[Callable[[], Board]],
        max_lives: int = 3,
        *,
        start_in_menu: bool = False,
        level_names: Sequence[str] | None = None,
    ) -> None:
        if type(max_lives) is not int or max_lives <= 0:
            raise ValueError("max_lives must be a positive integer")
        if callable(board_factory):
            self.level_factories = (board_factory,)
        else:
            self.level_factories = tuple(board_factory)
        if not self.level_factories or not all(callable(factory) for factory in self.level_factories):
            raise ValueError("at least one level factory is required")
        if level_names is None:
            self.level_names = tuple(
                f"LEVEL {index + 1:02d}" for index in range(len(self.level_factories))
            )
        else:
            self.level_names = tuple(level_names)
            if len(self.level_names) != len(self.level_factories):
                raise ValueError("level_names must match the number of level factories")
        self.max_lives = max_lives
        self.level_index = 0
        self._start_in_menu = start_in_menu
        self.restart()
        if start_in_menu:
            self.state = GameState.START

    @property
    def level_count(self) -> int:
        return len(self.level_factories)

    @property
    def level_number(self) -> int:
        return self.level_index + 1

    @property
    def level_name(self) -> str:
        return self.level_names[self.level_index]

    @property
    def has_next_level(self) -> bool:
        return self.level_index + 1 < self.level_count

    def _load_level(self) -> None:
        self.board = self.level_factories[self.level_index]()

    def _reset_runtime(self) -> None:
        self.lives = self.max_lives
        self.mistakes = 0
        self.elapsed_seconds = 0.0
        self.level_summary: LevelSummary | None = None
        self.animations: list[Animation] = []
        self.error_cells: set[tuple[int, int]] = set()

    def restart(self) -> None:
        self._load_level()
        self._reset_runtime()
        self.state = GameState.CLEARED if self.board.is_cleared() else GameState.PLAYING

    def start(self) -> None:
        if self.state is GameState.START:
            self.state = GameState.CLEARED if self.board.is_cleared() else GameState.PLAYING

    def next_level(self) -> bool:
        if self.state is not GameState.CLEARED or not self.has_next_level:
            return False
        self.level_index += 1
        self._load_level()
        self._reset_runtime()
        self.state = GameState.PLAYING
        return True

    def restart_campaign(self) -> None:
        self.level_index = 0
        self.restart()

    def click(self, row: int, col: int) -> MoveResult | None:
        if self.state is not GameState.PLAYING:
            return None

        result = self.board.click(row, col)
        if result.reason == "clear":
            assert result.direction is not None
            self.animations.append(FlyOutAnimation(row, col, result.direction))
            if self.board.is_cleared():
                self.level_summary = LevelSummary(
                    self.elapsed_seconds,
                    self.mistakes,
                    0,
                )
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
        if self.state is GameState.PLAYING:
            self.elapsed_seconds += delta_time
        remaining: list[Animation] = []
        for animation in self.animations:
            animation.update(delta_time)
            if animation.is_finished:
                if isinstance(animation, CollisionAnimation):
                    self.error_cells.add((animation.row, animation.col))
            else:
                remaining.append(animation)
        self.animations = remaining
