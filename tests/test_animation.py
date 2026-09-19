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


def test_fly_out_animation_moves_up_for_up_direction():
    animation = FlyOutAnimation(2, 3, "U")
    animation.update(0.30)
    assert animation.offset_cells == pytest.approx((-2.0, 0.0))


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
