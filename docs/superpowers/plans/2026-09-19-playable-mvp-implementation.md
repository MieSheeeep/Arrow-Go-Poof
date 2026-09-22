# 可游玩 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将第一阶段的纯 `Board` 规则扩展为一个 1200×800、可直接游玩的 Pygame 树形箭头解谜 MVP。

**Architecture:** 保持 `Board` 为纯规则层；新增 `Game` 协调生命值、胜负状态和动画；新增纯 Python 动画模型；由 `UI` 负责 Pygame 绘制和鼠标坐标转换；`main.py` 只负责初始化和主循环。逻辑点击在创建动画前立即更新，动画不修改棋盘状态。

**Tech Stack:** Python 3.10+, Pygame 2.6+, pytest 8+

---

## 执行前置条件

实现必须在隔离工作区进行，不得直接在 `main` 分支实现。执行本计划时先使用 `superpowers:using-git-worktrees` 创建或确认工作区：

```text
工作区：.worktrees/playable-mvp
分支：feature/playable-mvp
基线：a71bc3a
```

当前仓库的 `main` 已包含第二阶段设计文档提交 `a71bc3a`。如果 `feature/playable-mvp` 不存在，按用户已经选择的功能开发流程从当前 `main` 创建；不要重置、覆盖或删除现有 `core-board` worktree。

## 文件地图

| 文件 | 责任 |
| --- | --- |
| `src/levels.py` | 保留小测试关卡，新增不可变树形演示关卡和工厂 |
| `tests/test_levels.py` | 验证树形关卡形状、掩码和工厂隔离 |
| `src/animation.py` | 纯 Python 的飞出/撞击动画时间模型 |
| `tests/test_animation.py` | 验证动画方向、阶段、颜色和完成状态 |
| `src/game.py` | `GameState`、生命值、点击协调、动画生命周期和重置 |
| `tests/test_game.py` | 验证 Game 的完整状态转换，不启动窗口 |
| `src/ui.py` | 固定窗口布局、像素风绘制、HUD、结果面板和坐标映射 |
| `tests/test_ui.py` | 验证布局坐标转换和格子矩形，不要求显示器 |
| `main.py` | Pygame 初始化、事件循环、绘制和退出 |
| `README.md` | 更新安装、运行、测试和 MVP 功能说明 |

## 约定的接口

以下接口在任务之间保持一致，后续任务不得改名：

```python
# src/animation.py
class FlyOutAnimation:
    def __init__(self, row: int, col: int, direction: str,
                 duration: float = 0.30, distance: float = 2.0): ...
    def update(self, delta_time: float) -> None: ...
    @property
    def is_finished(self) -> bool: ...
    @property
    def offset_cells(self) -> tuple[float, float]: ...
    @property
    def color_state(self) -> str: ...

class CollisionAnimation:
    def __init__(self, row: int, col: int, blocker: tuple[int, int],
                 direction: str, approach_duration: float = 0.12,
                 impact_duration: float = 0.08,
                 retreat_duration: float = 0.16): ...
    def update(self, delta_time: float) -> None: ...
    @property
    def phase(self) -> str: ...       # approach / impact / retreat / done
    @property
    def is_finished(self) -> bool: ...
    @property
    def offset_cells(self) -> tuple[float, float]: ...
    @property
    def color_state(self) -> str: ... # normal before impact, error at/after impact

# src/game.py
class GameState(Enum):
    PLAYING = "playing"
    CLEARED = "cleared"
    FAILED = "failed"
    PAUSED = "paused"

class Game:
    def __init__(self, board_factory: Callable[[], Board], max_lives: int = 3): ...
    def click(self, row: int, col: int) -> MoveResult | None: ...
    def update(self, delta_time: float) -> None: ...
    def restart(self) -> None: ...
```

终止状态下 `Game.click()` 返回 `None`，不调用 `Board.click()`；`Board` 的五种既有 `reason` 字符串不扩展。阻挡动画完成时，`Game` 才把起点加入 `error_cells`，因此撞击之前不会提前变红。

---

### Task 1: 添加树形演示关卡

**Files:**
- Modify: `src/levels.py`
- Test: `tests/test_levels.py`

- [ ] **Step 1: 先写树形关卡失败测试**

在 `tests/test_levels.py` 增加以下测试。它先要求新常量和工厂不存在，因此应先失败：

