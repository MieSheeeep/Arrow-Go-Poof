"""Pure-Python timing models for non-blocking visual animations."""

from __future__ import annotations


_DIRECTION_DELTAS = {
    "U": (-1.0, 0.0),
    "D": (1.0, 0.0),
    "L": (0.0, -1.0),
    "R": (0.0, 1.0),
}


class _TimedAnimation:
    def __init__(self, duration: float) -> None:
        if duration <= 0:
            raise ValueError("duration must be positive")
        self.duration = duration
        self.elapsed = 0.0

    @property
    def is_finished(self) -> bool:
        return self.elapsed >= self.duration

    @property
    def progress(self) -> float:
        return min(self.elapsed / self.duration, 1.0)

    def update(self, delta_time: float) -> None:
        if delta_time < 0:
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
        distance: float = 2.0,
    ) -> None:
        super().__init__(duration)
        if distance <= 0:
            raise ValueError("distance must be positive")
        _direction_delta(direction)
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
            if duration <= 0:
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
        if self.elapsed < self.approach_duration:
            return "approach"
        if self.elapsed < self.approach_duration + self.impact_duration:
            return "impact"
        if not self.is_finished:
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
