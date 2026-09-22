# Arrow-Go-Poof（一箭又一箭）

基于 Python 和 Pygame 的桌面箭头消除解谜游戏。玩家点击无阻挡的箭头，让它飞出不规则棋盘，并逐格揭开下方的拼豆像素图。

项目重点不在复杂 UI，而在可测试的棋盘规则、逻辑与动画解耦，以及固定可通关的像素图关卡。

## 快速开始

要求：Python 3.10+。

```bash
python -m pip install -r requirements.txt
python main.py
```

运行测试：

```bash
python -m pytest -q
python -m compileall -q main.py src tests
```

## 核心玩法

每个有效格开始时包含一个 `U`、`D`、`L` 或 `R` 箭头。

- `None`：图案外的无效区域；箭头射线到达它时，视为已经离开谜题。
- `.`：已经清除的有效格；箭头可以穿过。
- `U/D/L/R`：仍存在的箭头；路径遇到的第一个箭头就是 blocker。

点击一个箭头时，Board 从下一格开始沿方向扫描：若没有 blocker，立即将当前位置写为 `.` 并返回 `clear`；若有 blocker，棋盘不变并返回 `blocked` 及 blocker 坐标。成功清除不等待动画完成，因此飞行动画期间仍可以继续操作其他箭头。

## 核心设计

| 模块 | 职责 |
| --- | --- |
| `Board` | 纯规则层：网格校验、路径检测、点击结果、剩余箭头与重置；不依赖 Pygame。 |
| `Game` | 流程层：生命、计时、得分、关卡状态，以及把 `MoveResult` 转换为动画。 |
| `Animation` | 纯时间模型：飞出、碰撞、掉心、星星弹出；只输出阶段、位移和缩放等数据。 |
| `UI` | 表现层：格子坐标换算、HUD、提示高亮和动画绘制；不改变 Board 规则。 |

数据流为：`鼠标坐标 → UI 格子坐标 → Game.click() → Board.click() → MoveResult → Game 动画列表 → UI 绘制`。

## 关键约定

### 不规则棋盘

关卡用尺寸一致的 `arrow_grid` 和 `color_grid` 表示。前者服务规则，后者保存清除箭头后应露出的颜色；两者的 `None` 位置共同确定像素图轮廓。

### 提示与真实操作使用同一规则

`Game.hint()` 调用 `Board.first_clearable_arrow()`，只返回当前可飞出的坐标。UI 在绘制高亮前再次检查该格仍是箭头，因此提示不会替玩家操作，也不会在箭头已清除后留下过期高亮。

### 动画不阻塞逻辑

成功点击后 Board 已经更新，`FlyOutAnimation` 只是该次操作的视觉副本。碰撞动画则使用 Board 返回的 blocker 坐标，绘制“接近、撞击变红、回退”的过程。

### 按得分结算星级

若关卡初始有 `N` 枚箭头，满连击的理论最高分为 `5 × N × (N + 1)`。最终得分达到最高分的 85% 为 3 星，达到 60% 为 2 星，其余通关为 1 星。倒计时只负责超时失败；阻挡会中断 Combo，从而间接影响得分。

## 项目结构

```text
main.py             Pygame 入口与事件分发
src/                Board、Game、动画、UI、关卡与音效实现
tests/              pytest 自动化测试
assets/             游戏图片、字体与声音资源
docs/               课程报告、测试计划与 AIGC 记录
```

## 项目文档

- [课程作业报告](docs/course-report.md)
- [测试计划](docs/test-plan.md)
- [AIGC 使用记录](docs/aigc-log.md)

仓库：<https://github.com/MieSheeeep/Arrow-Go-Poof>
