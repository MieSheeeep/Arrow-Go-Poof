# Course Assignment Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有单关卡 MVP 补齐为符合课程作业硬性要求的 Python/Pygame “一箭又一箭”基础版：开始界面、至少三关可通关流程、完整结果反馈、测试材料和 README 展示材料。

**Architecture:** 保持 `Board` 负责单关卡规则；`Game` 扩展为带关卡索引的流程协调器，管理开始、进行中、通关、失败和重开；`UI` 增加开始面板、下一关按钮和最终通关面板；`main.py` 只负责事件路由。关卡数据集中放在 `src/levels.py`，每个关卡用可复制的网格工厂提供，测试使用自动求解检查确实存在通关顺序。

**Tech Stack:** Python 3.10+, Pygame 2.6+, pytest 8+

---

## 当前缺口与文件地图

当前代码已经具备 Board 规则、单个树形关卡、箭头动画、碰撞反馈和基础结果面板，但课程作业还要求开始界面、至少 3 个可通关关卡、关卡切换和博客/截图材料。实现只在当前隔离 worktree 中进行，不直接修改 `main`。

| 文件 | 责任 |
| --- | --- |
| `src/levels.py` | 新增 flower、sun 两个可通关关卡、关卡工厂集合和名称 |
| `tests/test_levels.py` | 验证三个关卡、四个方向和自动可通关顺序 |
| `src/game.py` | 增加 START 状态、level_index、start/next/restart_campaign |
| `tests/test_game.py` | 验证开始、关卡切换、最终关、当前关重开 |
| `src/ui.py` | 绘制开始面板、关卡名称、下一关/重开按钮和最终通关面板 |
| `tests/test_ui.py` | 验证按钮矩形和三关 HUD 信息 |
| `main.py` | 路由开始按钮、下一关按钮、失败重开和最终重开 |
| `tests/test_main.py` | 验证 START/CLEARED/FAILED 的鼠标事件路由 |
| `README.md` | 更新课程版功能、三关、运行、测试、截图说明 |
| `docs/course-report.md` | 生成博客草稿：项目介绍、AIGC 三次记录、T01-T06 测试表、PSP 和心得框架 |
| `docs/assets/runtime-gameplay.png` | 由 Pygame 无显示器渲染生成的运行截图，用于 README |

### Task 1: 添加三关可通关关卡包

**Files:**
- Modify: `src/levels.py`
- Test: `tests/test_levels.py`

- [ ] **Step 1: 先写失败测试**

在 `tests/test_levels.py` 增加导入和行为测试：

```python
from collections import deque

from src.levels import (
    LEVEL_FACTORIES,
    LEVEL_NAMES,
    FLOWER_ARROW_GRID,
    SUN_ARROW_GRID,
    create_flower_board,
    create_sun_board,
)


def _winning_sequence(factory):
    initial = factory()
    start = tuple(tuple(row) for row in initial.arrow_grid)
    queue = deque([(start, [])])
    visited = {start}
    while queue:
        state, path = queue.popleft()
        if not any(cell in {"U", "D", "L", "R"} for row in state for cell in row):
            return path
        for row_index, row in enumerate(state):
            for col_index, cell in enumerate(row):
                if cell not in {"U", "D", "L", "R"}:
                    continue
                board = factory()
                board.arrow_grid = [list(values) for values in state]
                result = board.click(row_index, col_index)
                if not result.success:
                    continue
                next_state = tuple(tuple(values) for values in board.arrow_grid)
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((next_state, path + [(row_index, col_index)]))
    return None


def test_course_has_three_named_level_factories():
    assert len(LEVEL_FACTORIES) == 3
    assert len(LEVEL_NAMES) == 3
    assert all(factory().remaining_arrows() > 0 for factory in LEVEL_FACTORIES)


def test_extra_levels_use_all_four_arrow_directions():
    for grid in (FLOWER_ARROW_GRID, SUN_ARROW_GRID):
        arrows = {cell for row in grid for cell in row}
        assert {"U", "D", "L", "R"} <= arrows


def test_every_course_level_has_a_winning_sequence():
    for factory in LEVEL_FACTORIES:
        sequence = _winning_sequence(factory)
        assert sequence is not None
        assert len(sequence) == factory().remaining_arrows()


def test_extra_level_factories_return_independent_boards():
    first = create_flower_board()
    second = create_flower_board()
    first.arrow_grid[0][2] = "."
    assert second.arrow_grid[0][2] == "U"

    first = create_sun_board()
    second = create_sun_board()
    first.arrow_grid[0][0] = "."
    assert second.arrow_grid[0][0] == "U"
```

- [ ] **Step 2: 运行新增测试确认 RED**

运行 `python -m pytest tests/test_levels.py -q`。预期因新常量和工厂不存在而失败，既有树形关卡测试保留通过。

- [ ] **Step 3: 实现两个关卡和集合**