```python
from src.levels import (
    SAMPLE_ARROW_GRID,
    SAMPLE_COLOR_GRID,
    TREE_ARROW_GRID,
    TREE_COLOR_GRID,
    create_sample_board,
    create_tree_board,
)


def test_tree_level_is_a_12_by_13_irregular_grid():
    assert len(TREE_ARROW_GRID) == 12
    assert len(TREE_COLOR_GRID) == 12
    assert all(len(row) == 13 for row in TREE_ARROW_GRID)
    assert all(len(row) == 13 for row in TREE_COLOR_GRID)
    assert TREE_ARROW_GRID[0][0] is None
    assert TREE_ARROW_GRID[5][0] in {"L", "R", "U", "D"}
    assert TREE_COLOR_GRID[8][6] == "trunk"


def test_tree_level_arrow_and_color_masks_match():
    for arrow_row, color_row in zip(TREE_ARROW_GRID, TREE_COLOR_GRID):
        assert [cell is None for cell in arrow_row] == [cell is None for cell in color_row]


def test_tree_board_factory_returns_independent_boards():
    first = create_tree_board()
    second = create_tree_board()

    first.arrow_grid[0][6] = "."
    first.color_grid[8][6] = "changed"

    assert second.arrow_grid[0][6] == "U"
    assert second.color_grid[8][6] == "trunk"
    assert first.rows == second.rows == 12
    assert first.cols == second.cols == 13
```

- [ ] **Step 2: 运行新增测试确认 RED**

运行：

```bash
python -m pytest tests/test_levels.py -q
```

预期：失败，提示 `ImportError`，因为 `TREE_ARROW_GRID`、`TREE_COLOR_GRID` 和 `create_tree_board` 尚未定义；已有 sample 测试仍应通过。

- [ ] **Step 3: 写入不可变树形关卡数据**

在 `src/levels.py` 保留现有 sample 常量和工厂，并追加以下 12×13 数据。`None` 表示背景外区域；颜色掩码必须与箭头掩码一致。箭头方向安排为先清顶部和外缘、再清树冠内部、最后清树干与树根，保证演示关卡可以顺序游玩。

```python
TREE_ARROW_GRID = (
    (None, None, None, None, None, None, "U", None, None, None, None, None, None),
    (None, None, None, None, "U", "U", "U", "U", "U", None, None, None, None),
    (None, None, None, "U", "U", "U", "U", "U", "U", "U", "U", None, None),
    (None, None, "L", "U", "U", "U", "U", "U", "U", "U", "U", "R", None),
    (None, "L", "U", "U", "U", "U", "U", "U", "U", "U", "U", "R", None),
    ("L", "U", "U", "U", "U", "U", "U", "U", "U", "U", "U", "U", "R"),
    (None, "L", "U", "U", "U", "U", "U", "U", "U", "U", "U", "R", None),
    (None, None, "L", "U", "U", "U", "U", "U", "U", "U", "R", None, None),
    (None, None, None, None, "D", "D", "D", "D", "D", None, None, None, None),
    (None, None, None, None, "D", "D", "D", "D", "D", None, None, None, None),
    (None, None, None, None, "D", "D", "D", "D", "D", None, None, None, None),
    (None, None, None, "L", "D", "D", "D", "D", "D", "R", None, None, None),
)

TREE_COLOR_GRID = (
    (None, None, None, None, None, None, "leaf_light", None, None, None, None, None, None),
    (None, None, None, None, "leaf_light", "leaf_light", "leaf_light", "leaf_light", "leaf_light", None, None, None, None),
    (None, None, None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None, None),
    (None, None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None),
    (None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None),
    ("leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf"),
    (None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None),
    (None, None, "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", "leaf", None, None),
    (None, None, None, None, "trunk", "trunk", "trunk", "trunk", "trunk", None, None, None, None),
    (None, None, None, None, "trunk", "trunk", "trunk", "trunk", "trunk", None, None, None, None),
    (None, None, None, None, "trunk", "trunk", "trunk", "trunk", "trunk", None, None, None, None),
    (None, None, None, "grass", "grass", "grass", "grass", "grass", "grass", "grass", None, None, None),
)


def create_tree_board() -> Board:
    """Return a fresh Board for the tree-shaped demonstration level."""
    arrow_grid = [list(row) for row in TREE_ARROW_GRID]
    color_grid = [list(row) for row in TREE_COLOR_GRID]
    return Board(arrow_grid, color_grid)
```

