# Arrow-Go-Poof（一箭又一箭）

基于 Python 与 Pygame 的桌面箭头消除解谜游戏。

当前实现包含可直接游玩的 Pygame MVP：树形示例关卡、鼠标点击、三点生命值、成功飞出动画、阻挡撞击回退反馈、通关/失败面板和重新开始。计时、星级、Combo、音效和多关卡选择仍属于后续迭代。

## 环境

- Python 3.10+

```bash
python -m pip install -r requirements.txt
```

## 测试

```bash
python -m pytest -v
```

## 运行游戏

```bash
python main.py
```

窗口固定为 1200×800。关闭窗口退出；通关或失败后点击结果面板中的 `RESTART` 重新开始。
