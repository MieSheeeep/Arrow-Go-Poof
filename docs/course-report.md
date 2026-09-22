# “一箭又一箭”课程作业博客草稿

## 作业信息

| 项目内容 | 内容 |
| --- | --- |
| 这个作业属于哪个课程 | **提交前填写课程名称和课程链接** |
| 这个作业要求在哪里 | **提交前填写作业链接** |
| 这个作业的目标 | 使用 Python 和 AIGC 完成“一箭又一箭”小游戏 |
| 学号 | **提交前填写本人学号** |
| GitHub 仓库 | <https://github.com/MieSheeeep/Arrow-Go-Poof> |

## 1. 项目展示

项目启动后先显示带装饰箭头棋盘的工作桌封面，点击 `START GAME` 进入第一关。游戏窗口为 1200×800，中心区域是一块由箭头组成的**不规则像素区域**——图案外是背景，图案内每个像素位置都覆盖一枚单格箭头；三关依次为 16×16 附魔金苹果、16×16 精灵球和 18×17 月亮 Hello Kitty。成功点击后箭头沿自身方向飞出窗口，原位置露出下方隐藏的拼豆颜色；被阻挡时箭头移动到首个阻挡箭头、撞击变红并回退。顶部状态栏显示关卡、倒计时、三颗生命和暂停键；暂停后可继续、重开本关或返回主界面；通关页显示冻结的时间和逐颗弹出的星级。

<img src="assets/runtime-start.png" alt="开始界面（封面）" style="zoom:50%;" />

![游戏界面（顶部倒计时与三颗生命）](assets/runtime-gameplay.png)
![月亮 Hello Kitty 关卡](assets/runtime-moon-kitty.png)
![通关结果界面](assets/runtime-result.png)
![失败界面](assets/runtime-failed.png)
![暂停菜单](assets/runtime-paused.png)

建议发布博客时补充：碰撞变红瞬间截图，以及一段展示三关切换与飞出/碰撞动画的 GIF 或视频。

## 2. 项目介绍

玩家每次点击一个箭头，程序检查它沿自身方向到棋盘边界之间的同行或同列位置。如果没有其他箭头，Board 立即把它标记为已清除，Game 创建飞出动画；如果存在其他箭头，Board 返回首个 blocker，Game 立即扣除一次失误机会，CollisionAnimation 负责撞击、变红和回退。

与普通“正方形棋盘里零散放几个箭头”不同，本项目的棋盘是**不规则像素区域**：`U/D/L/R` 是四种方向箭头，`.` 是已露出的像素位置，`None` 是图案外的背景。只有属于图案的像素格才放置箭头，因此整个谜题的外轮廓会自然呈现像素画的形状（如月亮 Hello Kitty 的轮廓），而不是一个完整方框。箭头清除后，原位置显示颜色网格中的拼豆颜色，玩家在解谜过程中一点点“揭开”整幅像素画。

项目包含 ENCHANTED APPLE、BEAD BALL、MOON KITTY 三个关卡。每个关卡由二维箭头网格和颜色网格表示，三关均根据提交者提供的 `.px` 拼豆工程图案制作：附魔金苹果和精灵球为 16×16 固定网格，月亮 Hello Kitty 在设计阶段等比例压缩为 18×17；三个方向布局都通过固定种子生成、验证后复制为常量，因此每次启动布局相同，不会因随机生成而出现不可解关卡。

主要模块如下：

- `src/board.py`：纯规则层，负责网格校验、路径检测、点击结果和清除，不依赖 Pygame；
- `src/game.py`：负责生命值、失误次数、倒计时、开始/通关/失败/暂停状态、关卡索引和星级结算，并把规则结果转成动画；
- `src/animation.py`：不依赖 Pygame 的飞出、碰撞、扣心和星星弹出时间模型；
- `src/ui.py`：负责背景、棋盘、HUD（关卡/倒计时/生命/暂停）、开始/结果/暂停面板和坐标映射；
- `src/level_generator.py`：仅用于开发与测试；根据颜色掩码生成可解方向布局及其验证顺序，运行时不调用；
- `main.py`：负责 Pygame 初始化、事件分发、更新和绘制。

## 3. 实现思路

整体按 **Board / Game / UI 三层**划分。Board 只处理网格规则与状态；Game 管理生命、计时、得分、关卡状态，并把规则结果翻译为动画对象；UI 只做坐标换算和绘制。这样一来，规则不依赖 Pygame，动画也能以纯时间模型单独测试。

### 规则层：找到第一个阻挡物，而不是只看相邻格

