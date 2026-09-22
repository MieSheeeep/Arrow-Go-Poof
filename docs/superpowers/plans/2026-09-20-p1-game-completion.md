# P1 Game Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Complete the remaining PRD P1 work: level timing, time-and-mistake star ratings, in-game restart/menu controls, and full clear/failure result pages.

**Architecture:** src/game.py owns elapsed time, thresholds, terminal summaries, and state transitions. src/ui.py formats and renders Game state and supplies hit rectangles. main.py routes a button click before treating input as a board click.

**Tech Stack:** Python 3.10+, Pygame 2.6+, pytest 8+

---

## File map

- Modify src/game.py: LevelSummary, elapsed time, star calculation, return_to_menu.
- Modify src/levels.py: fixed time limits for the three picture levels.
- Modify src/ui.py: HUD timer, game controls, and terminal panels.
- Modify main.py: explicit restart, retry, and menu routing.
- Modify tests/test_game.py, tests/test_levels.py, tests/test_ui.py, tests/test_main.py.
- Modify README.md, docs/course-report.md, docs/test-plan.md, and runtime screenshots.

The existing P1 fly-out, collision-return, and persistent-red feedback are already present. Retain those implementations and treat the final full test run as their regression test.

### Task 1: Add a timer that only runs in PLAYING

**Files:**
- Modify: tests/test_game.py
- Modify: src/game.py

- [ ] **Step 1: Write failing timer tests in tests/test_game.py.**

~~~python
def test_level_timer_advances_only_while_playing_and_freezes_on_clear():
    game = Game(board_factory([["R"]]))
    game.update(4.25)
    game.click(0, 0)
    game.update(8.0)

    assert game.elapsed_seconds == pytest.approx(4.25)
    assert game.level_summary is not None
    assert game.level_summary.elapsed_seconds == pytest.approx(4.25)


def test_timer_does_not_start_in_menu_and_restart_resets_it():
    game = Game(board_factory([["R"]]), start_in_menu=True)
    game.update(5.0)
    game.start()
    game.update(2.5)
    game.restart()

    assert game.elapsed_seconds == 0.0
    assert game.level_summary is None
~~~

- [ ] **Step 2: Verify red.**

Run: python -m pytest tests/test_game.py -q

Expected: FAIL because elapsed_seconds and level_summary do not exist.

- [ ] **Step 3: Add minimal time state in src/game.py.**

~~~python
from dataclasses import dataclass


@dataclass(frozen=True)
class LevelSummary:
    elapsed_seconds: float
    mistakes: int
    stars: int
~~~

At the end of _reset_runtime add:

~~~python
self.elapsed_seconds = 0.0
self.level_summary: LevelSummary | None = None
~~~

At the start of update, after validating delta_time, add:

~~~python
if self.state is GameState.PLAYING:
    self.elapsed_seconds += delta_time
~~~

- [ ] **Step 4: Verify green.**

Run: python -m pytest tests/test_game.py -q

Expected: PASS.

- [ ] **Step 5: Commit.**

~~~bash
git add src/game.py tests/test_game.py && git commit -m "feat: track elapsed time for active levels"
~~~

### Task 2: Add campaign thresholds and clear-star summaries

**Files:**
- Modify: tests/test_game.py
- Modify: tests/test_levels.py
- Modify: src/game.py
- Modify: src/levels.py
- Modify: main.py

Use these fixed limits: Apple (90.0, 150.0), Bead Ball (80.0, 130.0), Moon Kitty (150.0, 240.0). Three stars requires no mistakes and the first limit; two stars allows one mistake and the second limit; every other clear earns one star.

- [ ] **Step 1: Write failing configuration and score tests.**

~~~python
# tests/test_levels.py
def test_campaign_defines_one_increasing_star_threshold_pair_per_level():
    assert LEVEL_STAR_THRESHOLDS == ((90.0, 150.0), (80.0, 130.0), (150.0, 240.0))
    assert len(LEVEL_STAR_THRESHOLDS) == len(LEVEL_FACTORIES)
    assert all(0 < three < two for three, two in LEVEL_STAR_THRESHOLDS)


