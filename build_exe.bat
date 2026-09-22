@echo off
chcp 65001 >nul
REM 一箭又一箭 打包脚本：用 PyInstaller 生成单文件可执行程序。
REM 产物输出到 dist\ArrowGoPoof.exe，双击即可运行（无需安装 Python）。

REM 1. 安装打包工具（已安装会自动跳过）
python -m pip install pyinstaller

REM 2. 打包说明：
REM    --windowed  不弹出控制台窗口（纯图形界面）
REM    --onefile   合并为单个 exe 文件
REM    --add-data  把 assets 资源目录一并打入（Windows 用分号分隔）
pyinstaller --noconfirm --clean --onefile --windowed ^
  --name ArrowGoPoof ^
  --add-data "assets;assets" ^
  main.py

echo.
echo 打包完成：dist\ArrowGoPoof.exe
pause
