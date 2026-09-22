# Score-Based Stars Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Award 1–3 completion stars from a level’s final score as a percentage of its theoretical maximum score.

**Architecture:** `Game` will calculate maximum score from the initially loaded board and create a frozen `LevelSummary` containing score, maximum score, and star count. The percentage thresholds are globally fixed at 85% and 60%, so `levels.py` no longer contains time-based star configuration; time remains a failure constraint only.

**Tech Stack:** Python 3, pytest, Pygame application state.

---

### Task 1: Replace time/mistake star tests with score-ratio tests

**Files:**
- Modify: `tests/test_game.py:94-108`

- [ ] **Step 1: Write failing score boundary tests**

Replace the old elapsed/mistake parametrization with tests using a ten-arrow board, whose maximum score is `5 * 10 * 11 == 550`:

```python
@pytest.mark.parametrize(
    ("score", "expected_stars"),
    [(550, 3), (468, 3), (467, 2), (330, 2), (329, 1)],
)
def test_clear_summary_uses_score_ratio_star_rules(score, expected_stars):
    game = Game(board_factory([["R"] * 10]))
    game.board.arrow_grid[0][:9] = ["."] * 9
    game.score = score - 10
    game.click(0, 9)
    assert game.level_summary.score == score
    assert game.level_summary.max_score == 550
    assert game.level_summary.stars == expected_stars
```

Add a second test that clears a one-arrow board at the same score with varied elapsed time and mistake count, and asserts the star result is unchanged.

- [ ] **Step 2: Run the focused test and verify the expected failure**

Run:

```powershell
python -m pytest tests/test_game.py -k "star" -v
```

Expected: FAIL because the current `LevelSummary` lacks `score` and `max_score`, and scoring still uses `star_thresholds`.

### Task 2: Implement score-based summary calculation

**Files:**
- Modify: `src/game.py:30-105`, `src/game.py:134-169`, `src/game.py:283-305`

- [ ] **Step 1: Define the frozen result fields and pure ratio function**

Change the summary and helper to the following interface:

```python
@dataclass(frozen=True)
class LevelSummary:
    elapsed_seconds: float
    mistakes: int
    score: int
    max_score: int
    stars: int


def _stars_for_score(score: int, max_score: int) -> int:
    if score * 100 >= max_score * 85:
        return 3
    if score * 100 >= max_score * 60:
        return 2
    return 1
```

Use integer multiplication rather than floating-point ratios, and reject a non-positive `max_score` with `ValueError`.

- [ ] **Step 2: Store maximum score when a board is loaded**

In both `_load_level()` and `load_custom_board()`, compute `initial_arrow_count = board.remaining_arrows()` and set:

```python
self.max_score = 5 * initial_arrow_count * (initial_arrow_count + 1)
```

Keep `score = 0` in `_reset_runtime()` so restart and next-level attempts are independent. In `load_state()`, recompute `max_score` from the restored board’s initial semantics only if saved state includes it; otherwise preserve the score from the save and calculate a safe ceiling from the current board plus history is unavailable. Prefer adding `max_score` to `to_dict()` and restoring it in `load_state()` to keep mid-level saves accurate.

- [ ] **Step 3: Build a score-based LevelSummary when the last arrow clears**

Replace the old `_stars_for(elapsed_seconds, mistakes, self.star_thresholds[...])` invocation with:

```python
self.level_summary = LevelSummary(
    self.elapsed_seconds,
    self.mistakes,
    self.score,
    self.max_score,
    _stars_for_score(self.score, self.max_score),
)
```

Remove the `star_thresholds` constructor parameter and validation without changing `time_limits`.

- [ ] **Step 4: Run focused tests and then the full suite**

Run:

```powershell
python -m pytest tests/test_game.py -v
python -m pytest -v
```

Expected: all tests pass after downstream callers and tests are updated in Tasks 3–4.

### Task 3: Remove stale campaign time-star configuration

**Files:**
- Modify: `src/levels.py:467-471`
- Modify: `main.py:5-10`, `main.py:92-98`
- Modify: `tests/test_levels.py:131-134`

- [ ] **Step 1: Write the failing configuration test**

Replace `test_campaign_defines_one_increasing_star_threshold_pair_per_level` with:

```python
def test_campaign_has_time_limits_but_no_time_based_star_thresholds():
    assert len(LEVEL_TIME_LIMITS) == len(LEVEL_FACTORIES)
    assert "LEVEL_STAR_THRESHOLDS" not in vars(levels)
```

Import `src.levels as levels` and retain the existing named-level assertions.

- [ ] **Step 2: Run it to verify the old constant fails the new rule**

Run:

```powershell
python -m pytest tests/test_levels.py -k "thresholds" -v
```

Expected: FAIL because `LEVEL_STAR_THRESHOLDS` still exists.

- [ ] **Step 3: Remove the constant and its application wiring**

Delete `LEVEL_STAR_THRESHOLDS` from `src/levels.py`; remove its import and the `star_thresholds=...` keyword from `main.py`. Keep `LEVEL_TIME_LIMITS` unchanged.

- [ ] **Step 4: Verify configuration and application tests**

Run:

```powershell
python -m pytest tests/test_levels.py tests/test_game.py tests/test_ui.py -v
python -m compileall -q main.py src tests
```

Expected: all selected tests pass and compileall exits with code 0.

### Task 4: Update accurate documentation and deliver the branch

**Files:**
- Modify: `docs/course-report.md:57-59`, `docs/course-report.md:114-115`

- [ ] **Step 1: Update the course report’s star description**

Replace the time/mistake rule with the verified 85% / 60% score-ratio rule. State that time can still produce `time_up`, and a blocker still interrupts combo, but neither directly selects a star value.

- [ ] **Step 2: Run final verification**

Run:

```powershell
python -m pytest -v
python -m compileall -q main.py src tests
git diff --check
```

Expected: all tests pass, compileall exits with code 0, and `git diff --check` prints no whitespace errors.

- [ ] **Step 3: Commit, push, and merge**

```powershell
git add main.py src/game.py src/levels.py tests/test_game.py tests/test_levels.py docs/course-report.md docs/superpowers/specs/2026-09-22-score-based-stars-design.md docs/superpowers/plans/2026-09-22-score-based-stars.md
git commit -m "feat: rate cleared levels by score"
git push -u origin codex/p1-game-completion
git switch main
git merge --no-ff codex/p1-game-completion
git push origin main
```

Before switching branches, confirm that unrelated modified files are untouched. If local `main` has commits not in this branch, merge `main` into the feature branch, rerun the final verification, then merge the feature branch into `main`.

## Self-review

- Spec coverage: Task 1 establishes 85% and 60% boundaries; Task 2 computes and freezes level score data; Task 3 removes time-star configuration while preserving time limits; Task 4 updates the report and delivery workflow.
- Placeholder scan: no unimplemented behavior or unspecified thresholds remain.
- Type consistency: `LevelSummary.score`, `LevelSummary.max_score`, `_stars_for_score(score, max_score)`, and `Game.max_score` use integer scores throughout.