最关键的约定是：`None` 表示像素画外的区域，箭头走到它就已经离开谜题；`.` 是已清除但仍属于图案的格子，可以穿过。因此路径检测必须逐格扫描，并在遇到第一个仍存在的箭头时记录坐标。`Board` 中对应的核心代码如下：

```python
while self.in_bounds(row, col):
    cell = self.arrow_grid[row][col]
    if cell is None:
        return None
    if cell in ARROWS:
        return row, col
    row += row_delta
    col += col_delta
```

这段代码同时避免了向上或向左移动时触发 Python 负索引的问题。点击方法再把“是否有 blocker”转换为结构化结果：

```python
blocker = self._find_blocker(row, col)
if blocker is not None:
    return MoveResult(False, row, col, cell, "blocked", blocker)

self.arrow_grid[row][col] = "."
return MoveResult(True, row, col, cell, "clear")
```

成功时立即写入 `"."`，而不是等待动画播放完毕。这样飞出的那一帧，逻辑棋盘已经露出颜色；再次点同一位置会得到 `already_cleared`，不会重复计分或重复生成动画。

### 流程层：逻辑先改变，视觉后跟上

`Game.click()` 不自己判断方向是否畅通，而是消费 `Board.click()` 的结果。成功分支创建飞出动画并累计 Combo/Score；最后一箭清除时冻结结算数据并追加星星动画。其顺序保证了动画不会阻塞下一次合法点击：

```python
result = self.board.click(row, col)
if result.reason == "clear":
    self.animations.append(FlyOutAnimation(row, col, result.direction))
    self.combo += 1
    self.score += 10 * self.combo
    if self.board.is_cleared():
        self.level_summary = LevelSummary(
            self.elapsed_seconds, self.mistakes,
            self.score, self.max_score,
            _stars_for_score(self.score, self.max_score),
        )
        self.animations.append(StarRevealAnimation(self.level_summary.stars))
```

相反，`blocked` 分支保留原箭头、扣除生命并创建带 blocker 坐标的 `CollisionAnimation`；动画完成后才把起点加入 `error_cells`，实现“前进碰撞 → 变红 → 回退 → 留下错误标记”。扣心也使用独立的 `HeartLossAnimation`，静态生命值立即减少，闪烁淡出只是视觉反馈。

倒计时由 `Game.elapsed_seconds` 统一维护，仅在 `PLAYING` 状态累加；暂停、通关和失败后都会冻结。HUD 读取 `remaining_seconds` 绘制倒计时和进度条。星级则只和本关总得分有关：若初始箭头数为 `N`，满连击的理论最高分是 `5 × N × (N + 1)`；达到它的 85% 得 3 星，达到 60% 得 2 星，否则为 1 星。时间仍可导致超时失败，阻挡仍会打断 Combo 间接拉低得分，但二者不再直接决定星级。

### 提示系统：给建议，但不替玩家操作

提示按钮没有直接删除箭头，也不把答案写进关卡。它只是向 Game 查询当前第一个可飞出的箭头，保存一个 UI 高亮坐标：

```python
elif ui.hint_rect().collidepoint(event.pos):
    ui.hint_cell = game.hint()

def hint(self) -> tuple[int, int] | None:
    if self.state is not GameState.PLAYING:
        return None
    return self.board.first_clearable_arrow()
```

`first_clearable_arrow()` 逐行调用同一套 `can_fly()` 规则，因此提示和真实点击不会出现两套判定。绘制前 UI 还会再次确认该坐标仍是箭头：

```python
if self.hint_cell is None or self.game.state is not GameState.PLAYING:
    return
row, col = self.hint_cell
if self.game.board.get_cell(row, col) not in {"U", "D", "L", "R"}:
    return
```

这一步处理了“提示出现后，玩家先手动消除了该箭头”的情况。确认有效后，UI 在格子外画随时间正弦变化的双层描边；提示始终是只读建议，玩家仍需自己点击。

### 飞行 UI 判定与绘制：用格子位移驱动像素位置

`FlyOutAnimation` 只保存 `row`、`col`、方向、时间和 `offset_cells`，不依赖窗口大小。它先有很短的反向蓄力，再按缓动曲线向箭头方向飞行；拖尾长度也随飞行进度增加。UI 接手后才把“移动了多少格”转换为“移动了多少像素”：

```python
rect = self.layout.cell_rect(animation.row, animation.col)
offset_row, offset_col = animation.offset_cells
center = (
    rect.centerx + round(offset_col * self.layout.cell_size),
    rect.centery + round(offset_row * self.layout.cell_size),
)
```

因此同一个动画模型可以适应不同关卡的格子尺寸；UI 还在飞行箭头后面补上三段渐隐拖尾，并在被清除的原格画短暂的 reveal glow。这里没有重新修改 Board：飞行对象只是已经完成的逻辑操作的可视化副本。

