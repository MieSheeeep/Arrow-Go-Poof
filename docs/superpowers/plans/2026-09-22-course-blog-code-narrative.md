# Course Blog Code Narrative Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich the existing course blog with concise, accurate implementation excerpts and a concrete iteration retrospective while preserving the mandated section numbering.

**Architecture:** This is a documentation-only change to `docs/course-report.md`. Section 3 will connect four existing code paths—Board rule resolution, Game-to-animation translation, the read-only hint flow, and logical-to-pixel fly-out rendering—using short excerpts from the current source. Section 7 will turn the real short-distance fly-out defect into an evidence-based “symptom → diagnosis → correction → regression test” reflection.

**Tech Stack:** Markdown, Python 3, pytest, Pygame project source for verification.

---

## File structure

- Modify: `docs/course-report.md` — retain the original “作业信息” table and sections 1–7; improve Section 3 and Section 7, then refresh the test count only from a newly run command.
- Inspect: `src/board.py` — `_find_blocker()`, `first_clearable_arrow()`, and `click()` define the puzzle outcome and blocker coordinate.
- Inspect: `src/game.py` — `hint()` and `click()` convert Board results to application state and animations.
- Inspect: `src/animation.py` — `FlyOutAnimation.offset_cells` encodes wind-up and outbound motion in logical cell units.
- Inspect: `src/ui.py` and `main.py` — hint button routing, pulsing hint outline, and the cell-unit to pixel conversion.

### Task 1: Verify source excerpts and current automated-test evidence

**Files:**
- Inspect: `src/board.py:93-134`
- Inspect: `src/game.py:205-209`, `src/game.py:283-305`
- Inspect: `src/animation.py:82-123`
- Inspect: `main.py:44-66`, `src/ui.py:632-678`, `src/ui.py:1039-1063`
- Inspect: `tests/test_animation.py`, `tests/test_board.py`, `tests/test_game.py`, `tests/test_ui.py`

- [ ] **Step 1: Extract the exact behavior that the blog will show**

Confirm that the excerpts implement these facts before quoting them:

```text
Board: None ends a ray, '.' is traversable, first U/D/L/R is the blocker,
and a clear click immediately writes '.'.
Hint: main.py assigns ui.hint_cell = game.hint(); Game returns
board.first_clearable_arrow() only during PLAYING; UI draws a pulse only when
that cell is still an arrow.
Fly-out: FlyOutAnimation produces offset_cells; UI multiplies those offsets by
layout.cell_size before drawing the transient arrow and its trail.
```

- [ ] **Step 2: Run the full test command before documenting its result**

Run:

```powershell
python -m pytest -v
python -m compileall -q main.py src tests
```

Expected: pytest exits with code 0; compileall exits with code 0. Record the exact passed-test count from pytest for Section 5 rather than retaining an unverified historical count.

### Task 2: Rewrite Section 3 as a code-led implementation narrative

**Files:**
- Modify: `docs/course-report.md` under `## 3. 实现思路`

- [ ] **Step 1: Keep the existing opening layer explanation and add a Board code excerpt**

Insert a shortened, verbatim local excerpt equivalent to:

```python
while self.in_bounds(row, col):
    cell = self.arrow_grid[row][col]
    if cell is None:
        return None
    if cell in ARROWS:
        return row, col
    row += row_delta
    col += col_delta

blocker = self._find_blocker(row, col)
if blocker is not None:
    return MoveResult(False, row, col, cell, "blocked", blocker)
self.arrow_grid[row][col] = "."
return MoveResult(True, row, col, cell, "clear")
```

Explain directly below it that `None` is a puzzle edge, `.` is traversable, and immediate mutation prevents a flying sprite from being clicked twice.

- [ ] **Step 2: Add the Game-to-animation excerpt without duplicating the whole state machine**

Use the current branch of `Game.click()` that creates `FlyOutAnimation` on `"clear"`. Explain that this sequence deliberately mutates Board first and queues visual feedback second, so visual duration never gates a later legal click. Mention blocker-driven collision, heart loss, and star reveal in prose only where the current source confirms them.

