"""Deterministic development-time generator for solvable arrow layouts."""

from __future__ import annotations

import random


DIRECTIONS = (
    ("U", -1, 0),
    ("D", 1, 0),
    ("L", 0, -1),
    ("R", 0, 1),
)
ARROWS = frozenset(direction for direction, _, _ in DIRECTIONS)


def _validate_mask(mask: tuple[tuple[str | None, ...], ...]) -> None:
    if not mask or not mask[0] or any(len(row) != len(mask[0]) for row in mask):
        raise ValueError("mask must be a non-empty rectangular grid")
    if not any(cell is not None for row in mask for cell in row):
        raise ValueError("mask must contain at least one puzzle cell")


def _can_fly(
    grid: list[list[str | None]], row: int, col: int, row_delta: int, col_delta: int
) -> bool:
    row += row_delta
    col += col_delta
    while 0 <= row < len(grid) and 0 <= col < len(grid[0]):
        if grid[row][col] in ARROWS:
            return False
        row += row_delta
        col += col_delta
    return True


def _clears_in_scan_order(grid: list[list[str | None]]) -> bool:
    while True:
        available = []
        for row_index, row in enumerate(grid):
            for col_index, cell in enumerate(row):
                if cell not in ARROWS:
                    continue
                direction = next(item for item in DIRECTIONS if item[0] == cell)
                if _can_fly(grid, row_index, col_index, direction[1], direction[2]):
                    available.append((row_index, col_index))
        if not available:
            return not any(cell in ARROWS for row in grid for cell in row)
        row_index, col_index = available[0]
        grid[row_index][col_index] = "."


def generate_solvable_arrow_grid(
    mask: tuple[tuple[str | None, ...], ...], seed: int, attempts: int = 200
) -> tuple[tuple[str | None, ...], ...]:
    """Create a reproducible, varied layout with a deterministic clear order."""
    _validate_mask(mask)
    if type(seed) is not int or type(attempts) is not int or attempts <= 0:
        raise ValueError("seed must be an integer and attempts must be positive")

    coordinates = [
        (row_index, col_index)
        for row_index, row in enumerate(mask)
        for col_index, cell in enumerate(row)
        if cell is not None
    ]
    required_directions = min(3, len(coordinates))
    rng = random.Random(seed)

    for _ in range(attempts):
        order = coordinates[:]
        rng.shuffle(order)
        grid: list[list[str | None]] = [
            [None for _ in row] for row in mask
        ]
        used_directions: set[str] = set()

        for row_index, col_index in reversed(order):
            choices = [
                direction
                for direction in DIRECTIONS
                if _can_fly(grid, row_index, col_index, direction[1], direction[2])
            ]
            if not choices:
                break
            unused = [direction for direction in choices if direction[0] not in used_directions]
            direction = rng.choice(unused or choices)
            grid[row_index][col_index] = direction[0]
            used_directions.add(direction[0])
        else:
            if len(used_directions) < required_directions:
                continue
            candidate = tuple(tuple(row) for row in grid)
            if _clears_in_scan_order([list(row) for row in candidate]):
                return candidate

    raise ValueError("could not generate a scan-order-solvable layout")