### 一次挫折与改进：箭头“飞出”却没有飞远

**现象：** 最初的飞出动画使用固定两格的位移。逻辑上箭头确实被清除了，但在 1200×800 的窗口里，视觉效果更像突然消失，玩家很难感受到“飞出”。

**定位：** 通过试玩和检查 `Board → Game.animations → UI._draw_animations()` 的数据流，确认问题不在规则层，而在动画只给了过短的 `offset_cells`；已有“动画结束”的测试也没有验证箭头是否离开可视区域。

**修改：** 改为按方向设置能越过窗口边界的默认飞行距离，并加入反向蓄力、缓动和拖尾。Board 仍然在点击成功的瞬间写入 `"."`，所以这次改动只限于 `FlyOutAnimation` 与 UI 绘制，不会改变关卡规则。

**回归测试：** `test_default_fly_out_distance_carries_arrow_past_window` 覆盖上下左右四个方向，验证默认距离足以把箭头送出窗口；同时保留蓄力阶段和完成阶段测试。这个问题也提醒我：单元测试能验证状态，真正的交互观感还需要运行试玩来发现。

关卡的设计采用“先确定图案、再冻结布局”的方式：先用附魔金苹果、精灵球或 Hello Kitty 的颜色掩码确定可见轮廓；生成工具在仍存在的箭头中选择一条无阻挡射线，把该坐标加入清除顺序并记录方向。重复到所有格子被选中后，得到的顺序天然可通关。工具使用固定种子保证可复现，最终的箭头网格和通关顺序都写入 `levels.py` 常量，避免把随机性带进游戏运行时。

## 4. AIGC 使用过程

以下记录来自实际开发过程，代码进入项目后均经过人工检查、测试和修改。

| 子任务 | 使用的 AIGC | AI 提供的帮助 | 实际效果与人工修改 |
| --- | --- | --- | --- |
| 需求分析与界面方向 | ChatGPT/Codex + 图像生成参考 | 将“箭头遮罩逐渐揭开像素图”的想法整理为窗口布局、颜色层级和交互状态 | 初始方案直接进入关卡，后来根据课程要求补充开始界面；保留几何绘制，不复制商业素材 |
| 工作桌背景美术 | 用户提供图片 + Codex | 提供一张包含拼豆盒、工作桌垫和手作工具的工作桌图片；Codex 将它接入开始和游戏界面，并把棋盘限制在桌垫内 | 人工确认图片中央留白适合标题、按钮和拼豆棋盘；保留代码绘制的标题和按钮 |
| 路径检测、Game 分层和测试设计 | Codex | 设计 Board/Game/Animation/UI 分层，生成方向检测和状态转换测试 | 人工核对边界、非法点击、重复点击和生命值归零；增加独立关卡工厂测试 |
| 飞出动画 Bug 调试 | ChatGPT/Codex | 根据试玩反馈追踪 Board 清除、Game 动画列表和 UI 绘制之间的数据流 | 发现飞出距离固定为 2 格导致箭头突然消失；先写失败回归测试，再改为越过 1200×800 窗口边界的方向距离 |
| 关卡设计与可通关验证 | Codex | 根据提交者提供的附魔金苹果、精灵球、月亮 Hello Kitty `.px` 拼豆图案生成固定方向布局和验证顺序 | 将大尺寸 Hello Kitty 等比例压缩为 18×17；三关均固定种子结果并加入逐步清空测试 |

## 5. 测试结果

自动化测试命令：

```bash
python -m pytest -v
python -m compileall -q main.py src tests
```

当前结果以本机最新命令输出为准：`186 passed`。自动化测试覆盖 Board 规则、四方向路径、三关可通关顺序、固定种子布局、飞出与碰撞动画、扣心反馈、倒计时与按总分结算的星级、开始/通关/失败/暂停/重开、鼠标事件路由和 UI 布局。

