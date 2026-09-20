"""Runnable Pygame entry point for the playable MVP."""
import pygame

from src.game import Game, GameState
from src.levels import LEVEL_FACTORIES, LEVEL_NAMES, LEVEL_STAR_THRESHOLDS
from src.ui import UI, WINDOW_SIZE


def process_event(event: pygame.event.Event, game: Game, ui: UI) -> bool:
    if event.type == pygame.QUIT:
        return False
    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return True

    if game.state is GameState.START:
        if ui.start_rect().collidepoint(event.pos):
            game.start()
    elif game.state in {GameState.CLEARED, GameState.FAILED}:
        if ui.result_primary_rect().collidepoint(event.pos):
            if game.state is GameState.FAILED:
                game.restart()
            elif game.has_next_level:
                game.next_level()
            else:
                game.restart_campaign()
        elif (
            game.state is GameState.CLEARED
            and ui.result_retry_rect().collidepoint(event.pos)
        ):
            game.restart()
        elif ui.result_menu_rect().collidepoint(event.pos):
            game.return_to_menu()
    elif game.state is GameState.PLAYING:
        if ui.pause_rect().collidepoint(event.pos):
            game.pause()
        else:
            cell = ui.cell_at(event.pos)
            if cell is not None:
                game.click(*cell)
    elif game.state is GameState.PAUSED:
        if ui.pause_resume_rect().collidepoint(event.pos):
            game.resume()
        elif ui.pause_restart_rect().collidepoint(event.pos):
            game.restart()
        elif ui.pause_menu_rect().collidepoint(event.pos):
            game.return_to_menu()
    return True


def main() -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("一箭又一箭")
        game = Game(
            LEVEL_FACTORIES,
            start_in_menu=True,
            level_names=LEVEL_NAMES,
            star_thresholds=LEVEL_STAR_THRESHOLDS,
        )
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