- [ ] **Step 4: 运行关卡测试确认 GREEN**

运行：

```bash
python -m pytest tests/test_levels.py -q
```

预期：所有 level 测试通过。

- [ ] **Step 5: 提交任务**

```bash
git add src/levels.py tests/test_levels.py
git commit -m "feat: add tree-shaped demo level"
```

### Task 2: 实现纯 Python 动画时间模型

**Files:**
- Modify: `src/animation.py`
- Create: `tests/test_animation.py`

- [ ] **Step 1: 写飞出和撞击动画的失败测试**

创建 `tests/test_animation.py`：

```python
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
```

- [ ] **Step 2: 运行测试确认 RED**

运行：

```bash
python -m pytest tests/test_animation.py -q
```

预期：失败，提示 `ImportError` 或缺少动画属性。

- [ ] **Step 3: 实现动画基类和两个动画类型**

在 `src/animation.py` 实现以下确定行为：

```python
from __future__ import annotations


_DIRECTION_DELTAS = {
    "U": (-1.0, 0.0),
    "D": (1.0, 0.0),
    "L": (0.0, -1.0),
    "R": (0.0, 1.0),
}


class _TimedAnimation:
    def __init__(self, duration: float) -> None:
        if duration <= 0:
            raise ValueError("duration must be positive")
        self.duration = duration
        self.elapsed = 0.0

    @property
    def is_finished(self) -> bool:
        return self.elapsed >= self.duration

    @property
    def progress(self) -> float:
        return min(self.elapsed / self.duration, 1.0)

    def update(self, delta_time: float) -> None:
        if delta_time < 0:
            raise ValueError("delta_time must be non-negative")
        self.elapsed = min(self.elapsed + delta_time, self.duration)


def _direction_delta(direction: str) -> tuple[float, float]:
    try:
        return _DIRECTION_DELTAS[direction]
    except KeyError as exc:
        raise ValueError(f"unknown direction: {direction!r}") from exc


class FlyOutAnimation(_TimedAnimation):
    def __init__(self, row: int, col: int, direction: str,
                 duration: float = 0.30, distance: float = 2.0) -> None:
        super().__init__(duration)
        if distance <= 0:
            raise ValueError("distance must be positive")
        _direction_delta(direction)
        self.row = row
        self.col = col
        self.direction = direction
        self.distance = distance

    @property
    def offset_cells(self) -> tuple[float, float]:
        row_delta, col_delta = _direction_delta(self.direction)
        eased = 1.0 - (1.0 - self.progress) ** 2
        return row_delta * self.distance * eased, col_delta * self.distance * eased

    @property
    def color_state(self) -> str:
        return "normal"


class CollisionAnimation(_TimedAnimation):
    def __init__(self, row: int, col: int, blocker: tuple[int, int],
                 direction: str, approach_duration: float = 0.12,
                 impact_duration: float = 0.08,
                 retreat_duration: float = 0.16) -> None:
        for duration in (approach_duration, impact_duration, retreat_duration):
            if duration <= 0:
                raise ValueError("collision phase durations must be positive")
        _direction_delta(direction)
        self.row = row
        self.col = col
        self.blocker = blocker
        self.direction = direction
        self.approach_duration = approach_duration
        self.impact_duration = impact_duration
        self.retreat_duration = retreat_duration
        super().__init__(approach_duration + impact_duration + retreat_duration)

    @property
    def phase(self) -> str:
        if self.elapsed < self.approach_duration:
            return "approach"
        if self.elapsed < self.approach_duration + self.impact_duration:
            return "impact"
        if not self.is_finished:
            return "retreat"
        return "done"

    @property
    def color_state(self) -> str:
        return "normal" if self.phase == "approach" else "error"

    @property
    def offset_cells(self) -> tuple[float, float]:
        target = (self.blocker[0] - self.row, self.blocker[1] - self.col)
        if self.phase == "approach":
            ratio = self.elapsed / self.approach_duration
            return target[0] * ratio, target[1] * ratio
        if self.phase == "impact":
            return float(target[0]), float(target[1])
        if self.phase == "retreat":
            phase_elapsed = self.elapsed - self.approach_duration - self.impact_duration
            ratio = 1.0 - phase_elapsed / self.retreat_duration
            return target[0] * ratio, target[1] * ratio
        return 0.0, 0.0
```

