import math

import pytest

from src.animation import CollisionAnimation, FlyOutAnimation


def test_fly_out_animation_moves_right_and_finishes():
    animation = FlyOutAnimation(2, 3, "R")

    assert animation.offset_cells == (0.0, 0.0)
    assert animation.color_state == "normal"

    animation.update(0.15)
    assert 0.0 < animation.offset_cells[1] < 2.0
    assert animation.offset_cells[0] == 0.0
    assert animation.is_finished is False

    animation.update(0.15)
    assert animation.is_finished is True
    assert animation.offset_cells == pytest.approx((0.0, 2.0))


@pytest.mark.parametrize(
    ("direction", "expected"),
    [
        ("U", (-2.0, 0.0)),
        ("D", (2.0, 0.0)),
        ("L", (0.0, -2.0)),
        ("R", (0.0, 2.0)),
    ],
)
def test_fly_out_animation_moves_in_each_direction(direction, expected):
    animation = FlyOutAnimation(2, 3, direction)
    animation.update(0.30)
    assert animation.offset_cells == pytest.approx(expected)


def test_collision_animation_changes_to_error_at_impact_then_retracts():
    animation = CollisionAnimation(1, 1, (1, 3), "R")

    animation.update(0.06)
    assert animation.phase == "approach"
    assert animation.color_state == "normal"
    assert animation.offset_cells == pytest.approx((0.0, 1.0))

    animation.update(0.06)
    assert animation.phase == "impact"
    assert animation.color_state == "error"
    assert animation.offset_cells == pytest.approx((0.0, 2.0))

    animation.update(0.08)
    assert animation.phase == "retreat"
    assert animation.color_state == "error"

    animation.update(0.16)
    assert animation.phase == "done"
    assert animation.is_finished is True
    assert animation.offset_cells == pytest.approx((0.0, 0.0))


@pytest.mark.parametrize("direction", ["X", "", "RR"])
def test_animation_rejects_unknown_direction(direction):
    with pytest.raises(ValueError):
        FlyOutAnimation(0, 0, direction)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: FlyOutAnimation(0, 0, "R", duration=0),
        lambda: FlyOutAnimation(0, 0, "R", duration=math.nan),
        lambda: FlyOutAnimation(0, 0, "R", duration=math.inf),
        lambda: CollisionAnimation(0, 0, (0, 1), "R", approach_duration=0),
        lambda: CollisionAnimation(0, 0, (0, 1), "R", impact_duration=math.nan),
    ],
)
def test_animation_rejects_non_positive_or_non_finite_durations(factory):
    with pytest.raises(ValueError):
        factory()


@pytest.mark.parametrize("delta_time", [-0.01, math.nan, math.inf])
def test_animation_rejects_invalid_delta_time(delta_time):
    animation = FlyOutAnimation(0, 0, "R")
    with pytest.raises(ValueError):
        animation.update(delta_time)


def test_animation_clamps_oversized_update_to_completion():
    animation = FlyOutAnimation(0, 0, "R")
    animation.update(10.0)

    assert animation.is_finished is True
    assert animation.elapsed == animation.duration
    assert animation.offset_cells == pytest.approx((0.0, 2.0))


def test_collision_phase_boundary_tolerates_float_accumulation():
    animation = CollisionAnimation(0, 0, (0, 1), "R")
    for _ in range(10):
        animation.update(0.012)

    assert animation.phase == "impact"
    assert animation.color_state == "error"
