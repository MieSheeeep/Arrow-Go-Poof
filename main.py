"""Runnable Pygame entry point for the playable MVP."""
import pygame

from src.game import Game, GameState
from src.levels import (
    LEVEL_FACTORIES,
    LEVEL_NAMES,
    LEVEL_STAR_THRESHOLDS,
    LEVEL_TIME_LIMITS,
    create_random_level_board,
)
from src.sound import SoundManager
from src.ui import UI, WINDOW_SIZE


def process_event(event: pygame.event.Event, game: Game, ui: UI, sound=None) -> bool:
    if event.type == pygame.QUIT:
        return False
    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
        game.load_custom_board(create_random_level_board())
        ui.hint_cell = None
        return True
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
        elif ui.hint_rect().collidepoint(event.pos):
            ui.hint_cell = game.hint()
        elif ui.undo_rect().collidepoint(event.pos):
            ui.hint_cell = None
            game.undo()
        elif ui.auto_rect().collidepoint(event.pos):
            game.auto_mode = not game.auto_mode
        elif ui.save_rect().collidepoint(event.pos):
            game.save("savegame.json")
        elif ui.load_rect().collidepoint(event.pos):
            try:
                game.load("savegame.json")
            except FileNotFoundError:
                pass
            ui.hint_cell = None
        else:
            cell = ui.cell_at(event.pos)
            if cell is not None:
                ui.hint_cell = None
                result = game.click(*cell)
                if sound is not None and result is not None:
                    if game.state is GameState.CLEARED:
                        sound.play("clear")
                    elif game.state is GameState.FAILED:
                        sound.play("fail")
                    elif result.reason == "blocked":
                        sound.play("collide")
                    elif result.reason == "clear":
                        sound.play("fly")
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
    sound = SoundManager()
    try:
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("一箭又一箭")
        game = Game(
            LEVEL_FACTORIES,
            start_in_menu=True,
            level_names=LEVEL_NAMES,
            star_thresholds=LEVEL_STAR_THRESHOLDS,
            time_limits=LEVEL_TIME_LIMITS,
        )
        ui = UI(screen, game)
        clock = pygame.time.Clock()
        running = True

        while running:
            delta_time = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if not process_event(event, game, ui, sound):
                    running = False

            game.update(delta_time)
            ui.draw()
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