- [ ] **Step 4: 运行动画测试和编译检查**

运行：

```bash
python -m pytest tests/test_animation.py -q
python -m compileall -q src/animation.py
```

预期：动画测试全部通过，编译无输出且退出码为 0。

- [ ] **Step 5: 提交任务**

```bash
git add src/animation.py tests/test_animation.py
git commit -m "feat: add non-blocking puzzle animations"
```

### Task 3: 实现 Game 状态协调器

**Files:**
- Modify: `src/game.py`
- Create: `tests/test_game.py`

- [ ] **Step 1: 写 Game 状态转换失败测试**

创建 `tests/test_game.py`：

```python
from src.animation import CollisionAnimation, FlyOutAnimation
from src.board import Board
from src.game import Game, GameState


def board_factory(arrows):
    def create():
        colors = [
            [None if cell is None else f"cell-{row}-{col}" for col, cell in enumerate(line)]
            for row, line in enumerate(arrows)
        ]
        return Board([list(line) for line in arrows], colors)

    return create


def test_game_starts_in_playing_with_three_lives():
    game = Game(board_factory([["R"]]))

    assert game.state is GameState.PLAYING
    assert game.lives == 3
    assert game.mistakes == 0
    assert game.board.remaining_arrows() == 1
    assert game.animations == []
    assert game.error_cells == set()


def test_successful_click_clears_board_and_creates_fly_out_animation():
    game = Game(board_factory([["R"]]))

    result = game.click(0, 0)

    assert result is not None and result.success is True
    assert game.board.get_cell(0, 0) == "."
    assert game.animations and isinstance(game.animations[0], FlyOutAnimation)
    assert game.state is GameState.CLEARED
    assert game.lives == 3


def test_blocked_click_deducts_life_and_creates_collision_animation():
    game = Game(board_factory([["R", "U"]]))

    result = game.click(0, 0)

    assert result is not None and result.reason == "blocked"
    assert result.blocker == (0, 1)
    assert game.lives == 2
    assert game.mistakes == 1
    assert game.state is GameState.PLAYING
    assert isinstance(game.animations[0], CollisionAnimation)
    assert game.error_cells == set()


def test_collision_error_cell_is_persisted_only_after_animation_finishes():
    game = Game(board_factory([["R", "U"]]))
    game.click(0, 0)

    game.update(0.12)
    assert game.error_cells == set()
    assert game.animations[0].color_state == "error"

    game.update(0.24)
    assert game.animations == []
    assert game.error_cells == {(0, 0)}


def test_invalid_click_does_not_change_game_state():
    game = Game(board_factory([[None, ".", "R"]]))

    for position in [(-1, 0), (0, 0), (0, 1)]:
        before = (game.lives, game.mistakes, len(game.animations))
        result = game.click(*position)
        assert result is not None and result.success is False
        assert (game.lives, game.mistakes, len(game.animations)) == before


def test_three_blocked_clicks_enter_failed_and_stop_future_clicks():
    game = Game(board_factory([["R", "U"]]))

    for _ in range(3):
        game.click(0, 0)

    assert game.lives == 0
    assert game.mistakes == 3
    assert game.state is GameState.FAILED
    animation_count = len(game.animations)
    assert game.click(0, 0) is None
    assert len(game.animations) == animation_count


def test_restart_restores_board_and_runtime_state():
    game = Game(board_factory([["R"]]))
    game.click(0, 0)
    game.update(1.0)
    game.restart()

    assert game.state is GameState.PLAYING
    assert game.lives == 3
    assert game.mistakes == 0
    assert game.board.get_cell(0, 0) == "R"
    assert game.animations == []
    assert game.error_cells == set()
```

- [ ] **Step 2: 运行 Game 测试确认 RED**

运行：

```bash
python -m pytest tests/test_game.py -q
```

预期：失败，提示 `Game`、`GameState` 或方法未实现。

- [ ] **Step 3: 实现 Game 协调器**

在 `src/game.py` 实现以下核心逻辑：

