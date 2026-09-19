# Fixed Art Levels and Main Menu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the small FLOWER/SUN levels with fixed, large, visually recognizable pixel-art puzzles whose varied arrow layouts are reproducibly generated and proven solvable, and upgrade the opening screen into a proper one-button main menu.

**Architecture:** `src/level_generator.py` is a pure development/test utility: it constructs a solvable arrow layout and its forward removal order from a color mask and fixed seed. `src/levels.py` stores frozen tuple constants generated from that utility, so the runtime never varies. `UI` draws an art-directed main menu from existing primitive shapes; `Game` and Board rules remain unchanged.

**Tech Stack:** Python 3.10+, Pygame 2.6+, pytest 8+

---

### Task 1: Add deterministic solvable-layout generator

**Files:**
- Create: `src/level_generator.py`
- Create: `tests/test_level_generator.py`

- [ ] **Step 1: Write failing generator tests**

Create `tests/test_level_generator.py` with a compact irregular mask and assertions for determinism, direction coverage, and a playable sequence:

```python
from src.board import Board
from src.level_generator import generate_solvable_arrow_grid


MASK = (
    (None, "pixel", None),
    ("pixel", "pixel", "pixel"),
    (None, "pixel", None),
)


def _clear_in_scan_order(grid):
    board = Board([list(row) for row in grid], [list(row) for row in MASK])
    moves = 0
    while not board.is_cleared():
        available = [
            (row, col)
            for row, values in enumerate(board.arrow_grid)
            for col, cell in enumerate(values)
            if cell in {"U", "D", "L", "R"} and board.can_fly(row, col)
        ]
        assert available
        assert board.click(*available[0]).success
        moves += 1
    return moves


def test_generator_is_deterministic_and_preserves_mask():
    first = generate_solvable_arrow_grid(MASK, seed=20260919)
    second = generate_solvable_arrow_grid(MASK, seed=20260919)
    assert first == second
    assert [cell is None for row in first for cell in row] == [
        cell is None for row in MASK for cell in row
    ]


def test_generated_grid_is_playable_and_uses_multiple_directions():
    grid = generate_solvable_arrow_grid(MASK, seed=9)
    assert _clear_in_scan_order(grid) == 5
    assert len({cell for row in grid for cell in row if cell is not None}) >= 3
```

- [ ] **Step 2: Run tests to verify RED**

Run `python -m pytest tests/test_level_generator.py -q`. Expected: collection fails because `src.level_generator` does not exist.

- [ ] **Step 3: Implement reverse-order generator**

Create `src/level_generator.py`. `generate_solvable_arrow_grid(mask, seed)` must:

1. collect all non-`None` coordinates;
2. use `random.Random(seed)` and a deterministic shuffled forward removal order;
3. add coordinates in reverse removal order;
4. choose a random direction whose ray contains no already placed arrow before `None` or a grid edge;
5. retry a bounded number of shuffled orders before raising `ValueError`.

Use these interfaces:

```python
DIRECTIONS = (("U", -1, 0), ("D", 1, 0), ("L", 0, -1), ("R", 0, 1))

def generate_solvable_arrow_grid(
    mask: tuple[tuple[str | None, ...], ...], seed: int, attempts: int = 200
) -> tuple[tuple[str | None, ...], ...]: ...
```

- [ ] **Step 4: Run focused tests to verify GREEN**

Run `python -m pytest tests/test_level_generator.py -q`. Expected: all generator tests pass.

- [ ] **Step 5: Commit generator**

```bash
git add src/level_generator.py tests/test_level_generator.py
git commit -m "feat: add deterministic solvable level generator"
```

### Task 2: Freeze large flower and sun pixel-art levels

**Files:**
- Modify: `src/levels.py`
- Modify: `tests/test_levels.py`

- [ ] **Step 1: Write failing level-quality tests**

Extend `tests/test_levels.py` with the following assertions:

```python
def test_flower_and_sun_are_large_fixed_pixel_art_levels():
    flower = create_flower_board()
    sun = create_sun_board()
    assert flower.rows == flower.cols == 13
    assert sun.rows == sun.cols == 13
    assert flower.remaining_arrows() >= 70
    assert sun.remaining_arrows() >= 80
    assert FLOWER_COLOR_GRID[3][6] == "center"
    assert FLOWER_COLOR_GRID[10][6] == "stem"
    assert SUN_COLOR_GRID[4][6] == "sun"
    assert SUN_COLOR_GRID[11][0] == "grass"


def test_frozen_art_layouts_match_their_generation_seeds():
    assert FLOWER_ARROW_GRID == generate_solvable_arrow_grid(
        FLOWER_COLOR_GRID, FLOWER_LAYOUT_SEED
    )
    assert SUN_ARROW_GRID == generate_solvable_arrow_grid(SUN_COLOR_GRID, SUN_LAYOUT_SEED)
```

- [ ] **Step 2: Run tests to verify RED**

Run `python -m pytest tests/test_levels.py -q`. Expected: failures because the old grids are small and the new seeds/colors do not exist.

- [ ] **Step 3: Replace the two color masks and freeze generated arrows**

Define 13×13 tuple masks in `src/levels.py`:

