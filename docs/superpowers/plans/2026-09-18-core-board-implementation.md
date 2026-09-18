# Core Board Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first-round Python/Pygame project skeleton and a fully tested, Pygame-independent Board that implements irregular-region arrow removal rules.

**Architecture:** The repository root is the Python project root. `src.board` owns validated level state and all pure game rules, `src.levels` owns reusable level definitions, and the remaining runtime modules stay intentionally minimal. `MoveResult` carries UI-ready outcomes while Board state changes happen synchronously and independently of future animation.

**Tech Stack:** Python 3.10+, pytest 8, Pygame 2.6 (declared for later UI work; not imported by Board)

---

## File map

- Create `requirements.txt`: pin compatible pytest and Pygame major versions.
- Create `.gitignore`: exclude Python caches and local virtual environments.
- Create `main.py`: load the sample level and print a minimal status line.
- Create `src/__init__.py`: mark the source package.
- Create `src/board.py`: `MoveResult`, input validation, queries, path inspection, clicks, counts, and reset.
- Create `src/levels.py`: immutable-by-convention sample data and a factory that returns a fresh Board.
- Create `src/game.py`: document the future Game-layer boundary.
- Create `src/ui.py`: document the future UI-layer boundary.
- Create `src/animation.py`: document the future animation-layer boundary.
- Create `tests/__init__.py`: mark the test package.
- Create `tests/test_board.py`: Board behavior and validation tests.
- Create `tests/test_levels.py`: verify sample-level creation and state independence.
- Create `assets/images/.gitkeep`, `assets/sounds/.gitkeep`, `assets/fonts/.gitkeep`: preserve empty asset directories.
- Modify `README.md`: add setup, test, and run commands plus current scope.

### Task 1: Create the minimal project skeleton

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `src/game.py`
- Create: `src/ui.py`
- Create: `src/animation.py`
- Create: `tests/__init__.py`
- Create: `assets/images/.gitkeep`
- Create: `assets/sounds/.gitkeep`
- Create: `assets/fonts/.gitkeep`

- [ ] **Step 1: Create dependency declarations**

Create `requirements.txt` with:

```text
pygame>=2.6,<3
pytest>=8,<9
```

Create `.gitignore` with:

```text
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
```

- [ ] **Step 2: Create package and boundary modules**

Create `src/__init__.py` and `tests/__init__.py` as empty files. Create these exact module contents:

```python
# src/game.py
"""Future application state, lives, timing, and page-flow coordination."""
```

```python
# src/ui.py
"""Future Pygame rendering and input translation."""
```

```python
# src/animation.py
"""Future non-blocking visual animation definitions."""
```

Create empty `.gitkeep` files in each asset subdirectory.

- [ ] **Step 3: Install dependencies and verify pytest is available**

Run: `python -m pip install -r requirements.txt`

Run: `python -m pytest --version`

Expected: pytest prints an 8.x version and exits successfully.

- [ ] **Step 4: Commit the skeleton**

```bash
git add .gitignore requirements.txt src tests assets
git commit -m "chore: scaffold Python game project"
```

### Task 2: Validate Board construction and expose safe cell queries

**Files:**
- Create: `src/board.py`
- Create: `tests/test_board.py`

- [ ] **Step 1: Write failing construction and query tests**

Create `tests/test_board.py` with:

