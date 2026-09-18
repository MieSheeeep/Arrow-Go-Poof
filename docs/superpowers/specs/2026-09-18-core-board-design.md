# “一箭又一箭”核心棋盘设计

## 目标与范围

第一轮开发搭建 Python 项目骨架，并实现可脱离 Pygame 测试的棋盘规则。范围包括关卡数据、棋盘状态、箭头路径判定、点击结果、通关统计和重置。不包括正式 UI、动画、音效、生命值、计时、Combo、星级及页面流程。

仓库本身作为项目根目录，直接放置 `main.py`、`src/`、`tests/`、`assets/` 和 `docs/`，不再增加一层同名项目目录。

## 模块边界

- `src/board.py`：定义 `Board`、不可变的 `MoveResult`、方向集合及路径规则。只负责棋盘规则和状态变化，不依赖 Pygame。
- `src/levels.py`：保存最小示例关卡，并通过工厂函数创建新 `Board`，避免共享可变运行状态。
- `src/game.py`、`src/ui.py`、`src/animation.py`：本轮仅建立带职责说明的最小模块，不预先实现后续功能。
- `main.py`：最小命令行入口，用于确认示例关卡可加载；不创建正式窗口。
- `tests/test_board.py`：覆盖路径规则、点击结果、状态变化、重置、输入隔离和关卡校验。

## 数据模型

`arrow_grid` 是矩形二维列表：

- `None` 表示棋盘外或无效区域；
- `"."` 表示属于像素画但箭头已经清除；
- `"U"`、`"D"`、`"L"`、`"R"` 表示仍存在的箭头。

`color_grid` 与 `arrow_grid` 尺寸相同。无效位置必须同为 `None`，有效位置必须有非 `None` 的颜色或颜色 ID。颜色值的具体类型本轮不限制。

`MoveResult` 是冻结的 dataclass：

```python
@dataclass(frozen=True)
class MoveResult:
    success: bool
    row: int
    col: int
    direction: str | None
    reason: str
    blocker: tuple[int, int] | None = None
```

## 初始化与状态隔离

`Board(arrow_grid, color_grid)` 校验两个网格均为非空矩形二维结构、尺寸一致、箭头值合法，且两者的有效区域掩码一致。非法关卡配置抛出 `ValueError`。

Board 深复制传入数据。它分别保存不可被运行过程修改的初始箭头网格和当前箭头网格；`reset()` 从初始副本重新生成当前状态。调用方原始关卡数据不会因点击或重置而变化。

## 路径判定

`can_fly(row, col)` 对越界、`None` 和 `"."` 返回 `False`。合法箭头从相邻格开始沿方向逐格检查，并在访问数组前检查边界：

1. 越出二维数组边界：箭头已离开谜题区域，可以飞出；
2. 遇到 `None`：箭头已离开不规则谜题区域，可以飞出，不再检查 `None` 后方；
3. 遇到 `"."`：继续前进；
4. 遇到任一仍存在的箭头：不能飞出，该坐标是第一个阻挡位置。

内部使用一个私有路径检查方法同时服务 `can_fly()` 和 `click()`，保证布尔判断、失败原因及阻挡位置来自同一套规则。

## 点击与状态变化

`click(row, col)` 永不因普通点击位置而抛出索引异常，而是返回以下结果：

| 情况 | success | reason | direction | blocker |
| --- | --- | --- | --- | --- |
| 成功飞出 | `True` | `"clear"` | 原方向 | `None` |
| 被阻挡 | `False` | `"blocked"` | 原方向 | 第一个阻挡坐标 |
| 点击越界 | `False` | `"out_of_bounds"` | `None` | `None` |
| 点击无效区域 | `False` | `"invalid_cell"` | `None` | `None` |
| 点击已清除格 | `False` | `"already_cleared"` | `None` | `None` |

只有 `"blocked"` 表示后续 Game 层需要扣生命。成功点击会在返回前立即将当前位置改为 `"."`，与未来动画完全解耦；因此动画期间重复点击同一位置会得到 `"already_cleared"`。

## 查询能力

- `in_bounds(row, col)`：判断坐标是否处于矩形数组范围内；非整数坐标返回 `False`，布尔值不作为合法坐标。
- `get_cell(row, col)`：越界时安全返回 `None`，否则返回当前箭头格状态。
- `is_arrow(row, col)`：仅当当前值属于四个方向时返回 `True`。
- `remaining_arrows()`：统计当前仍存在的箭头。
- `is_cleared()`：当剩余箭头数量为零时返回 `True`。
- `reset()`：恢复初始箭头网格；颜色网格不参与运行时修改。

## 测试策略

使用 pytest 严格按测试先行实现。核心测试覆盖：无遮挡、路径阻挡、跨越已清除格后仍被阻挡、边缘向外、`None` 立即离开区域、`"."` 可穿过、清除最后箭头、重置、三类非法点击、首个阻挡坐标、成功后立即更新、重复点击、剩余数量、输入深复制，以及尺寸、矩形结构、箭头合法值和有效区域掩码校验。

`Board` 测试全部使用真实对象，不使用 Pygame 或 mocks。最终执行完整 `pytest`，并用最小入口加载示例关卡验证项目骨架可运行。