- FLOWER uses petal colors (`petal_light`, `petal`, `center`), a vertical `stem`, two `leaf` areas, and `None` outside the silhouette;
- SUN uses `ray`, `sun`, `sky`, and a three-row `grass` horizon.

Add fixed seeds:

```python
FLOWER_LAYOUT_SEED = 2026091901
SUN_LAYOUT_SEED = 2026091902
```

Run the generator once, copy its tuple output into `FLOWER_ARROW_GRID` and `SUN_ARROW_GRID`, and leave `create_flower_board`/`create_sun_board` as simple fresh-copy factories. Do not call the generator from a factory or from the runtime game loop.

- [ ] **Step 4: Extend UI colors and run level tests**

Add `petal_light`, `petal`, `center`, `stem`, `sun`, `ray`, and `sky` colors to `COLOR_MAP`. Run `python -m pytest tests/test_levels.py tests/test_ui.py -q`; expected: all pass and every factory remains independent.

- [ ] **Step 5: Commit the visual levels**

```bash
git add src/levels.py src/ui.py tests/test_levels.py tests/test_ui.py
git commit -m "feat: replace flower and sun with fixed pixel art levels"
```

### Task 3: Upgrade the opening screen into a main menu

**Files:**
- Modify: `src/ui.py`
- Modify: `tests/test_ui.py`

- [ ] **Step 1: Write failing rendering test**

Add a test that initializes Pygame fonts, creates a START-state game, draws the menu onto a 1200×800 surface, and asserts pixels at the title panel and start button differ from `BACKGROUND`.

```python
def test_start_screen_draws_a_distinct_title_panel_and_start_button():
    pygame.font.init()
    screen = pygame.Surface(WINDOW_SIZE)
    game = Game(LEVEL_FACTORIES, start_in_menu=True, level_names=LEVEL_NAMES)
    UI(screen, game).draw()
    assert screen.get_at((600, 250))[:3] == HUD_COLOR
    assert screen.get_at((600, 515))[:3] == (105, 181, 78)
```

- [ ] **Step 2: Run focused test to verify RED**

Run `python -m pytest tests/test_ui.py::test_start_screen_draws_a_distinct_title_panel_and_start_button -q`. Expected: failure until the new panel geometry is drawn.

- [ ] **Step 3: Implement art-directed main menu**

Revise `_draw_start_panel()` to draw a 1200×800 composition with a wide, dark-blue title band, a decorative small tree/arrow motif, the Chinese title `一箭又一箭`, a one-line rule, and one green `START GAME` button. Keep `start_rect()` as the only actionable control; do not add level-select or exit buttons.

- [ ] **Step 4: Run UI and entry tests**

Run `python -m pytest tests/test_ui.py tests/test_main.py -q`. Expected: menu rendering and start-button event routing pass.

- [ ] **Step 5: Commit main menu**

```bash
git add src/ui.py tests/test_ui.py
git commit -m "feat: polish main menu presentation"
```

### Task 4: Refresh screenshots, docs, and final verification

**Files:**
- Modify: `README.md`, `docs/course-report.md`
- Modify: `docs/assets/runtime-start.png`, `docs/assets/runtime-gameplay.png`, `docs/assets/runtime-result.png`

- [ ] **Step 1: Regenerate screenshots**

Use Pygame with `SDL_VIDEODRIVER=dummy` to save the redesigned menu, a partially revealed large flower or sun level, and a result panel. Inspect all three images before committing.

- [ ] **Step 2: Refresh descriptions**

Update README and the course-report project display text to describe fixed hand-authored/fixed-seed layouts, large flower and sun designs, and the full main menu. Do not claim runtime randomness.

- [ ] **Step 3: Run complete verification**

Run:

```bash
python -m pytest -q
python -m compileall -q main.py src tests
git diff --check
```

Then run the dummy main-loop smoke test and launch `python main.py` for visual inspection.

- [ ] **Step 4: Commit documentation and screenshots**

```bash
git add README.md docs/course-report.md docs/assets/runtime-start.png docs/assets/runtime-gameplay.png docs/assets/runtime-result.png
git commit -m "docs: showcase redesigned course levels"
```

### Task 5: Publish the completed redesign

**Files:**
- Modify: none unless verification identifies a defect

- [ ] **Step 1: Verify Git state**

Run `git status --short --branch` and `git log --oneline -10`; expected: clean worktree with focused commits.

- [ ] **Step 2: Push the detached HEAD safely**

Push to the existing course branch with:

```bash
git push origin HEAD:refs/heads/codex/course-assignment-complete
```

- [ ] **Step 3: Report branch URL and launched game**

Report the GitHub branch URL, test total, screenshot paths, and remind the user that personal report fields remain their responsibility.

## Plan self-review

- All requested changes map to a task: fixed directions, large sun/flower visuals, main menu, tests, screenshots, and GitHub update.
- The generator interface is pure and isolated from runtime factories.
- The plan does not introduce level selection, runtime randomization, scoring, sound, or other out-of-scope functionality.
- `FLOWER_LAYOUT_SEED` and `SUN_LAYOUT_SEED` are used consistently in level tests and frozen constants.
