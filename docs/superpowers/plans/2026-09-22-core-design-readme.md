# Core Design README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the image-heavy feature list with a concise README centered on gameplay rules and the project’s core design.

**Architecture:** `README.md` will be the entry document for running and understanding the repository, not a copy of the course blog. It will state the Board/Game/Animation/UI responsibilities and the important state rules without screenshots or exhaustive UI descriptions.

**Tech Stack:** Markdown, Python 3, Pygame, pytest.

---

### Task 1: Rewrite the README around the verified design

**Files:**
- Modify: `README.md`
- Inspect: `src/board.py`, `src/game.py`, `src/animation.py`, `src/ui.py`, `requirements.txt`

- [ ] **Step 1: Replace the title and image block with a concise overview**

Use the title `# Arrow-Go-Poof（一箭又一箭）` and a two-sentence Chinese summary. Do not include Markdown or HTML image tags.

- [ ] **Step 2: Add quick-start commands**

Include exactly these commands:

```bash
python -m pip install -r requirements.txt
python main.py
python -m pytest -q
python -m compileall -q main.py src tests
```

- [ ] **Step 3: Add the core rule and architecture sections**

Document these facts without implementation-sized code blocks: `None` ends an irregular puzzle region, `.` is traversable, the first arrow is the blocker, success immediately writes `.`, and Board/Game/Animation/UI have separate responsibilities. State that hints call the same clearability rule and that fly-out animation does not gate input.

- [ ] **Step 4: Add score and project-layout sections**

State `5 × N × (N + 1)` as the perfect-combo ceiling and 85% / 60% score thresholds. List only `main.py`, `src/`, `tests/`, `assets/`, and `docs/`, then link the three existing project documents.

### Task 2: Validate and deliver the documentation change

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Check content constraints**

Run:

```powershell
rg -n "!\[|<img|时间与失误|85%|60%|Board|Game|Animation|UI" README.md
```

Expected: no image syntax or old time/mistake star rule; all four architecture names and both score thresholds are present.

- [ ] **Step 2: Run project verification**

Run:

```powershell
python -m pytest -q
python -m compileall -q main.py src tests
git diff --check
```

Expected: tests and compilation succeed; no whitespace errors.

- [ ] **Step 3: Commit, push, and merge**

```powershell
git add README.md docs/superpowers/specs/2026-09-22-core-design-readme-design.md docs/superpowers/plans/2026-09-22-core-design-readme.md
git commit -m "docs: rewrite readme around core design"
git push -u origin codex/p1-game-completion
```

Fast-forward `main` only after confirming it is an ancestor of `codex/p1-game-completion`; rerun the test suite for the resulting main commit, then push `main`. Do not stage `docs/Blog.md` or `docs/assets/cover.png`.

## Self-review

- Spec coverage: Task 1 maps every requested README section and accuracy rule to a concrete edit; Task 2 checks images, stale star wording, testing, and delivery.
- Placeholder scan: no incomplete behavior or unspecified threshold remains.
- Consistency: `Board`, `Game`, `Animation`, `UI`, `None`, `.`, 85%, and 60% match current source and the approved design.
