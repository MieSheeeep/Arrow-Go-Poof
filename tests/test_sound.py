"""Tests for the generated sound effects."""

from src.sound import SAMPLE_RATE, SoundManager, _wave


def test_wave_generates_expected_byte_length():
    data = _wave(0.1, 440, 0.5)

    assert len(data) == int(SAMPLE_RATE * 0.1) * 2


def test_wave_supports_sweep_and_square_shapes():
    assert len(_wave(0.2, 300, 0.5, sweep_to=900)) > 0
    assert len(_wave(0.2, 300, 0.5, shape="square")) > 0


def test_sound_manager_constructs_and_plays_safely():
    manager = SoundManager()

    manager.play("fly")
    manager.play("collide")
    manager.play("unknown")