# tests/test_game.py
@pytest.mark.parametrize(
    ("elapsed", "mistakes", "expected_stars"),
    [(9.5, 0, 3), (15.0, 1, 2), (25.0, 0, 1), (9.5, 2, 1)],
)
def test_clear_summary_uses_time_and_mistake_star_rules(elapsed, mistakes, expected_stars):
    game = Game(board_factory([["R"]]), star_thresholds=((10.0, 20.0),))
    game.elapsed_seconds = elapsed
    game.mistakes = mistakes
    game.click(0, 0)

    assert game.level_summary == LevelSummary(elapsed, mistakes, expected_stars)
~~~

Import LevelSummary and LEVEL_STAR_THRESHOLDS into their respective test modules.

- [ ] **Step 2: Verify red.**

Run: python -m pytest tests/test_game.py tests/test_levels.py -q

Expected: FAIL because star_thresholds and LEVEL_STAR_THRESHOLDS do not exist.

- [ ] **Step 3: Add level data before LEVEL_NAMES in src/levels.py.**

~~~python
LEVEL_STAR_THRESHOLDS = (
    (90.0, 150.0),  # ENCHANTED APPLE
    (80.0, 130.0),  # BEAD BALL
    (150.0, 240.0),  # MOON KITTY
)
~~~

- [ ] **Step 4: Add validation, calculation, and summary construction in src/game.py.**

Extend Game.__init__ with keyword-only star_thresholds: Sequence[tuple[float, float]] | None = None. After level-name validation, add:

~~~python
if star_thresholds is None:
    self.star_thresholds = tuple((60.0, 120.0) for _ in self.level_factories)
else:
    self.star_thresholds = tuple(star_thresholds)
    if len(self.star_thresholds) != len(self.level_factories):
        raise ValueError("star_thresholds must match the number of level factories")
    if any(
        len(limits) != 2
        or not all(math.isfinite(limit) and limit > 0 for limit in limits)
        or limits[0] >= limits[1]
        for limits in self.star_thresholds
    ):
        raise ValueError("each star threshold pair must be positive and increasing")
~~~

Add the helper:

~~~python
def _stars_for(elapsed_seconds: float, mistakes: int, limits: tuple[float, float]) -> int:
    three_star_limit, two_star_limit = limits
    if elapsed_seconds <= three_star_limit and mistakes == 0:
        return 3
    if elapsed_seconds <= two_star_limit and mistakes <= 1:
        return 2
    return 1
~~~

When the final arrow clears, set this before CLEARED:

~~~python
self.level_summary = LevelSummary(
    self.elapsed_seconds,
    self.mistakes,
    _stars_for(self.elapsed_seconds, self.mistakes, self.star_thresholds[self.level_index]),
)
self.state = GameState.CLEARED
~~~

- [ ] **Step 5: Pass thresholds from main.py, verify, and commit.**

~~~python
from src.levels import LEVEL_FACTORIES, LEVEL_NAMES, LEVEL_STAR_THRESHOLDS

game = Game(
    LEVEL_FACTORIES,
    start_in_menu=True,
    level_names=LEVEL_NAMES,
    star_thresholds=LEVEL_STAR_THRESHOLDS,
)
~~~

Run: python -m pytest tests/test_game.py tests/test_levels.py -q

Expected: PASS for all threshold and star outcomes.

~~~bash
git add src/game.py src/levels.py main.py tests/test_game.py tests/test_levels.py && git commit -m "feat: add timed star ratings for campaign levels"
~~~

### Task 3: Render the timer, ratings, and complete action controls

**Files:**
- Modify: tests/test_ui.py
- Modify: src/ui.py

- [ ] **Step 1: Write failing formatter and geometry tests.**

~~~python
@pytest.mark.parametrize(
    ("seconds", "expected"),
    [(0.0, "00:00.00"), (9.5, "00:09.50"), (65.125, "01:05.12")],
)
def test_format_elapsed_time(seconds, expected):
    assert format_elapsed_time(seconds) == expected


