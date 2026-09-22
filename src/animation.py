"""Pure-Python timing models for non-blocking visual animations."""

from __future__ import annotations

import math


_RELATIVE_TOLERANCE = 1e-9


def _reached(value: float, boundary: float) -> bool:
    return value >= boundary or math.isclose(
        value, boundary, rel_tol=_RELATIVE_TOLERANCE, abs_tol=0.0
    )

_DIRECTION_DELTAS = {
    "U": (-1.0, 0.0),
    "D": (1.0, 0.0),
    "L": (0.0, -1.0),
    "R": (0.0, 1.0),
}

# Distances are measured in grid cells. They carry an arrow from anywhere in
# the fixed 1200x800 playfield beyond the corresponding screen edge.
_DEFAULT_FLY_OUT_DISTANCES = {
    "U": 16.0,
    "D": 16.0,
    "L": 20.0,
    "R": 20.0,
}


class _TimedAnimation:
    def __init__(self, duration: float) -> None:
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("duration must be positive")
        self.duration = duration
        self.elapsed = 0.0

    @property
    def is_finished(self) -> bool:
        return _reached(self.elapsed, self.duration)

    @property
    def progress(self) -> float:
        if self.is_finished:
            return 1.0
        return min(self.elapsed / self.duration, 1.0)

    def update(self, delta_time: float) -> None:
        if not math.isfinite(delta_time) or delta_time < 0:
            raise ValueError("delta_time must be non-negative")
        self.elapsed = min(self.elapsed + delta_time, self.duration)


def _direction_delta(direction: str) -> tuple[float, float]:
    try:
        return _DIRECTION_DELTAS[direction]
    except KeyError as exc:
        raise ValueError(f"unknown direction: {direction!r}") from exc


class FlyOutAnimation(_TimedAnimation):
    def __init__(
        self,
        row: int,
        col: int,
        direction: str,
        duration: float = 0.50,
        distance: float | None = None,
    ) -> None:
        super().__init__(duration)
        _direction_delta(direction)
        if distance is None:
            distance = _DEFAULT_FLY_OUT_DISTANCES[direction]
        if not math.isfinite(distance) or distance <= 0:
            raise ValueError("distance must be positive")
        self.row = row
        self.col = col
        self.direction = direction
        self.distance = distance
        self.windup_duration = min(0.07, duration * 0.18)
        self.flight_duration = duration - self.windup_duration

    @property
    def phase(self) -> str:
        if not _reached(self.elapsed, self.windup_duration):
            return "windup"
        if not self.is_finished:
            return "flying"
        return "done"

    @property
    def flight_progress(self) -> float:
        if self.phase == "windup":
            return 0.0
        return min(
            (self.elapsed - self.windup_duration) / self.flight_duration,
            1.0,
        )

    @property
    def offset_cells(self) -> tuple[float, float]:
        row_delta, col_delta = _direction_delta(self.direction)
        if self.phase == "windup":
            ratio = self.elapsed / self.windup_duration
            pull = 0.16 * math.sin(ratio * math.pi)
            return -row_delta * pull, -col_delta * pull
        eased = 1.0 - (1.0 - self.flight_progress) ** 2
        return row_delta * self.distance * eased, col_delta * self.distance * eased

    @property
    def scale(self) -> float:
        if self.phase == "windup":
            ratio = self.elapsed / self.windup_duration
            return 1.0 + 0.10 * math.sin(ratio * math.pi)
        return 1.0 + 0.035 * (1.0 - self.flight_progress)

    @property
    def trail_length_cells(self) -> float:
        if self.phase == "windup":
            return 0.0
        return 0.25 + 0.75 * self.flight_progress

    @property
    def color_state(self) -> str:
        return "normal"


