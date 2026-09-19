"""Deterministic development-time generator for solvable arrow layouts."""

from __future__ import annotations

from dataclasses import dataclass
import random


DIRECTIONS = (
    ("U", -1, 0),
    ("D", 1, 0),
    ("L", 0, -1),
    ("R", 0, 1),
)
@dataclass(frozen=True)
class GeneratedLayout:
    """A frozen arrow grid plus one verified order that clears it."""

    arrow_grid: tuple[tuple[str | None, ...], ...]
    solution: tuple[tuple[int, int], ...]


def _validate_mask(mask: tuple[tuple[str | None, ...], ...]) -> None:
    if not mask or not mask[0] or any(len(row) != len(mask[0]) for row in mask):
        raise ValueError("mask must be a non-empty rectangular grid")
    if not any(cell is not None for row in mask for cell in row):
        raise ValueError("mask must contain at least one puzzle cell")


def _is_clear_from_remaining(
    remaining: set[tuple[int, int]],
    row: int,
    col: int,
    row_delta: int,
    col_delta: int,
    rows: int,
    cols: int,
) -> bool:
    """Return whether a ray has no still-present arrow cells."""
    row += row_delta
    col += col_delta
    while 0 <= row < rows and 0 <= col < cols:
        if (row, col) in remaining:
            return False
        row += row_delta
        col += col_delta
    return True


def generate_solvable_layout(
    mask: tuple[tuple[str | None, ...], ...], seed: int
) -> GeneratedLayout:
    """Create a reproducible varied layout and its valid forward clear order.

    This helper is for design-time use.  The game stores its generated result as
    constants, so normal play never depends on random generation.
    """
    _validate_mask(mask)
    if type(seed) is not int:
        raise ValueError("seed must be an integer")

    coordinates = [
        (row_index, col_index)
        for row_index, row in enumerate(mask)
        for col_index, cell in enumerate(row)
        if cell is not None
    ]
    # A small lower bound prevents a large picture from visually collapsing
    # into one or two directions without over-constraining reverse placement.
    minimum_per_direction = len(coordinates) // 30
    required_directions = min(3, len(coordinates))
    rng = random.Random(seed)

    # Build the *forward* solution directly.  On every step we remove a cell
    # with an open ray among the remaining arrows, so the stored order is
    # guaranteed playable.  This avoids the artificial, stripe-like layouts
    # produced by forcing a row-major removal order.
    remaining = set(coordinates)
    solution: list[tuple[int, int]] = []
    grid: list[list[str | None]] = [[None for _ in row] for row in mask]
    direction_counts = {direction: 0 for direction, _, _ in DIRECTIONS}
    rows = len(mask)
    cols = len(mask[0])

    while remaining:
        available = [
            (row_index, col_index, direction)
            for row_index, col_index in sorted(remaining)
            for direction in DIRECTIONS
            if _is_clear_from_remaining(
                remaining,
                row_index,
                col_index,
                direction[1],
                direction[2],
                rows,
                cols,
            )
        ]
        fewest_uses = min(direction_counts[direction[2][0]] for direction in available)
        balanced_choices = [
            candidate
            for candidate in available
            if direction_counts[candidate[2][0]] == fewest_uses
        ]
        row_index, col_index, direction = rng.choice(balanced_choices)
        grid[row_index][col_index] = direction[0]
        direction_counts[direction[0]] += 1
        remaining.remove((row_index, col_index))
        solution.append((row_index, col_index))

    used_directions = {direction for direction, count in direction_counts.items() if count}
    if len(used_directions) < required_directions or (
        minimum_per_direction
        and any(count < minimum_per_direction for count in direction_counts.values())
    ):
        raise ValueError("could not generate a varied solvable layout")
    return GeneratedLayout(
        arrow_grid=tuple(tuple(row) for row in grid),
        solution=tuple(solution),
    )


def generate_solvable_arrow_grid(
    mask: tuple[tuple[str | None, ...], ...], seed: int
) -> tuple[tuple[str | None, ...], ...]:
    """Return only the arrow grid for callers that do not need its solution."""
    return generate_solvable_layout(mask, seed).arrow_grid