```python
from copy import deepcopy

import pytest

from src.board import Board


def make_board(arrow_grid):
    color_grid = [
        [None if cell is None else f"color-{row}-{col}" for col, cell in enumerate(line)]
        for row, line in enumerate(arrow_grid)
    ]
    return Board(arrow_grid, color_grid)


def test_board_copies_input_grids():
    arrows = [["R", "."]]
    colors = [["red", "blue"]]
    original_arrows = deepcopy(arrows)
    original_colors = deepcopy(colors)

    board = Board(arrows, colors)
    board.arrow_grid[0][0] = "."
    board.color_grid[0][0] = "changed"

    assert arrows == original_arrows
    assert colors == original_colors


def test_cell_queries_are_safe():
    board = make_board([[None, "U", "."]])

    assert board.in_bounds(0, 0) is True
    assert board.in_bounds(-1, 0) is False
    assert board.in_bounds(0, 3) is False
    assert board.in_bounds(True, 0) is False
    assert board.get_cell(0, 1) == "U"
    assert board.get_cell(-1, 1) is None
    assert board.is_arrow(0, 1) is True
    assert board.is_arrow(0, 0) is False
    assert board.is_arrow(0, 2) is False


@pytest.mark.parametrize(
    ("arrows", "colors"),
    [
        ([], []),
        ([[]], [[]]),
        ([["R"], ["L", "U"]], [["a"], ["b", "c"]]),
        ([["R"]], [["a"], ["b"]]),
        ([["X"]], [["a"]]),
        ([[None]], [["a"]]),
        ([["R"]], [[None]]),
    ],
)
def test_invalid_level_configuration_raises_value_error(arrows, colors):
    with pytest.raises(ValueError):
        Board(arrows, colors)
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_board.py -v`

Expected: collection fails with `ModuleNotFoundError: No module named 'src.board'`.

- [ ] **Step 3: Implement construction, validation, and queries**

Create `src/board.py` with:

```python
"""Pure board state and rules for the arrow puzzle."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


ARROWS = frozenset({"U", "D", "L", "R"})


@dataclass(frozen=True)
class MoveResult:
    success: bool
    row: int
    col: int
    direction: str | None
    reason: str
    blocker: tuple[int, int] | None = None


class Board:
    """Validated, mutable runtime state for one puzzle level."""

    def __init__(
        self,
        arrow_grid: list[list[str | None]],
        color_grid: list[list[Any | None]],
    ) -> None:
        self._validate_grids(arrow_grid, color_grid)
        self._initial_arrow_grid = deepcopy(arrow_grid)
        self._initial_color_grid = deepcopy(color_grid)
        self.arrow_grid = deepcopy(arrow_grid)
        self.color_grid = deepcopy(color_grid)
        self.rows = len(self.arrow_grid)
        self.cols = len(self.arrow_grid[0])

    @staticmethod
    def _grid_size(grid: object, name: str) -> tuple[int, int]:
        if not isinstance(grid, list) or not grid:
            raise ValueError(f"{name} must be a non-empty list of rows")
        if any(not isinstance(row, list) for row in grid):
            raise ValueError(f"{name} rows must be lists")
        if not grid[0]:
            raise ValueError(f"{name} rows must not be empty")
        width = len(grid[0])
        if any(len(row) != width for row in grid):
            raise ValueError(f"{name} must be rectangular")
        return len(grid), width

    @classmethod
    def _validate_grids(
        cls,
        arrow_grid: object,
        color_grid: object,
    ) -> None:
        arrow_size = cls._grid_size(arrow_grid, "arrow_grid")
        color_size = cls._grid_size(color_grid, "color_grid")
        if arrow_size != color_size:
            raise ValueError("arrow_grid and color_grid must have identical dimensions")

        for row_index, row in enumerate(arrow_grid):
            for col_index, cell in enumerate(row):
                if cell is not None and cell != "." and cell not in ARROWS:
                    raise ValueError("arrow_grid contains an invalid cell value")
                color = color_grid[row_index][col_index]
                if (cell is None) != (color is None):
                    raise ValueError("arrow_grid and color_grid masks must match")

    def in_bounds(self, row: int, col: int) -> bool:
        return (
            type(row) is int
            and type(col) is int
            and 0 <= row < self.rows
            and 0 <= col < self.cols
        )

    def get_cell(self, row: int, col: int) -> str | None:
        if not self.in_bounds(row, col):
            return None
        return self.arrow_grid[row][col]

    def is_arrow(self, row: int, col: int) -> bool:
        return self.get_cell(row, col) in ARROWS
```

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python -m pytest tests/test_board.py -v`

Expected: all construction and query tests pass with no warnings.

- [ ] **Step 5: Commit validated Board construction**

```bash
git add src/board.py tests/test_board.py
git commit -m "feat: validate board data and expose cell queries"
```

### Task 3: Implement irregular-region path inspection

**Files:**
- Modify: `src/board.py`
- Modify: `tests/test_board.py`

- [ ] **Step 1: Append failing path tests**

Append to `tests/test_board.py`:

```python
def test_t01_arrow_can_fly_when_path_has_no_arrow():
    board = make_board([["R", ".", "."]])

    assert board.can_fly(0, 0) is True


