"""Runnable Pygame entry point for the playable MVP."""
import pygame

from src.game import Game, GameState
from src.levels import create_tree_board
from src.ui import UI, WINDOW_SIZE


def process_event(event: pygame.event.Event, game: Game, ui: UI) -> bool:
    if event.type == pygame.QUIT:
        return False
    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return True

    if game.state in {GameState.CLEARED, GameState.FAILED}:
        if ui.restart_rect().collidepoint(event.pos):
            game.restart()
    elif game.state is GameState.PLAYING:
        cell = ui.cell_at(event.pos)
        if cell is not None:
            game.click(*cell)
    return True


def main() -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("一箭又一箭")
        game = Game(create_tree_board)
        ui = UI(screen, game)
        clock = pygame.time.Clock()
        running = True

        while running:
            delta_time = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if not process_event(event, game, ui):
                    running = False

            game.update(delta_time)
            ui.draw()
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