在 `src/levels.py` 增加以下两个网格。每个 `None` 与颜色掩码同步，`"."` 表示像素图中原本没有箭头但保留底色的位置：

```python
FLOWER_ARROW_GRID = (
    (None, None, "U", None, None),
    (None, "L", "U", "R", None),
    ("L", "L", ".", "R", "R"),
    (None, "L", "D", "R", None),
    (None, None, "D", None, None),
)
FLOWER_COLOR_GRID = (
    (None, None, "flower", None, None),
    (None, "flower", "flower", "flower", None),
    ("leaf", "flower", "leaf_light", "flower", "leaf"),
    (None, "leaf", "trunk", "leaf", None),
    (None, None, "grass", None, None),
)

SUN_ARROW_GRID = (
    ("U", "U", "U", "U"),
    ("L", "U", "U", "R"),
    ("L", "D", "D", "R"),
    ("L", "D", "D", "R"),
)
SUN_COLOR_GRID = (
    ("flower", "flower", "flower", "flower"),
    ("flower", "leaf_light", "leaf_light", "flower"),
    ("grass", "leaf", "leaf", "grass"),
    ("grass", "trunk", "trunk", "grass"),
)


def create_flower_board() -> Board:
    return Board(
        [list(row) for row in FLOWER_ARROW_GRID],
        [list(row) for row in FLOWER_COLOR_GRID],
    )


def create_sun_board() -> Board:
    return Board(
        [list(row) for row in SUN_ARROW_GRID],
        [list(row) for row in SUN_COLOR_GRID],
    )


LEVEL_NAMES = ("TREE", "FLOWER", "SUN")
LEVEL_FACTORIES = (create_tree_board, create_flower_board, create_sun_board)
```

- [ ] **Step 4: 运行关卡测试确认 GREEN**

运行 `python -m pytest tests/test_levels.py -q`，确认三关都有非空解，并确认 `Board` 原有测试不变。

- [ ] **Step 5: 提交关卡任务**

```bash
git add src/levels.py tests/test_levels.py
git commit -m "feat: add three playable course levels"
```

### Task 2: 扩展 Game 为关卡流程和开始状态

**Files:**
- Modify: `src/game.py`
- Test: `tests/test_game.py`

- [ ] **Step 1: 先写失败测试**

新增以下行为测试，保持原有单关卡测试可继续使用 callable 工厂：

```python
from src.levels import LEVEL_FACTORIES


def test_campaign_can_start_from_menu_and_reports_level_count():
    game = Game(LEVEL_FACTORIES, start_in_menu=True)
    assert game.state is GameState.START
    assert game.level_count == 3
    assert game.level_index == 0
    assert game.level_number == 1


def test_start_enters_first_level_and_next_level_replaces_board():
    game = Game(LEVEL_FACTORIES, start_in_menu=True)
    game.start()
    first_board = game.board
    assert game.state is GameState.PLAYING
    assert game.level_name == "TREE"

    game.state = GameState.CLEARED
    assert game.next_level() is True
    assert game.level_index == 1
    assert game.level_name == "FLOWER"
    assert game.board is not first_board
    assert game.state is GameState.PLAYING


def test_last_level_reports_no_next_level_and_campaign_restart_returns_to_first():
    game = Game(LEVEL_FACTORIES)
    game.level_index = 2
    game.restart()
    game.state = GameState.CLEARED
    assert game.has_next_level is False
    assert game.next_level() is False
    game.restart_campaign()
    assert game.level_index == 0
    assert game.state is GameState.PLAYING
```

- [ ] **Step 2: 运行测试确认 RED**

运行 `python -m pytest tests/test_game.py -q`，预期新测试因 START、关卡属性和方法不存在而失败。

- [ ] **Step 3: 实现最小流程接口**

`Game` 接受 callable 或 callable sequence，新增 `GameState.START`、`level_index`、`level_count`、`level_number`、`level_name`、`has_next_level`、`start()`、`next_level()`、`restart_campaign()`；默认单工厂仍保持 `PLAYING`，主入口显式传 `start_in_menu=True`。清空最后一关仍使用 `CLEARED`，由 `has_next_level` 决定按钮显示“下一关”还是“重新开始”。

- [ ] **Step 4: 运行 Game 与全量测试**

运行 `python -m pytest tests/test_board.py tests/test_levels.py tests/test_animation.py tests/test_game.py -q`，确认既有生命、碰撞、重开和动画测试通过。

- [ ] **Step 5: 提交 Game 任务**

```bash
git add src/game.py tests/test_game.py
git commit -m "feat: add start and multi-level game flow"
```

### Task 3: 增加开始界面、下一关和结果流程

**Files:**
- Modify: `src/ui.py`, `main.py`
- Test: `tests/test_ui.py`, `tests/test_main.py`

- [ ] **Step 1: 先写失败测试**

