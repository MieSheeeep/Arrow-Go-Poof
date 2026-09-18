"""Pure board state and rules for the arrow puzzle."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


ARROWS = frozenset({"U", "D", "L", "R"})
DIRECTION_DELTAS = {
    "U": (-1, 0),
    "D": (1, 0),
    "L": (0, -1),
    "R": (0, 1),
}


@dataclass(frozen=True)
class MoveResult:
    success: bool
    row: int
    col: int
    direction: str | None
    reason: str
    blocker: tuple[int, int] | None = None


class Board:
    """Validated, mutable runtime state for one puzzle level."""

    def __init__(
        self,
        arrow_grid: list[list[str | None]],
        color_grid: list[list[Any | None]],
    ) -> None:
        self._validate_grids(arrow_grid, color_grid)
        self._initial_arrow_grid = deepcopy(arrow_grid)
        self._initial_color_grid = deepcopy(color_grid)
        self.arrow_grid = deepcopy(arrow_grid)
        self.color_grid = deepcopy(color_grid)
        self.rows = len(self.arrow_grid)
        self.cols = len(self.arrow_grid[0])

    @staticmethod
    def _grid_size(grid: object, name: str) -> tuple[int, int]:
        if not isinstance(grid, list) or not grid:
            raise ValueError(f"{name} must be a non-empty list of rows")
        if any(not isinstance(row, list) for row in grid):
            raise ValueError(f"{name} rows must be lists")
        if not grid[0]:
            raise ValueError(f"{name} rows must not be empty")
        width = len(grid[0])
        if any(len(row) != width for row in grid):
            raise ValueError(f"{name} must be rectangular")
        return len(grid), width

    @classmethod
    def _validate_grids(
        cls,
        arrow_grid: object,
        color_grid: object,
    ) -> None:
        arrow_size = cls._grid_size(arrow_grid, "arrow_grid")
        color_size = cls._grid_size(color_grid, "color_grid")
        if arrow_size != color_size:
            raise ValueError("arrow_grid and color_grid must have identical dimensions")

        for row_index, row in enumerate(arrow_grid):
            for col_index, cell in enumerate(row):
                if cell is not None and (
                    type(cell) is not str or (cell != "." and cell not in ARROWS)
                ):
                    raise ValueError("arrow_grid contains an invalid cell value")
                color = color_grid[row_index][col_index]
                if (cell is None) != (color is None):
                    raise ValueError("arrow_grid and color_grid masks must match")

    def in_bounds(self, row: int, col: int) -> bool:
        return (
            type(row) is int
            and type(col) is int
            and 0 <= row < self.rows
            and 0 <= col < self.cols
        )

    def get_cell(self, row: int, col: int) -> str | None:
        if not self.in_bounds(row, col):
            return None
        return self.arrow_grid[row][col]

    def is_arrow(self, row: int, col: int) -> bool:
        return self.get_cell(row, col) in ARROWS

    def _find_blocker(self, row: int, col: int) -> tuple[int, int] | None:
        row_delta, col_delta = DIRECTION_DELTAS[self.arrow_grid[row][col]]
        row += row_delta
        col += col_delta

        while self.in_bounds(row, col):
            cell = self.arrow_grid[row][col]
            if cell is None:
                return None
            if cell in ARROWS:
                return row, col
            row += row_delta
            col += col_delta
        return None

    def can_fly(self, row: int, col: int) -> bool:
        return self.is_arrow(row, col) and self._find_blocker(row, col) is None