def test_t02_arrow_cannot_fly_when_an_arrow_blocks_path():
    board = make_board([["R", "U"]])

    assert board.can_fly(0, 0) is False


def test_t03_cleared_cells_do_not_hide_a_distant_blocker():
    board = make_board([["R", ".", ".", "U"]])

    assert board.can_fly(0, 0) is False


def test_t04_top_edge_arrow_flies_without_negative_index_lookup():
    board = make_board([["U"], ["D"]])

    assert board.can_fly(0, 0) is True


def test_t05_none_ends_the_puzzle_region_immediately():
    board = make_board([["R", None, "U"]])

    assert board.can_fly(0, 0) is True


def test_t06_cleared_cells_can_be_crossed_on_a_clear_path():
    board = make_board([["R", ".", "."]])

    assert board.can_fly(0, 0) is True


@pytest.mark.parametrize("position", [(-1, 0), (0, 3), (0, 0), (0, 1)])
def test_can_fly_returns_false_for_non_arrow_positions(position):
    board = make_board([[None, ".", "R"]])

    assert board.can_fly(*position) is False
```

- [ ] **Step 2: Run path tests and verify RED**

Run: `python -m pytest tests/test_board.py -k "t01 or t02 or t03 or t04 or t05 or t06 or can_fly" -v`

Expected: tests fail with `AttributeError: 'Board' object has no attribute 'can_fly'`.

- [ ] **Step 3: Implement one shared path-inspection rule**

Add below `ARROWS` in `src/board.py`:

```python
DIRECTION_DELTAS = {
    "U": (-1, 0),
    "D": (1, 0),
    "L": (0, -1),
    "R": (0, 1),
}
```

Add these methods to `Board`:

```python
    def _find_blocker(self, row: int, col: int) -> tuple[int, int] | None:
        direction = self.arrow_grid[row][col]
        row_delta, col_delta = DIRECTION_DELTAS[direction]
        next_row = row + row_delta
        next_col = col + col_delta

        while self.in_bounds(next_row, next_col):
            cell = self.arrow_grid[next_row][next_col]
            if cell is None:
                return None
            if cell in ARROWS:
                return next_row, next_col
            next_row += row_delta
            next_col += col_delta
        return None

    def can_fly(self, row: int, col: int) -> bool:
        if not self.is_arrow(row, col):
            return False
        return self._find_blocker(row, col) is None
```

- [ ] **Step 4: Run all Board tests and verify GREEN**

Run: `python -m pytest tests/test_board.py -v`

Expected: all tests pass; in particular the top-edge test does not inspect the final row through a negative index.

- [ ] **Step 5: Commit path rules**

```bash
git add src/board.py tests/test_board.py
git commit -m "feat: implement irregular board flight paths"
```

### Task 4: Return detailed click outcomes and update state immediately

**Files:**
- Modify: `src/board.py`
- Modify: `tests/test_board.py`

- [ ] **Step 1: Append failing click tests**

Append to `tests/test_board.py`:

```python
def test_t01_successful_click_clears_cell_immediately():
    board = make_board([["R", "."]])

    result = board.click(0, 0)

    assert result.success is True
    assert result.row == 0
    assert result.col == 0
    assert result.direction == "R"
    assert result.reason == "clear"
    assert result.blocker is None
    assert board.get_cell(0, 0) == "."


def test_t02_blocked_click_returns_first_blocker_without_mutation():
    board = make_board([["R", ".", "U", "L"]])
    before = deepcopy(board.arrow_grid)

    result = board.click(0, 0)

    assert result.success is False
    assert result.direction == "R"
    assert result.reason == "blocked"
    assert result.blocker == (0, 2)
    assert board.arrow_grid == before


