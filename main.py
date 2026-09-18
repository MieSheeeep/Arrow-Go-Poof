"""Minimal development entry point for the first project iteration."""
from src.levels import create_sample_board

def main() -> None:
    board = create_sample_board()
    print(f"一箭又一箭：示例关卡已加载，剩余箭头 {board.remaining_arrows()} 个")

if __name__ == "__main__":
    main()