增加事件路由测试：START 点击开始，CLEARED 有下一关时进入下一关，FAILED 重置当前关，最终 CLEARED 重置整局；增加 `UI.start_rect()` 和 `UI.result_action_rect()` 的矩形测试。

- [ ] **Step 2: 运行聚焦测试确认 RED**

运行 `python -m pytest tests/test_main.py tests/test_ui.py -q`，预期因按钮接口和 START 路由不存在而失败。

- [ ] **Step 3: 实现 UI 和入口**

`UI.draw()` 在 START 状态只绘制背景和开始面板；游戏状态绘制棋盘/HUD；CLEARED 或 FAILED 绘制结果面板。保留 `restart_rect()` 兼容旧测试，并让 `result_action_rect()` 返回同一按钮位置。`main.process_event()` 按状态路由：START 调 `game.start()`；CLEARED 调 `next_level()` 或 `restart_campaign()`；FAILED 调 `restart()`；PLAYING 才把棋盘点击传给 `Game.click()`。HUD 显示 `LEVEL 01/03` 和当前关卡名。

- [ ] **Step 4: 运行 UI、入口和全量测试**

运行 `python -m pytest tests/test_main.py tests/test_ui.py -q`，再运行 `python -m pytest -q`。

- [ ] **Step 5: 提交流程任务**

```bash
git add src/ui.py main.py tests/test_ui.py tests/test_main.py
git commit -m "feat: add start screen and level progression UI"
```

### Task 4: 完成 README、AIGC/测试博客材料和截图

**Files:**
- Modify: `README.md`
- Create: `docs/course-report.md`
- Create: `docs/assets/runtime-gameplay.png`

- [ ] **Step 1: 更新 README**

README 必须写明项目名、Python/Pygame 环境、安装命令、`python main.py`、开始按钮/鼠标点击/结果按钮操作、三关说明、运行测试命令、AIGC 协作说明和截图 Markdown：

```markdown
![游戏运行截图](docs/assets/runtime-gameplay.png)
```

- [ ] **Step 2: 创建博客草稿**

`docs/course-report.md` 记录课程作业表头、规则与路径检测、模块分工、T01-T06 测试结果、至少三次真实 AIGC 协作（需求/关卡/动画调试）、PSP 表格和心得。个人学号、课程链接和实际耗时不能由代码推断，明确标注为提交前需要本人填写的字段。

- [ ] **Step 3: 生成运行截图**

使用 Pygame dummy video driver 创建 1200×800 surface，构造 START 和 PLAYING 两个状态并保存一张实际 UI PNG 到 `docs/assets/runtime-gameplay.png`；截图不得引入外部商业素材。

- [ ] **Step 4: 检查 README 与报告文件**

运行 `rg -n "运行|安装|测试|AIGC|PSP|T01|截图|GitHub" README.md docs/course-report.md`，确认各课程要求都有对应文字；运行 `git diff --check`。

- [ ] **Step 5: 提交文档任务**

```bash
git add README.md docs/course-report.md docs/assets/runtime-gameplay.png
git commit -m "docs: complete course assignment materials"
```

### Task 5: 集成验收与交付

**Files:**
- Modify: 仅当验收发现问题时修改对应源文件和回归测试

- [ ] **Step 1: 自动化验收**

运行：

```bash
python -m pytest -v
python -m compileall -q main.py src tests
git diff --check
```

预期：全部测试通过，编译和空白检查退出码为 0。

- [ ] **Step 2: 无显示器主循环 smoke test**

运行：

```powershell
$env:SDL_VIDEODRIVER='dummy'; python -c "import pygame; import main; pygame.init(); pygame.event.post(pygame.event.Event(pygame.QUIT)); main.main(); print('main_smoke_ok')"
```

- [ ] **Step 3: 手工验收清单**

运行 `python main.py`，检查开始界面、三关顺序、四方向路径、飞出、碰撞变红回退、连续点击、失败重开、通关后下一关和最终重开。每关用测试中的 winning sequence 或手动试玩确认可以清空。

- [ ] **Step 4: 检查 Git 提交范围和远端**

运行 `git status --short --branch`、`git log --oneline -12` 和 `git remote -v`。工作区应干净，提交应覆盖关卡、流程、UI、测试和文档；向 GitHub 推送前不上传密钥或临时文件。

- [ ] **Step 5: 使用 finishing-a-development-branch 收尾**

验证完成后按 detached worktree 收尾流程向用户提供保留、推送创建 PR 或丢弃选项；在用户选择前不合并到 `main`。

## 自检

- 三个 `LEVEL_FACTORIES` 都有 BFS 验证的通关顺序；
- START、PLAYING、CLEARED、FAILED 的界面和事件路由都有测试；
- T01-T06 可由自动化测试和博客表格对应；
- AIGC 日志只记录真实开发过程，不声称不存在的工具调用；
- 课程链接、学号和实际耗时保留给提交者本人填写；
- 不加入非必要的音效、计时、星级等扩展，先保证基础 100 分要求。