```python
from __future__ import annotations

from enum import Enum
from typing import Callable

from src.animation import CollisionAnimation, FlyOutAnimation
from src.board import Board, MoveResult


class GameState(Enum):
    PLAYING = "playing"
    CLEARED = "cleared"
    FAILED = "failed"
    PAUSED = "paused"


class Game:
    def __init__(self, board_factory: Callable[[], Board], max_lives: int = 3) -> None:
        if max_lives <= 0:
            raise ValueError("max_lives must be positive")
        self.board_factory = board_factory
        self.max_lives = max_lives
        self.restart()

    def restart(self) -> None:
        self.board = self.board_factory()
        self.lives = self.max_lives
        self.mistakes = 0
        self.state = GameState.PLAYING
        self.animations = []
        self.error_cells = set()

    def click(self, row: int, col: int) -> MoveResult | None:
        if self.state is not GameState.PLAYING:
            return None

        result = self.board.click(row, col)
        if result.reason == "clear":
            self.animations.append(FlyOutAnimation(row, col, result.direction))
            if self.board.is_cleared():
                self.state = GameState.CLEARED
        elif result.reason == "blocked":
            self.lives -= 1
            self.mistakes += 1
            self.animations.append(
                CollisionAnimation(row, col, result.blocker, result.direction)
            )
            if self.lives == 0:
                self.state = GameState.FAILED
        return result

    def update(self, delta_time: float) -> None:
        remaining = []
        for animation in self.animations:
            animation.update(delta_time)
            if animation.is_finished:
                if isinstance(animation, CollisionAnimation):
                    self.error_cells.add((animation.row, animation.col))
            else:
                remaining.append(animation)
        self.animations = remaining
```

`result.direction` 和 `result.blocker` 在 `reason` 已经判定后不为空；若静态类型检查提示可选值，使用局部断言或显式分支，不改变 `Board.MoveResult` 契约。不要在 `Game` 中复制路径判定。

- [ ] **Step 4: 运行 Game、Board 和关卡全量测试**

运行：

```bash
python -m pytest tests/test_board.py tests/test_levels.py tests/test_animation.py tests/test_game.py -q
```

预期：所有测试通过，且现有 Board 行为没有变化。

- [ ] **Step 5: 提交任务**

```bash
git add src/game.py tests/test_game.py
git commit -m "feat: add game state coordinator"
```

### Task 4: 实现固定布局和 Pygame UI

**Files:**
- Modify: `src/ui.py`
- Create: `tests/test_ui.py`

- [ ] **Step 1: 写不启动显示器的布局测试**

创建 `tests/test_ui.py`：

```python
import pygame

from src.ui import GridLayout, WINDOW_SIZE


def test_window_and_grid_layout_match_mvp_design():
    assert WINDOW_SIZE == (1200, 800)
    layout = GridLayout(origin=(260, 130), cell_size=48)

    assert layout.cell_at((260, 130), rows=12, cols=13) == (0, 0)
    assert layout.cell_at((307, 177), rows=12, cols=13) == (0, 0)
    assert layout.cell_at((308, 178), rows=12, cols=13) == (1, 1)
    assert layout.cell_at((259, 130), rows=12, cols=13) is None
    assert layout.cell_at((260 + 13 * 48, 130), rows=12, cols=13) is None


def test_grid_layout_returns_pixel_rect_for_cell():
    layout = GridLayout(origin=(260, 130), cell_size=48)
    rect = layout.cell_rect(2, 3)

    assert isinstance(rect, pygame.Rect)
    assert rect.topleft == (404, 226)
    assert rect.size == (48, 48)
```

- [ ] **Step 2: 运行布局测试确认 RED**

运行：

```bash
python -m pytest tests/test_ui.py -q
```

预期：失败，提示 `GridLayout` 或 `WINDOW_SIZE` 未定义。

- [ ] **Step 3: 实现布局、背景、棋盘和 HUD 绘制**

在 `src/ui.py` 添加以下固定接口：