class HeartLossAnimation(_TimedAnimation):
    """Transient HUD feedback for a life slot that was just consumed."""

    def __init__(self, heart_index: int, duration: float = 0.32) -> None:
        if type(heart_index) is not int or heart_index < 0:
            raise ValueError("heart_index must be a non-negative integer")
        super().__init__(duration)
        self.heart_index = heart_index
        self.flash_duration = min(0.10, duration * 0.35)

    @property
    def phase(self) -> str:
        if not _reached(self.elapsed, self.flash_duration):
            return "flash"
        if not self.is_finished:
            return "fade"
        return "done"

    @property
    def scale(self) -> float:
        if self.phase == "flash":
            ratio = self.elapsed / self.flash_duration
            return 1.0 + 0.18 * math.sin(ratio * math.pi)
        if self.phase == "fade":
            ratio = (self.elapsed - self.flash_duration) / (
                self.duration - self.flash_duration
            )
            return 1.0 - 0.12 * ratio
        return 0.88

    @property
    def alpha(self) -> int:
        if self.phase == "flash":
            return 255
        if self.phase == "fade":
            ratio = (self.elapsed - self.flash_duration) / (
                self.duration - self.flash_duration
            )
            return round(255 * (1.0 - ratio))
        return 0

    @property
    def shake_offset_x(self) -> int:
        if self.phase != "flash":
            return 0
        ratio = self.elapsed / self.flash_duration
        return round(math.sin(ratio * math.pi * 4) * 3)


class StarRevealAnimation(_TimedAnimation):
    """Reveal the earned result stars in a short, staggered sequence."""

    def __init__(
        self,
        star_count: int,
        *,
        initial_delay: float = 0.14,
        stagger: float = 0.18,
        pop_duration: float = 0.22,
    ) -> None:
        if type(star_count) is not int or not 1 <= star_count <= 3:
            raise ValueError("star_count must be an integer between 1 and 3")
        for value in (initial_delay, stagger, pop_duration):
            if not math.isfinite(value) or value <= 0:
                raise ValueError("star reveal timings must be positive")
        self.star_count = star_count
        self.initial_delay = initial_delay
        self.stagger = stagger
        self.pop_duration = pop_duration
        super().__init__(initial_delay + stagger * (star_count - 1) + pop_duration)

    def star_progress(self, index: int) -> float:
        if type(index) is not int or not 0 <= index <= 2:
            raise ValueError("star index must be between 0 and 2")
        if index >= self.star_count:
            return 0.0
        return min(
            max(0.0, (self.elapsed - self.initial_delay - index * self.stagger) / self.pop_duration),
            1.0,
        )

    def star_scale(self, index: int) -> float:
        progress = self.star_progress(index)
        return 1.0 + 0.30 * math.sin(progress * math.pi)


class CollisionAnimation(_TimedAnimation):
    def __init__(
        self,
        row: int,
        col: int,
        blocker: tuple[int, int],
        direction: str,
        approach_duration: float = 0.12,
        impact_duration: float = 0.08,
        retreat_duration: float = 0.16,
    ) -> None:
        for duration in (approach_duration, impact_duration, retreat_duration):
            if not math.isfinite(duration) or duration <= 0:
                raise ValueError("collision phase durations must be positive")
        _direction_delta(direction)
        self.row = row
        self.col = col
        self.blocker = blocker
        self.direction = direction
        self.approach_duration = approach_duration
        self.impact_duration = impact_duration
        self.retreat_duration = retreat_duration
        super().__init__(approach_duration + impact_duration + retreat_duration)

    @property
    def phase(self) -> str:
        if not _reached(self.elapsed, self.approach_duration):
            return "approach"
        if not _reached(self.elapsed, self.approach_duration + self.impact_duration):
            return "impact"
        if not _reached(self.elapsed, self.duration):
            return "retreat"
        return "done"

    @property
    def color_state(self) -> str:
        return "normal" if self.phase == "approach" else "error"

    @property
    def offset_cells(self) -> tuple[float, float]:
        target = (self.blocker[0] - self.row, self.blocker[1] - self.col)
        if self.phase == "approach":
            ratio = self.elapsed / self.approach_duration
            return target[0] * ratio, target[1] * ratio
        if self.phase == "impact":
            return float(target[0]), float(target[1])
        if self.phase == "retreat":
            phase_elapsed = self.elapsed - self.approach_duration - self.impact_duration
            ratio = 1.0 - phase_elapsed / self.retreat_duration
            return target[0] * ratio, target[1] * ratio
        return 0.0, 0.0
