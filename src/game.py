"""Application state and rule-to-animation coordination for one level."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from collections.abc import Callable, Sequence

from src.animation import (
    CollisionAnimation,
    FlyOutAnimation,
    HeartLossAnimation,
    StarRevealAnimation,
)
from src.board import Board, MoveResult


class GameState(Enum):
    START = "start"
    PLAYING = "playing"
    CLEARED = "cleared"
    FAILED = "failed"
    PAUSED = "paused"


Animation = FlyOutAnimation | CollisionAnimation | HeartLossAnimation | StarRevealAnimation


@dataclass(frozen=True)
class LevelSummary:
    """The frozen runtime facts shown after a level has been cleared."""

    elapsed_seconds: float
    mistakes: int
    stars: int


def _stars_for(
    elapsed_seconds: float,
    mistakes: int,
    limits: tuple[float, float],
) -> int:
    """Return a 1--3 star rating for a completed level."""
    three_star_limit, two_star_limit = limits
    if elapsed_seconds <= three_star_limit and mistakes == 0:
        return 3
    if elapsed_seconds <= two_star_limit and mistakes <= 1:
        return 2
    return 1


class Game:
    def __init__(
        self,
        board_factory: Callable[[], Board] | Sequence[Callable[[], Board]],
        max_lives: int = 3,
        *,
        start_in_menu: bool = False,
        level_names: Sequence[str] | None = None,
        star_thresholds: Sequence[tuple[float, float]] | None = None,
        time_limits: Sequence[float] | None = None,
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
        if star_thresholds is None:
            self.star_thresholds = tuple((60.0, 120.0) for _ in self.level_factories)
        else:
            self.star_thresholds = tuple(star_thresholds)
            if len(self.star_thresholds) != len(self.level_factories):
                raise ValueError("star_thresholds must match the number of level factories")
            for limits in self.star_thresholds:
                if (
                    not isinstance(limits, tuple)
                    or len(limits) != 2
                    or not all(math.isfinite(limit) and limit > 0 for limit in limits)
                    or limits[0] >= limits[1]
                ):
                    raise ValueError(
                        "each star threshold pair must be positive and increasing"
                    )
        if time_limits is None:
            self.time_limits = tuple(180.0 for _ in self.level_factories)
        else:
            self.time_limits = tuple(time_limits)
            if len(self.time_limits) != len(self.level_factories) or not all(
                math.isfinite(limit) and limit > 0 for limit in self.time_limits
            ):
                raise ValueError(
                    "time_limits must contain one positive finite limit per level"
                )
        self.max_lives = max_lives
        self.level_index = 0
        self._start_in_menu = start_in_menu
        self.auto_mode = False
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

    @property
    def time_limit_seconds(self) -> float:
        return self.time_limits[self.level_index]

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, self.time_limit_seconds - self.elapsed_seconds)

    def _load_level(self) -> None:
        self.board = self.level_factories[self.level_index]()

    def _reset_runtime(self) -> None:
        self.lives = self.max_lives
        self.mistakes = 0
        self.elapsed_seconds = 0.0
        self.level_summary: LevelSummary | None = None
        self.animations: list[Animation] = []
        self.error_cells: set[tuple[int, int]] = set()
        self.failure_reason: str | None = None
        self.combo = 0
        self.score = 0
        self.max_combo = 0
        self.history: list[tuple[int, int, str]] = []
        self.custom_level = False

    def restart(self) -> None:
        self._load_level()
        self._reset_runtime()
        self.state = GameState.CLEARED if self.board.is_cleared() else GameState.PLAYING

    def start(self) -> None:
        if self.state is GameState.START:
            self.state = GameState.CLEARED if self.board.is_cleared() else GameState.PLAYING

    def load_custom_board(self, board: Board) -> None:
        """Swap in a caller-provided board and start a fresh attempt."""
        self.board = board
        self._reset_runtime()
        self.custom_level = True
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

    def return_to_menu(self) -> None:
        """Discard the current attempt and show a fresh campaign menu."""
        self.level_index = 0
        self._load_level()
        self._reset_runtime()
        self.state = GameState.START

    def pause(self) -> bool:
        """Freeze a live level without changing its board or timer."""
        if self.state is not GameState.PLAYING:
            return False
        self.state = GameState.PAUSED
        return True

    def resume(self) -> bool:
        """Continue a level that was paused by the player."""
        if self.state is not GameState.PAUSED:
            return False
        self.state = GameState.PLAYING
        return True

    def hint(self) -> tuple[int, int] | None:
        """Return a currently clickable arrow for the player, or None."""
        if self.state is not GameState.PLAYING:
            return None
        return self.board.first_clearable_arrow()

    def undo(self) -> bool:
        """Restore the most recent successful clear, if possible."""
        if self.state not in {GameState.PLAYING, GameState.CLEARED}:
            return False
        if self.animations or not self.history:
            return False
        row, col, direction = self.history.pop()
        if self.board.get_cell(row, col) != ".":
            return False
        self.board.arrow_grid[row][col] = direction
        self.score = max(0, self.score - 10 * self.combo)
        self.combo = max(0, self.combo - 1)
        self.error_cells.discard((row, col))
        if self.state is GameState.CLEARED:
            self.level_summary = None
            self.state = GameState.PLAYING
        return True

    def auto_solve_step(self) -> bool:
        """Click one currently clearable arrow; return whether a move happened."""
        if self.state is not GameState.PLAYING:
            return False
        cell = self.board.first_clearable_arrow()
        if cell is None:
            return False
        result = self.click(*cell)
        return result is not None and result.success

    def to_dict(self) -> dict:
        """Serialize the current attempt for saving."""
        return {
            "level_index": self.level_index,
            "arrow_grid": [list(row) for row in self.board.arrow_grid],
            "color_grid": [list(row) for row in self.board.color_grid],
            "lives": self.lives,
            "mistakes": self.mistakes,
            "elapsed_seconds": self.elapsed_seconds,
            "combo": self.combo,
            "score": self.score,
        }

    def load_state(self, data: dict) -> None:
        """Restore an attempt previously produced by to_dict."""
        self.level_index = int(data["level_index"])
        self.board = Board(data["arrow_grid"], data["color_grid"])
        self.lives = int(data["lives"])
        self.mistakes = int(data["mistakes"])
        self.elapsed_seconds = float(data["elapsed_seconds"])
        self.combo = int(data.get("combo", 0))
        self.score = int(data.get("score", 0))
        self.max_combo = self.combo
        self.level_summary = None
        self.animations = []
        self.error_cells = set()
        self.history = []
        self.failure_reason = None
        self.state = GameState.PLAYING

    def save(self, path) -> None:
        """Write the current attempt to a JSON file."""
        import json

        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, ensure_ascii=False)

    def load(self, path) -> None:
        """Restore an attempt from a JSON file."""
        import json

        with open(path, "r", encoding="utf-8") as handle:
            self.load_state(json.load(handle))

    def click(self, row: int, col: int) -> MoveResult | None:
        if self.state is not GameState.PLAYING:
            return None

        result = self.board.click(row, col)
        if result.reason == "clear":
            assert result.direction is not None
            self.animations.append(FlyOutAnimation(row, col, result.direction))
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.score += 10 * self.combo
            self.history.append((row, col, result.direction))
            if self.board.is_cleared():
                self.level_summary = LevelSummary(
                    self.elapsed_seconds,
                    self.mistakes,
                    _stars_for(
                        self.elapsed_seconds,
                        self.mistakes,
                        self.star_thresholds[self.level_index],
                    ),
                )
                self.animations.append(StarRevealAnimation(self.level_summary.stars))
                self.state = GameState.CLEARED
        elif result.reason == "blocked":
            assert result.direction is not None
            assert result.blocker is not None
            self.lives -= 1
            self.mistakes += 1
            self.combo = 0
            self.animations.append(
                CollisionAnimation(row, col, result.blocker, result.direction)
            )
            self.animations.append(HeartLossAnimation(self.lives))
            if self.lives == 0:
                self.failure_reason = "lives"
                self.state = GameState.FAILED
        return result

    def update(self, delta_time: float) -> None:
        if not math.isfinite(delta_time) or delta_time < 0:
            raise ValueError("delta_time must be a finite non-negative number")
        if self.state is GameState.PAUSED:
            return
        if self.state is GameState.PLAYING:
            self.elapsed_seconds = min(
                self.elapsed_seconds + delta_time, self.time_limit_seconds
            )
            if self.remaining_seconds == 0.0:
                self.failure_reason = "time_up"
                self.state = GameState.FAILED
        remaining: list[Animation] = []
        for animation in self.animations:
            animation.update(delta_time)
            if animation.is_finished:
                if isinstance(animation, CollisionAnimation):
                    self.error_cells.add((animation.row, animation.col))
            else:
                remaining.append(animation)
        self.animations = remaining
        if self.auto_mode and self.state is GameState.PLAYING and not self.animations:
            self.auto_solve_step()