```python
from __future__ import annotations

import pygame

from src.animation import CollisionAnimation, FlyOutAnimation
from src.game import Game, GameState


WINDOW_SIZE = (1200, 800)
BACKGROUND = (126, 190, 232)
HUD_COLOR = (39, 77, 119)
ARROW_TILE = (235, 237, 235)
ARROW_COLOR = (86, 102, 126)
ERROR_TILE = (238, 112, 112)
ERROR_ARROW = (128, 38, 38)
HOVER_COLOR = (102, 213, 255)


class GridLayout:
    def __init__(self, origin: tuple[int, int], cell_size: int) -> None:
        if cell_size <= 0:
            raise ValueError("cell_size must be positive")
        self.origin = origin
        self.cell_size = cell_size

    def cell_at(self, position: tuple[int, int], rows: int, cols: int):
        x, y = position
        origin_x, origin_y = self.origin
        local_x = x - origin_x
        local_y = y - origin_y
        if local_x < 0 or local_y < 0:
            return None
        col = local_x // self.cell_size
        row = local_y // self.cell_size
        if row >= rows or col >= cols:
            return None
        return row, col

    def cell_rect(self, row: int, col: int) -> pygame.Rect:
        x = self.origin[0] + col * self.cell_size
        y = self.origin[1] + row * self.cell_size
        return pygame.Rect(x, y, self.cell_size, self.cell_size)


class UI:
    def __init__(self, screen: pygame.Surface, game: Game) -> None:
        self.screen = screen
        self.game = game
        self.layout = GridLayout(origin=(260, 130), cell_size=48)
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)

    def cell_at(self, position: tuple[int, int]):
        return self.layout.cell_at(position, self.game.board.rows, self.game.board.cols)

    def restart_rect(self) -> pygame.Rect:
        return pygame.Rect(490, 505, 220, 52)

    def draw(self) -> None:
        self._draw_background()
        self._draw_board()
        self._draw_animations()
        self._draw_hud()
        if self.game.state in {GameState.CLEARED, GameState.FAILED}:
            self._draw_result_panel()

    def _draw_background(self) -> None:
        self.screen.fill(BACKGROUND)
        pygame.draw.rect(self.screen, (102, 164, 199), (0, 350, 1200, 450))
        pygame.draw.polygon(self.screen, (78, 142, 177), [(0, 410), (190, 270), (390, 410)])
        pygame.draw.polygon(self.screen, (92, 155, 186), [(760, 420), (970, 250), (1200, 420)])
        pygame.draw.rect(self.screen, (104, 170, 84), (0, 560, 1200, 240))
        for x, y in [(90, 95), (1030, 110), (180, 250), (950, 260)]:
            pygame.draw.rect(self.screen, (245, 247, 238), (x, y, 92, 18))
            pygame.draw.rect(self.screen, (245, 247, 238), (x + 24, y - 14, 58, 18))

    def _draw_board(self) -> None:
        hover_cell = self.cell_at(pygame.mouse.get_pos())
        active_cells = {(animation.row, animation.col) for animation in self.game.animations}
        for row in range(self.game.board.rows):
            for col in range(self.game.board.cols):
                color_name = self.game.board.color_grid[row][col]
                if color_name is None:
                    continue
                rect = self.layout.cell_rect(row, col)
                cell = self.game.board.arrow_grid[row][col]
                if (row, col) in self.game.error_cells:
                    fill = ERROR_TILE
                elif color_name in {"trunk"}:
                    fill = (142, 91, 55)
                elif color_name in {"grass"}:
                    fill = (86, 157, 73)
                else:
                    fill = (105, 181, 78)
                if cell in {"U", "D", "L", "R"} and (row, col) not in active_cells:
                    fill = ERROR_TILE if (row, col) in self.game.error_cells else ARROW_TILE
                pygame.draw.rect(self.screen, fill, rect)
                pygame.draw.rect(self.screen, (67, 93, 112), rect, 1)
                if cell in {"U", "D", "L", "R"} and (row, col) not in active_cells:
                    self._draw_arrow(rect, cell, ERROR_ARROW if (row, col) in self.game.error_cells else ARROW_COLOR)
                if hover_cell == (row, col):
                    pygame.draw.rect(self.screen, HOVER_COLOR, rect, 2)

    def _draw_animations(self) -> None:
        for animation in self.game.animations:
            rect = self.layout.cell_rect(animation.row, animation.col)
            offset_row, offset_col = animation.offset_cells
            rect = rect.move(round(offset_col * self.layout.cell_size), round(offset_row * self.layout.cell_size))
            color = ERROR_ARROW if animation.color_state == "error" else ARROW_COLOR
            pygame.draw.rect(self.screen, ERROR_TILE if animation.color_state == "error" else ARROW_TILE, rect)
            self._draw_arrow(rect, animation.direction, color)

    def _draw_arrow(self, rect: pygame.Rect, direction: str, color: tuple[int, int, int]) -> None:
        center = rect.center
        arm = self.layout.cell_size // 3
        points = {
            "U": [(center[0], center[1] - arm), (center[0] - arm // 2, center[1]), (center[0] - 5, center[1]), (center[0] - 5, center[1] + arm), (center[0] + 5, center[1] + arm), (center[0] + 5, center[1]), (center[0] + arm // 2, center[1])],
            "D": [(center[0], center[1] + arm), (center[0] - arm // 2, center[1]), (center[0] - 5, center[1]), (center[0] - 5, center[1] - arm), (center[0] + 5, center[1] - arm), (center[0] + 5, center[1]), (center[0] + arm // 2, center[1])],
            "L": [(center[0] - arm, center[1]), (center[0], center[1] - arm // 2), (center[0], center[1] - 5), (center[0] + arm, center[1] - 5), (center[0] + arm, center[1] + 5), (center[0], center[1] + 5), (center[0], center[1] + arm // 2)],
            "R": [(center[0] + arm, center[1]), (center[0], center[1] - arm // 2), (center[0], center[1] - 5), (center[0] - arm, center[1] - 5), (center[0] - arm, center[1] + 5), (center[0], center[1] + 5), (center[0], center[1] + arm // 2)],
        }
        pygame.draw.polygon(self.screen, color, points[direction])

    def _draw_hud(self) -> None:
        pygame.draw.rect(self.screen, HUD_COLOR, (220, 22, 760, 62), border_radius=12)
        text = f"LEVEL 01    ♥ {self.game.lives}    ✕ {self.game.mistakes}    ARROWS {self.game.board.remaining_arrows()}"
        surface = self.font.render(text, True, (250, 230, 133))
        self.screen.blit(surface, (250, 42))

    def _draw_result_panel(self) -> None:
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((12, 28, 54, 120))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(365, 230, 470, 360)
        pygame.draw.rect(self.screen, (39, 77, 119), panel, border_radius=16)
        title = "LEVEL CLEAR" if self.game.state is GameState.CLEARED else "TRY AGAIN"
        title_surface = self.font.render(title, True, (250, 230, 133))
        self.screen.blit(title_surface, title_surface.get_rect(center=(600, 310)))
        stats = self.small_font.render(f"Mistakes: {self.game.mistakes}", True, (240, 245, 250))
        self.screen.blit(stats, stats.get_rect(center=(600, 370)))
        button = self.restart_rect()
        pygame.draw.rect(self.screen, (105, 181, 78), button, border_radius=8)
        label = self.small_font.render("RESTART", True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=button.center))
```