def test_gameplay_and_result_controls_have_distinct_hit_areas():
    pygame.font.init()
    ui = UI(pygame.Surface(WINDOW_SIZE), Game(create_tree_board))
    rects = [
        ui.restart_rect(), ui.menu_rect(), ui.result_primary_rect(),
        ui.result_retry_rect(), ui.result_menu_rect(),
    ]
    assert all(rect.width > 0 and rect.height > 0 for rect in rects)
    assert not ui.restart_rect().colliderect(ui.menu_rect())
    assert not ui.result_primary_rect().colliderect(ui.result_retry_rect())
    assert not ui.result_retry_rect().colliderect(ui.result_menu_rect())
~~~

- [ ] **Step 2: Verify red.**

Run: python -m pytest tests/test_ui.py -q

Expected: FAIL because the formatter and new rectangle methods are absent.

- [ ] **Step 3: Add the formatter and rectangle API in src/ui.py.**

~~~python
def format_elapsed_time(seconds: float) -> str:
    minutes, remaining = divmod(seconds, 60.0)
    return f"{int(minutes):02d}:{remaining:05.2f}"
~~~

~~~python
def restart_rect(self) -> pygame.Rect:
    return pygame.Rect(842, 34, 128, 38)

def menu_rect(self) -> pygame.Rect:
    return pygame.Rect(230, 34, 112, 38)

def result_primary_rect(self) -> pygame.Rect:
    return pygame.Rect(490, 505, 220, 48)

def result_retry_rect(self) -> pygame.Rect:
    return pygame.Rect(490, 561, 220, 42)

def result_menu_rect(self) -> pygame.Rect:
    return pygame.Rect(490, 611, 220, 42)
~~~

- [ ] **Step 4: Implement HUD and terminal-panel rendering.**

In _draw_hud, retain level number/name, lives, mistakes, and arrows; add TIME plus format_elapsed_time(self.game.elapsed_seconds), then draw MENU and RESTART with the existing green rounded-button style.

In _draw_result_panel, use a centered pygame.Rect(0, 0, 500, 540). On CLEARED render LEVEL CLEAR or ALL CLEAR, exact time, mistakes, and:

~~~python
summary = self.game.level_summary
stars = "★" * summary.stars + "☆" * (3 - summary.stars)
~~~

On FAILED render TRY AGAIN, frozen time, and mistakes without stars. Draw RESTART LEVEL on failure, NEXT LEVEL on non-final clear, RESTART GAME on final clear, RETRY LEVEL only on clear, and MAIN MENU on every terminal page.

- [ ] **Step 5: Verify green and commit.**

Run: python -m pytest tests/test_ui.py -q

Expected: PASS.

~~~bash
git add src/ui.py tests/test_ui.py && git commit -m "feat: show timer ratings and in-game controls"
~~~

### Task 4: Route controls before grid clicks

**Files:**
- Modify: tests/test_game.py
- Modify: tests/test_main.py
- Modify: src/game.py
- Modify: main.py

- [ ] **Step 1: Write failing Game and router tests.**

Give StubUI these distinct rectangles:

~~~python
def restart_rect(self): return pygame.Rect(0, 0, 100, 40)
def menu_rect(self): return pygame.Rect(110, 0, 100, 40)
def result_primary_rect(self): return pygame.Rect(220, 0, 100, 40)
def result_retry_rect(self): return pygame.Rect(330, 0, 100, 40)
def result_menu_rect(self): return pygame.Rect(440, 0, 100, 40)
~~~

Add these routing tests:

~~~python
def test_playing_restart_button_resets_level_without_routing_to_board(monkeypatch):
    game, ui = make_game(), StubUI()
    game.click(0, 0)
    monkeypatch.setattr(game, "click", lambda *_: pytest.fail("restart routed to board"))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (10, 10)})

    assert process_event(event, game, ui) is True
    assert game.board.get_cell(0, 0) == "R"


def test_playing_menu_button_returns_to_start_state_without_routing_to_board(monkeypatch):
    game, ui = make_game(), StubUI()
    monkeypatch.setattr(game, "click", lambda *_: pytest.fail("menu routed to board"))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (120, 10)})

    assert process_event(event, game, ui) is True
    assert game.state is GameState.START
~~~

Also add a three-level return_to_menu test asserting START, level index 0, three lives, elapsed 0.0, and no animations.

- [ ] **Step 2: Verify red.**

Run: python -m pytest tests/test_game.py tests/test_main.py -q