| 编号 | 测试内容 | 预期结果 | 实际结果 | 是否通过 |
| --- | --- | --- | --- | --- |
| T01 | 点击前方无阻挡的箭头 | 箭头从逻辑棋盘清除并飞出 | `Game` 创建 `FlyOutAnimation`，测试通过 | 通过 |
| T02 | 点击前方有阻挡的箭头 | 箭头不消失，失误次数减 1 | `CollisionAnimation` 命中 blocker 并扣除生命，测试通过 | 通过 |
| T03 | 点击边缘且朝向棋盘外的箭头 | 正常消失，不发生越界 | Board 边界检测通过，测试通过 | 通过 |
| T04 | 清除本关全部箭头 | 显示通关并进入下一关 | 三关工厂和 `next_level()` 测试通过 | 通过 |
| T05 | 失误次数耗尽 | 显示失败并允许重开 | `FAILED` 状态拒绝普通点击，结果按钮重开，测试通过 | 通过 |
| T06 | 游戏进行中重新开始 | 棋盘和失误次数恢复 | `restart()` 清空动画/错误标记并恢复关卡，测试通过 | 通过 |
| T07 | 三个拼豆关卡的固定布局 | 每次启动方向相同且存在通关顺序 | 固定种子复算、已冻结顺序逐步清空，测试通过 | 通过 |
| T08 | 飞出与碰撞动画 | 飞出有蓄力并越过窗口；碰撞变红、回退后保留错误标记 | `FlyOutAnimation` 阶段与越界距离、`CollisionAnimation` 阶段与 `error_cells` 时序测试通过 | 通过 |
| T09 | 倒计时 | 仅对局计时；暂停/通关/失败后冻结；重开清零；超时失败 | `Game.elapsed_seconds` 状态转换与超时测试通过 | 通过 |
| T10 | 总得分星级结算 | 达到最高分 85%/60% 的边界时正确获得 3/2 星，低于 60% 为 1 星 | 得分边界、时间/失误不直接影响星级与 `StarRevealAnimation` 测试通过 | 通过 |
| T11 | 游戏中重开与返回主菜单 | 操作按钮不触发棋盘点击，状态正确复位 | 事件路由与 `return_to_menu()` 测试通过 | 通过 |
| T12 | 暂停、继续与暂停菜单操作 | 暂停时计时冻结，继续后计时恢复；重开/返回菜单不触发棋盘点击 | `PAUSED` 状态与事件路由测试覆盖 | 通过 |

## 6. PSP 表格

以下“实际耗时”应根据本人真实记录填写，不能由 AI 代填：

| 任务 | 预估耗时（小时） | 实际耗时（小时） | 差异（小时） |
| --- | ---: | ---: | ---: |
| 需求分析与游戏设计 | 1.0 | **待填写** | **待计算** |
| Python 与 Pygame 学习 | 1.5 | **待填写** | **待计算** |
| 游戏界面实现 | 2.0 | **待填写** | **待计算** |
| 路径与碰撞逻辑实现 | 2.0 | **待填写** | **待计算** |
| 关卡设计 | 1.0 | **待填写** | **待计算** |
| AIGC 辅助开发 | 2.0 | **待填写** | **待计算** |
| 测试与修改 | 1.5 | **待填写** | **待计算** |
| README 与博客撰写 | 1.0 | **待填写** | **待计算** |
| 合计 | 12.0 | **待填写** | **待计算** |

## 7. 心得体会草稿

这次作业让我第一次较完整地走了一遍“用 AIGC 协作做一个小游戏”的流程。它确实提升了需求拆分、代码骨架、测试用例和 Bug 定位的速度，但它给出的只是候选方案；规则边界、交互体验和最终提交内容仍然需要我自己运行、检查和负责。

印象最深的是飞出动画的 Bug。最初版本把飞行距离写成固定两格，逻辑上箭头已经清除，视觉上却像突然消失。这个问题单看 `Board` 和状态测试不容易发现，是试玩时才暴露出来的。之后我补充了“默认飞行距离必须越过窗口”的回归测试，再沿着 Board 清除、Game 动画列表和 UI 像素绘制的链路定位，最后把动画改为按方向飞出可视区域。它让我意识到：状态正确并不等于体验正确，运行试玩同样是验证的一部分。

提示功能也让我更清楚地认识到分层边界。开始时我担心提示会和玩家点击走出两套规则，之后让 `Game.hint()` 直接调用 Board 的可飞行判断，UI 只保存并高亮返回的坐标；绘制前再检查该格是否仍为箭头。这样提示不会替玩家操作，也不会在箭头已被消除后留下错误高亮。这个小功能虽然不复杂，却让我体会到“单一规则来源”比单纯把功能做出来更重要。

分层设计在后期修改时帮了很大忙。Board 的路径规则、Game 的倒计时/扣心/得分与 UI 的渲染分开后，动画模型可以脱离 Pygame 单独测试；将星级从时间和失误改为总分比例时，也只需要修改结算逻辑和测试，而不必重写结果页。最终项目跑过 186 个用例。没有这些边界，逻辑很容易散落到绘制代码里，既难改也难测。

总的来说，AI 更适合作为协作型开发工具：它能快速提供结构和实现思路，但不能代替我判断“这个规则是否符合玩法”“这个动画是否真的自然”以及“测试是否覆盖了关键边界”。这次经历让我对“先写能失败的测试，再改实现；再用试玩检查体验”的流程有了更具体的认识。