实现时若当前 Pygame 版本不支持 `border_radius`，将对应调用改为普通 `pygame.draw.rect`，不改变布局和测试接口。棋盘绘制必须跳过正在播放动画的原始箭头，避免出现一支箭头的重影；动画结束后再由 Board/error marker 绘制最终状态。悬停描边只改变视觉，不改变点击判定。

- [ ] **Step 4: 运行 UI 测试和编译检查**

运行：

```bash
python -m pytest tests/test_ui.py -q
python -m compileall -q src/ui.py
```

预期：布局测试通过，编译无错误。

- [ ] **Step 5: 提交任务**

```bash
git add src/ui.py tests/test_ui.py
git commit -m "feat: add pixel-inspired pygame UI"
```

### Task 5: 接入 Pygame 主循环和重新开始交互

**Files:**
- Modify: `main.py`
- Modify: `README.md`

- [ ] **Step 1: 先写入口导入和运行契约检查**

在 `tests/test_levels.py` 末尾增加一个轻量测试，确保主入口仍导入新工厂而不是旧命令行输出：

```python
def test_tree_factory_is_available_for_runtime_entry_point():
    board = create_tree_board()
    assert board.rows == 12
    assert board.cols == 13
    assert board.remaining_arrows() > 0
```

运行：

```bash
python -m pytest tests/test_levels.py -q
```

预期：通过。该测试确保入口所需工厂存在，窗口主循环留给编译和手动 smoke test，避免 CI 因无显示器挂起。

- [ ] **Step 2: 将 `main.py` 替换为固定窗口主循环**

使用以下主循环结构：