@pytest.mark.parametrize(
    ("position", "reason"),
    [
        ((-1, 0), "out_of_bounds"),
        ((0, 3), "out_of_bounds"),
        ((0, 0), "invalid_cell"),
        ((0, 1), "already_cleared"),
    ],
)
def test_t09_invalid_clicks_return_specific_non_blocked_reasons(position, reason):
    board = make_board([[None, ".", "R"]])

    result = board.click(*position)

    assert result.success is False
    assert result.reason == reason
    assert result.direction is None
    assert result.blocker is None


def test_repeated_click_after_success_is_already_cleared():
    board = make_board([["R"]])

    first = board.click(0, 0)
    second = board.click(0, 0)

    assert first.success is True
    assert second.success is False
    assert second.reason == "already_cleared"
```

- [ ] **Step 2: Run click tests and verify RED**

Run: `python -m pytest tests/test_board.py -k "click or repeated" -v`

Expected: tests fail with `AttributeError: 'Board' object has no attribute 'click'`.

- [ ] **Step 3: Implement detailed click results**

Add this method to `Board` in `src/board.py`:

```python
    def click(self, row: int, col: int) -> MoveResult:
        if not self.in_bounds(row, col):
            return MoveResult(False, row, col, None, "out_of_bounds")

        cell = self.arrow_grid[row][col]
        if cell is None:
            return MoveResult(False, row, col, None, "invalid_cell")
        if cell == ".":
            return MoveResult(False, row, col, None, "already_cleared")

        blocker = self._find_blocker(row, col)
        if blocker is not None:
            return MoveResult(False, row, col, cell, "blocked", blocker)

        self.arrow_grid[row][col] = "."
        return MoveResult(True, row, col, cell, "clear")
```

- [ ] **Step 4: Run all Board tests and verify GREEN**

Run: `python -m pytest tests/test_board.py -v`

Expected: all tests pass, blocked clicks preserve state, and successful clicks mutate state before returning.

- [ ] **Step 5: Commit click behavior**

```bash
git add src/board.py tests/test_board.py
git commit -m "feat: return detailed arrow click results"
```

### Task 5: Add completion, remaining-count, and reset behavior

**Files:**
- Modify: `src/board.py`
- Modify: `tests/test_board.py`

- [ ] **Step 1: Append failing lifecycle tests**

Append to `tests/test_board.py`:

```python
def test_remaining_arrows_counts_only_live_arrows():
    board = make_board([["R", ".", None], ["U", "D", "L"]])

    assert board.remaining_arrows() == 4
    assert board.is_cleared() is False


def test_t07_clearing_last_arrow_completes_board():
    board = make_board([["R"]])

    board.click(0, 0)

    assert board.remaining_arrows() == 0
    assert board.is_cleared() is True


def test_t08_reset_restores_complete_initial_state():
    arrows = [["L", ".", "R"]]
    colors = [["red", "green", "blue"]]
    board = Board(arrows, colors)

    assert board.click(0, 0).success is True
    assert board.click(0, 2).success is True
    board.color_grid[0][0] = "changed"
    board.reset()

    assert board.arrow_grid == arrows
    assert board.color_grid == colors
    assert board.remaining_arrows() == 2
```

- [ ] **Step 2: Run lifecycle tests and verify RED**

Run: `python -m pytest tests/test_board.py -k "remaining or t07 or t08" -v`

Expected: tests fail because `remaining_arrows`, `is_cleared`, and `reset` do not exist.

- [ ] **Step 3: Implement lifecycle methods**

Add these methods to `Board` in `src/board.py`:

```python
    def remaining_arrows(self) -> int:
        return sum(cell in ARROWS for row in self.arrow_grid for cell in row)

    def is_cleared(self) -> bool:
        return self.remaining_arrows() == 0

    def reset(self) -> None:
        self.arrow_grid = deepcopy(self._initial_arrow_grid)
        self.color_grid = deepcopy(self._initial_color_grid)