Expected: FAIL because menu reset and button routing are absent.

- [ ] **Step 3: Implement return_to_menu in src/game.py.**

~~~python
def return_to_menu(self) -> None:
    self.level_index = 0
    self._load_level()
    self._reset_runtime()
    self.state = GameState.START
~~~

- [ ] **Step 4: Route every UI action in main.py.**

~~~python
elif game.state in {GameState.CLEARED, GameState.FAILED}:
    if ui.result_primary_rect().collidepoint(event.pos):
        if game.state is GameState.FAILED:
            game.restart()
        elif game.has_next_level:
            game.next_level()
        else:
            game.restart_campaign()
    elif game.state is GameState.CLEARED and ui.result_retry_rect().collidepoint(event.pos):
        game.restart()
    elif ui.result_menu_rect().collidepoint(event.pos):
        game.return_to_menu()
elif game.state is GameState.PLAYING:
    if ui.restart_rect().collidepoint(event.pos):
        game.restart()
    elif ui.menu_rect().collidepoint(event.pos):
        game.return_to_menu()
    else:
        cell = ui.cell_at(event.pos)
        if cell is not None:
            game.click(*cell)
~~~

- [ ] **Step 5: Add retry coverage, verify green, and commit.**

~~~python
def test_clear_retry_button_restarts_current_level():
    game, ui = make_game(), StubUI()
    game.state = GameState.CLEARED
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (340, 10)})

    assert process_event(event, game, ui) is True
    assert game.state is GameState.PLAYING
    assert game.board.get_cell(0, 0) == "R"
~~~

Run: python -m pytest tests/test_game.py tests/test_main.py -q

Expected: PASS and control clicks never call ui.cell_at.

~~~bash
git add src/game.py main.py tests/test_game.py tests/test_main.py && git commit -m "feat: add restart retry and menu navigation controls"
~~~

### Task 5: Refresh documentation and complete P1 acceptance

**Files:**
- Modify: README.md
- Modify: docs/course-report.md
- Modify: docs/test-plan.md
- Replace: docs/assets/runtime-start.png
- Replace: docs/assets/runtime-gameplay.png
- Replace: docs/assets/runtime-result.png
- Create: docs/assets/runtime-failed.png

- [ ] **Step 1: Update documentation.**

In README, document timer, stars, RESTART, MENU, RETRY LEVEL, and MAIN MENU. State the exact 3/2/1-star rule from Task 2. In the course report, add timer/rating design and T09 timer freeze/reset, T10 rating outcomes, T11 in-game restart/menu routing. In the test plan, replace planned T09 with 计时与星级正确结算 and add T11 游戏中重新开始与返回主菜单不触发棋盘点击.

- [ ] **Step 2: Capture the four runtime pages.**

Run python main.py. Capture start, active gameplay with timer/buttons, clear with time/stars/retry, and failure with frozen time/mistakes/menu. Save them to the exact filenames above and verify the README embeds render.

- [ ] **Step 3: Run automated and manual acceptance checks.**

~~~bash
python -m pytest -q
python -m compileall -q src main.py tests
git diff --check
~~~

Expected: all tests pass, compilation has no errors, and the diff check has no whitespace errors. Copy the printed test total exactly into README and the report.

In the live game, wait five seconds on the menu (time stays 00:00.00); start, restart, and return to menu; clear a level and verify time/stars/retry/next; fail after three blocked clicks and verify frozen time/restart/menu; confirm existing fly-out/collision animations still permit legal clicks on other arrows.

- [ ] **Step 4: Commit and push the evidence.**

~~~bash
git add README.md docs/course-report.md docs/test-plan.md docs/assets/runtime-start.png docs/assets/runtime-gameplay.png docs/assets/runtime-result.png docs/assets/runtime-failed.png && git commit -m "docs: document P1 scoring controls and test evidence"
git push origin main
~~~

## Coverage check

- Timer, freeze, and reset: Task 1.
- Time-and-mistake stars: Task 2.
- Complete menu/result pages and course-required in-game restart: Tasks 3 and 4.
- Existing P1 animation/feedback: final regression suite in Task 5.
- Combo, audio, particles, executable packaging, hints, undo, and random levels remain P2/P3 and are intentionally out of scope.

