"""程序化生成的轻量音效，无需外部音频文件。"""

from __future__ import annotations

import array
import math

import pygame

SAMPLE_RATE = 44100


def _wave(
    duration: float,
    frequency: float,
    volume: float,
    *,
    sweep_to: float | None = None,
    shape: str = "sine",
) -> bytes:
    """生成一段带衰减包络的波形，返回 16-bit 有符号单声道字节流。"""
    count = max(1, int(SAMPLE_RATE * duration))
    samples = array.array("h")
    for index in range(count):
        ratio = index / count
        freq = (
            frequency
            if sweep_to is None
            else frequency + (sweep_to - frequency) * ratio
        )
        phase = 2 * math.pi * freq * index / SAMPLE_RATE
        value = math.sin(phase)
        if shape == "square":
            value = 1.0 if value >= 0 else -1.0
        envelope = 1.0 - ratio
        samples.append(int(value * volume * envelope * 32767))
    return samples.tobytes()


class SoundManager:
    """播放程序生成的短音效；音频不可用时静默禁用。"""

    def __init__(self) -> None:
        self.enabled = False
        self._effects: dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)
            self._effects = {
                "fly": pygame.mixer.Sound(
                    buffer=_wave(0.09, 620, 0.45, sweep_to=980)
                ),
                "collide": pygame.mixer.Sound(
                    buffer=_wave(0.14, 150, 0.55, shape="square")
                ),
                "clear": pygame.mixer.Sound(
                    buffer=_wave(0.30, 523, 0.4, sweep_to=1046)
                ),
                "fail": pygame.mixer.Sound(
                    buffer=_wave(0.32, 440, 0.4, sweep_to=110)
                ),
            }
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def play(self, name: str) -> None:
        if not self.enabled:
            return
        effect = self._effects.get(name)
        if effect is not None:
            effect.play()
