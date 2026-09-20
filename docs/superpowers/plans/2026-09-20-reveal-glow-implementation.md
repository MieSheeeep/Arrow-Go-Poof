# Immediate Coloured Reveal Glow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each successfully clicked arrow reveal its bead pixel with an immediate, same-colour flash that fades during the first 0.22 seconds of its fly-out.

**Architecture:** Leave game rules unchanged. The UI derives a short-lived glow from each `FlyOutAnimation` origin and elapsed time, draws it above the newly revealed pixel, and then draws the moving arrow. The colour comes from the existing `COLOR_MAP` lookup for `Board.color_grid`.

**Tech Stack:** Python 3.13, Pygame 2.6, pytest 8.

---

### Task 1: Define deterministic glow timing

**Files:**

- Modify: `src/ui.py:40-100`
- Test: `tests/test_ui.py`

- [ ] **Step 1: Add the failing test**

```python
from src.animation import FlyOutAnimation
from src.ui import REVEAL_GLOW_DURATION, reveal_glow_strength


def test_reveal_glow_strength_is_immediate_then_fades_to_zero():
    animation = FlyOutAnimation(0, 0, "R")
    assert reveal_glow_strength(animation) == 1.0
    animation.update(REVEAL_GLOW_DURATION / 2)
    assert reveal_glow_strength(animation) == pytest.approx(0.5)
    animation.update(REVEAL_GLOW_DURATION / 2)
    assert reveal_glow_strength(animation) == 0.0
```

- [ ] **Step 2: Verify RED**

Run `python -m pytest tests/test_ui.py::test_reveal_glow_strength_is_immediate_then_fades_to_zero -q`.

Expected: collection fails because the duration constant and helper do not exist.

- [ ] **Step 3: Implement the timing helper**

```python
REVEAL_GLOW_DURATION = 0.22


def reveal_glow_strength(animation: FlyOutAnimation) -> float:
    """Return the immediate-to-zero intensity for a successful reveal."""
    return max(0.0, 1.0 - animation.elapsed / REVEAL_GLOW_DURATION)
```

Import `FlyOutAnimation` in `src/ui.py`.

- [ ] **Step 4: Verify GREEN**

Run `python -m pytest tests/test_ui.py::test_reveal_glow_strength_is_immediate_then_fades_to_zero -q`.

Expected: PASS.

### Task 2: Render the colour-matched flash

**Files:**

- Modify: `src/ui.py:390-425`
- Test: `tests/test_ui.py`

- [ ] **Step 1: Add the failing rendering test**

```python
def test_successful_flyout_immediately_brightens_the_revealed_pixel():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(lambda: Board([["R"]], [["ball_red"]]))
    ui = UI(screen, game)
    game.click(0, 0)
    ui.draw()
    assert sum(screen.get_at(ui.layout.cell_rect(0, 0).center)[:3]) > sum(COLOR_MAP["ball_red"])
```

- [ ] **Step 2: Verify RED**

Run `python -m pytest tests/test_ui.py::test_successful_flyout_immediately_brightens_the_revealed_pixel -q`.

Expected: FAIL because no reveal glow is drawn.

- [ ] **Step 3: Implement the overlay**

Add `_draw_reveal_glow(self, animation: FlyOutAnimation)` before `_draw_animations()`. It must resolve the origin colour, draw a rounded overlay with alpha `round(145 * strength)`, add a white outline with alpha `round(120 * strength)`, and return after 0.22 seconds. Call it for each `FlyOutAnimation` before drawing that animation's moved arrow.

- [ ] **Step 4: Verify GREEN and commit**

Run `python -m pytest tests/test_ui.py -q`; expect PASS. Then commit `src/ui.py` and `tests/test_ui.py` with message `feat: add immediate coloured reveal glow`.

### Task 3: Capture runtime evidence and validate

**Files:**

- Modify: `docs/assets/runtime-gameplay.png`

- [ ] **Step 1: Capture the active fly-out frame**

Use dummy SDL to start a campaign game, click a clear arrow, draw immediately, and save `docs/assets/runtime-gameplay.png`.

- [ ] **Step 2: Verify and commit**

Run `python -m pytest -q`, `python -m compileall -q main.py src tests`, and `git diff --check`. Expect all checks to pass. Commit the screenshot with message `docs: refresh reveal glow gameplay capture`.