- [ ] **Step 3: Add a “提示系统：给建议但不替玩家操作” subsection**

Use the following short excerpts and explain the one-way flow “button → Game query → UI state → draw”:

```python
elif ui.hint_rect().collidepoint(event.pos):
    ui.hint_cell = game.hint()

def hint(self) -> tuple[int, int] | None:
    if self.state is not GameState.PLAYING:
        return None
    return self.board.first_clearable_arrow()
```

Then include a compact UI guard showing that stale hints disappear after a cell is cleared:

```python
if self.hint_cell is None or self.game.state is not GameState.PLAYING:
    return
row, col = self.hint_cell
if self.game.board.get_cell(row, col) not in {"U", "D", "L", "R"}:
    return
```

- [ ] **Step 4: Add a “飞行 UI 判定与绘制” subsection**

Show the current cell-to-pixel mapping and explain why animation owns a logical `offset_cells`, while UI owns `layout.cell_size`:

```python
offset_row, offset_col = animation.offset_cells
center = (
    rect.centerx + round(offset_col * self.layout.cell_size),
    rect.centery + round(offset_row * self.layout.cell_size),
)
```

In prose, describe the wind-up / eased-flight split and the trail as visual concerns; make clear that none of it changes Board state.

- [ ] **Step 5: Add the compact iteration record at the end of Section 3**

Add the heading `### 一次挫折与改进：箭头“飞出”却没有飞远` and four bold labels in this exact order: `现象`、`定位`、`修改`、`回归测试`. State only confirmed facts: the initial fixed two-cell movement looked like abrupt disappearance during play; the correction uses direction-specific distances that leave the viewport; animation tests assert direction/phase/distance behavior.

### Task 3: Refresh validation and preserve submission constraints

**Files:**
- Modify: `docs/course-report.md` under `## 5. 测试结果` and `## 7. 心得体会草稿`
- Inspect: `docs/course-report.md`

- [ ] **Step 1: Update Section 5 only with the new full-suite count**

Replace the old `157 passed` phrase with the exact count obtained in Task 1. Keep the existing T01–T12 row identifiers, order, and PSP table unchanged.

- [ ] **Step 2: Revise the reflection to refer back to the concrete fly-out and hint design decisions**

Keep the existing first-person tone. Replace generic claims with the verified example: visual playtesting exposed the two-cell fly-out problem, a regression test was added, and the separation of Board/Game/UI made the fix local. Mention that a hint is read-only and must validate its target at draw time, which avoids stale highlighting after an immediate clear.

- [ ] **Step 3: Validate Markdown structure and links**

Run:

```powershell
rg -n "^## [1-7]\. |^## 作业信息|^## 6\. PSP" docs/course-report.md
rg -n "assets/runtime-(start|gameplay|moon-kitty|result|failed|paused)\.png" docs/course-report.md
```

Expected: exactly one `作业信息` heading, exactly one heading for each original section 1–7 in order, and all six pre-existing runtime image paths remain present. Do not edit the course-information placeholders or any PSP actual-hour cell.

- [ ] **Step 4: Commit the documentation-only change**

```powershell
git add docs/course-report.md docs/superpowers/specs/2026-09-22-course-blog-design.md docs/superpowers/plans/2026-09-22-course-blog-code-narrative.md
git commit -m "docs: enrich course blog implementation narrative"
```

Commit only these three documentation files; leave existing source, asset, and unrelated documentation changes untouched.

## Self-review

- Spec coverage: Task 2 supplies representative source excerpts, a hint explanation, fly-out UI mapping, and the required setback/improvement record. Task 3 preserves numbering, old PSP cells, images, and refreshes the test evidence.
- Placeholder scan: no implementation placeholder remains; the plan specifies exact headings, source excerpts, commands, and scope.
- Type consistency: every named identifier matches the current source: `Board._find_blocker`, `Board.first_clearable_arrow`, `Game.hint`, `FlyOutAnimation.offset_cells`, `UI.hint_cell`, and `UI.hint_rect`.