```python
"""Runnable Pygame entry point for the playable MVP."""
import pygame

from src.game import Game, GameState
from src.levels import create_tree_board
from src.ui import UI, WINDOW_SIZE


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("一箭又一箭")
    game = Game(create_tree_board)
    ui = UI(screen, game)
    clock = pygame.time.Clock()
    running = True

    while running:
        delta_time = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.state in {GameState.CLEARED, GameState.FAILED}:
                    if ui.restart_rect().collidepoint(event.pos):
                        game.restart()
                else:
                    cell = ui.cell_at(event.pos)
                    if cell is not None:
                        game.click(*cell)

        game.update(delta_time)
        ui.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```

不要在 `main.py` 中复制棋盘判定、生命值或绘制代码；它只连接 Pygame 事件、`Game` 和 `UI`。

- [ ] **Step 3: 更新 README 使用说明**

将 README 的当前阶段说明更新为：

```markdown
当前实现包含可直接游玩的 Pygame MVP：树形示例关卡、鼠标点击、三点生命值、成功飞出动画、阻挡撞击回退反馈、通关/失败面板和重新开始。计时、星级、Combo、音效和多关卡选择仍属于后续迭代。
```

补充运行说明：

```markdown
## 运行游戏

```bash
python main.py
```

窗口固定为 1200×800。关闭窗口退出；通关或失败后点击结果面板中的 `RESTART` 重新开始。
```

- [ ] **Step 4: 执行静态验证**

运行：

```bash
python -m compileall -q main.py src tests
python -m pytest -q
```

预期：编译退出码为 0，全部测试通过。

- [ ] **Step 5: 提交入口和文档**

```bash
git add main.py README.md tests/test_levels.py
git commit -m "feat: launch playable pygame MVP"
```

### Task 6: 运行验收、修复集成问题并完成交付

**Files:**
- Modify: 仅在验收发现问题时修改对应实现文件和测试文件

- [ ] **Step 1: 运行完整自动化验证**

运行：

```bash
python -m pytest -v
python -m compileall -q main.py src tests
git diff --check
```

预期：所有测试通过、编译无输出、`git diff --check` 无空白错误。

- [ ] **Step 2: 进行手动窗口验收**

运行：

```bash
python main.py
```

依次检查：

1. 窗口尺寸为 1200×800，启动后直接显示树形关卡；
2. 点击无遮挡箭头时，箭头立即从棋盘逻辑状态消失并向外飞出；
3. 点击被阻挡箭头时，生命值立即减少，箭头先撞向 blocker，撞击时变红，回退后仍为红色；
4. 动画播放期间点击其他箭头仍然有效；
5. 连续三次阻挡后显示失败面板；
6. 按 `RESTART` 后棋盘、生命值、失误次数、动画和红色标记全部恢复；
7. 清除全部箭头后显示通关面板；
8. 点击窗口关闭按钮后程序正常退出。

- [ ] **Step 3: 若验收失败，先补回归测试再修复**

任何发现的行为问题都按以下顺序处理：

```bash
python -m pytest tests/<对应测试文件>.py -q
git diff --check
```

先在对应测试文件加入最小失败用例，再修改实现；修复后重新运行单测和完整测试，不通过时不得进入交付。

- [ ] **Step 4: 检查工作区和提交范围**

运行：

```bash
git status --short --branch
git log --oneline -8
```

预期：工作区干净，提交只包含本计划涉及的关卡、动画、Game、UI、入口、测试和 README 文件。

- [ ] **Step 5: 提交最终修复并转入分支收尾**

如有最后修复：

```bash
git add src tests main.py README.md
git commit -m "fix: complete playable MVP verification"
```

所有任务完成后，必须使用 `superpowers:finishing-a-development-branch`，向用户提供合并、推送创建 PR、保留分支或放弃分支的选择；在用户选择前不要合并到 `main`。

## 计划自检

- 设计覆盖：窗口、树形关卡、HUD、坐标映射、成功飞出、阻挡撞击/变红/回退、生命值、通关、失败、重开、并行动画和测试均有对应任务。
- 范围控制：没有加入菜单、计时、星级、Combo、音效、复杂粒子或真实图片资源。
- TDD：每个新增核心模块先写失败测试，再实现最小行为，再执行聚焦测试和全量测试。
- 类型一致性：`GameState`、`Game.click()`、动画属性和 `GridLayout` 接口在任务间保持统一。
- 占位检查：计划不包含未定义的占位步骤或模糊的“自行处理”要求；每个代码步骤都给出目标接口、代码结构和验证命令。
