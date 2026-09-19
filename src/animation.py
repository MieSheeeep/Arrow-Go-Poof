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
        duration: float = 0.30,
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

    @property
    def offset_cells(self) -> tuple[float, float]:
        row_delta, col_delta = _direction_delta(self.direction)
        eased = 1.0 - (1.0 - self.progress) ** 2
        return row_delta * self.distance * eased, col_delta * self.distance * eased

    @property
    def color_state(self) -> str:
        return "normal"


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