```

- [ ] **Step 4: Run all Board tests and verify GREEN**

Run: `python -m pytest tests/test_board.py -v`

Expected: every Board test passes with no errors or warnings.

- [ ] **Step 5: Commit Board lifecycle behavior**

```bash
git add src/board.py tests/test_board.py
git commit -m "feat: add board completion and reset state"
```

### Task 6: Add a reusable sample level and minimal entry point

**Files:**
- Create: `src/levels.py`
- Create: `tests/test_levels.py`
- Create: `main.py`

- [ ] **Step 1: Write a failing level-factory test**

Create `tests/test_levels.py` with:

```python
from src.levels import create_sample_board


def test_sample_board_factory_returns_independent_boards():
    first = create_sample_board()
    second = create_sample_board()

    first.arrow_grid[0][2] = "."

    assert second.arrow_grid[0][2] == "U"
    assert first.color_grid == second.color_grid
```

- [ ] **Step 2: Run the factory test and verify RED**

Run: `python -m pytest tests/test_levels.py -v`

Expected: collection fails with `ModuleNotFoundError: No module named 'src.levels'`.

- [ ] **Step 3: Implement sample-level data and factory**

Create `src/levels.py` with:

```python
"""Built-in level definitions for development and tests."""

from src.board import Board


SAMPLE_ARROW_GRID = [
    [None, None, "U", None, None],
    [None, "L", "D", "R", None],
    ["R", "U", "L", "D", "L"],
]

SAMPLE_COLOR_GRID = [
    [None, None, "leaf_light", None, None],
    [None, "leaf", "leaf", "leaf", None],
    ["grass", "trunk", "trunk", "grass", "flower"],
]


def create_sample_board() -> Board:
    """Return a fresh Board for the built-in sample level."""
    return Board(SAMPLE_ARROW_GRID, SAMPLE_COLOR_GRID)
```

- [ ] **Step 4: Add the minimal executable entry point**

Create `main.py` with:

```python
"""Minimal development entry point for the first project iteration."""

from src.levels import create_sample_board


def main() -> None:
    board = create_sample_board()
    print(f"一箭又一箭：示例关卡已加载，剩余箭头 {board.remaining_arrows()} 个")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Verify the level factory and entry point**

Run: `python -m pytest tests/test_levels.py -v`

Expected: one test passes.

Run: `python main.py`

Expected: `一箭又一箭：示例关卡已加载，剩余箭头 9 个`

- [ ] **Step 6: Commit the sample level and entry point**

```bash
git add src/levels.py tests/test_levels.py main.py
git commit -m "feat: add sample level and development entry point"
```

### Task 7: Document, verify, and finish the first iteration

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace README with setup and scope documentation**

Replace `README.md` with:

````markdown
# Arrow-Go-Poof（一箭又一箭）

基于 Python 与 Pygame 的桌面箭头消除解谜游戏。

当前第一轮实现包含项目骨架、示例关卡数据，以及不依赖 Pygame 的核心 `Board` 规则。正式 UI、动画、音效、生命值、计时、Combo 和星级将在后续迭代实现。

## 环境

- Python 3.10+

```bash
python -m pip install -r requirements.txt
```

## 测试

```bash
python -m pytest -v
```

## 运行最小入口

```bash
python main.py
```
````

- [ ] **Step 2: Run the complete automated test suite**

Run: `python -m pytest -v`

Expected: all tests in `tests/test_board.py` and `tests/test_levels.py` pass with no warnings.

- [ ] **Step 3: Check source compilation and working-tree scope**

Run: `python -m compileall -q main.py src tests`

Expected: command exits with status 0 and prints no errors.

Run: `git status --short`

Expected: only `README.md` is modified; Python cache directories are ignored.

- [ ] **Step 4: Commit documentation and ignore rules**

```bash
git add README.md
git commit -m "docs: document first-round project usage"
```

- [ ] **Step 5: Perform final verification from a clean state**

Run: `python -m pytest -q`

Run: `python main.py`

Run: `git status --short --branch`

Expected: all tests pass, the sample level reports 9 arrows, and the branch has no uncommitted project files.
