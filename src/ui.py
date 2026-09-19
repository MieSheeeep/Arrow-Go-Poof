"""Pygame layout, rendering, and input translation for the playable MVP."""

from __future__ import annotations

import pygame

from src.game import Game, GameState


WINDOW_SIZE = (1200, 800)
BACKGROUND = (126, 190, 232)
HUD_COLOR = (39, 77, 119)
ARROW_TILE = (235, 237, 235)
ARROW_COLOR = (86, 102, 126)
ERROR_TILE = (238, 112, 112)
ERROR_ARROW = (128, 38, 38)
HOVER_COLOR = (102, 213, 255)


class GridLayout:
    def __init__(self, origin: tuple[int, int], cell_size: int) -> None:
        if cell_size <= 0:
            raise ValueError("cell_size must be positive")
        self.origin = origin
        self.cell_size = cell_size

    def cell_at(
        self,
        position: tuple[int, int],
        rows: int,
        cols: int,
    ) -> tuple[int, int] | None:
        x, y = position
        local_x = x - self.origin[0]
        local_y = y - self.origin[1]
        if local_x < 0 or local_y < 0:
            return None
        col = local_x // self.cell_size
        row = local_y // self.cell_size
        if row >= rows or col >= cols:
            return None
        return row, col

    def cell_rect(self, row: int, col: int) -> pygame.Rect:
        x = self.origin[0] + col * self.cell_size
        y = self.origin[1] + row * self.cell_size
        return pygame.Rect(x, y, self.cell_size, self.cell_size)


class UI:
    def __init__(self, screen: pygame.Surface, game: Game) -> None:
        self.screen = screen
        self.game = game
        self.layout = GridLayout(origin=(260, 130), cell_size=48)
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)

    def cell_at(self, position: tuple[int, int]) -> tuple[int, int] | None:
        return self.layout.cell_at(position, self.game.board.rows, self.game.board.cols)

    def restart_rect(self) -> pygame.Rect:
        return pygame.Rect(490, 505, 220, 52)

    def draw(self) -> None:
        self._draw_background()
        self._draw_board()
        self._draw_animations()
        self._draw_hud()
        if self.game.state in {GameState.CLEARED, GameState.FAILED}:
            self._draw_result_panel()

    def _draw_background(self) -> None:
        self.screen.fill(BACKGROUND)
        pygame.draw.rect(self.screen, (102, 164, 199), (0, 350, 1200, 450))
        pygame.draw.polygon(
            self.screen,
            (78, 142, 177),
            [(0, 410), (190, 270), (390, 410)],
        )
        pygame.draw.polygon(
            self.screen,
            (92, 155, 186),
            [(760, 420), (970, 250), (1200, 420)],
        )
        pygame.draw.rect(self.screen, (104, 170, 84), (0, 560, 1200, 240))
        for x, y in [(90, 95), (1030, 110), (180, 250), (950, 260)]:
            pygame.draw.rect(self.screen, (245, 247, 238), (x, y, 92, 18))
            pygame.draw.rect(self.screen, (245, 247, 238), (x + 24, y - 14, 58, 18))

    def _draw_board(self) -> None:
        hover_cell = self.cell_at(pygame.mouse.get_pos())
        active_cells = {
            (animation.row, animation.col) for animation in self.game.animations
        }
        for row in range(self.game.board.rows):
            for col in range(self.game.board.cols):
                color_name = self.game.board.color_grid[row][col]
                if color_name is None:
                    continue

                rect = self.layout.cell_rect(row, col)
                cell = self.game.board.arrow_grid[row][col]
                if color_name == "trunk":
                    fill = (142, 91, 55)
                elif color_name == "grass":
                    fill = (86, 157, 73)
                else:
                    fill = (105, 181, 78)

                has_arrow = cell in {"U", "D", "L", "R"}
                is_active = (row, col) in active_cells
                if has_arrow and not is_active:
                    fill = ERROR_TILE if (row, col) in self.game.error_cells else ARROW_TILE
                pygame.draw.rect(self.screen, fill, rect)
                pygame.draw.rect(self.screen, (67, 93, 112), rect, 1)

                if has_arrow and not is_active:
                    arrow_color = (
                        ERROR_ARROW
                        if (row, col) in self.game.error_cells
                        else ARROW_COLOR
                    )
                    self._draw_arrow(rect, cell, arrow_color)
                if hover_cell == (row, col):
                    pygame.draw.rect(self.screen, HOVER_COLOR, rect, 2)

    def _draw_animations(self) -> None:
        for animation in self.game.animations:
            rect = self.layout.cell_rect(animation.row, animation.col)
            offset_row, offset_col = animation.offset_cells
            rect = rect.move(
                round(offset_col * self.layout.cell_size),
                round(offset_row * self.layout.cell_size),
            )
            is_error = animation.color_state == "error"
            pygame.draw.rect(self.screen, ERROR_TILE if is_error else ARROW_TILE, rect)
            self._draw_arrow(rect, animation.direction, ERROR_ARROW if is_error else ARROW_COLOR)

    def _draw_arrow(
        self,
        rect: pygame.Rect,
        direction: str,
        color: tuple[int, int, int],
    ) -> None:
        center = rect.center
        arm = self.layout.cell_size // 3
        points = {
            "U": [
                (center[0], center[1] - arm),
                (center[0] - arm // 2, center[1]),
                (center[0] - 5, center[1]),
                (center[0] - 5, center[1] + arm),
                (center[0] + 5, center[1] + arm),
                (center[0] + 5, center[1]),
                (center[0] + arm // 2, center[1]),
            ],
            "D": [
                (center[0], center[1] + arm),
                (center[0] - arm // 2, center[1]),
                (center[0] - 5, center[1]),
                (center[0] - 5, center[1] - arm),
                (center[0] + 5, center[1] - arm),
                (center[0] + 5, center[1]),
                (center[0] + arm // 2, center[1]),
            ],
            "L": [
                (center[0] - arm, center[1]),
                (center[0], center[1] - arm // 2),
                (center[0], center[1] - 5),
                (center[0] + arm, center[1] - 5),
                (center[0] + arm, center[1] + 5),
                (center[0], center[1] + 5),
                (center[0], center[1] + arm // 2),
            ],
            "R": [
                (center[0] + arm, center[1]),
                (center[0], center[1] - arm // 2),
                (center[0], center[1] - 5),
                (center[0] - arm, center[1] - 5),
                (center[0] - arm, center[1] + 5),
                (center[0], center[1] + 5),
                (center[0], center[1] + arm // 2),
            ],
        }
        pygame.draw.polygon(self.screen, color, points[direction])

    def _draw_hud(self) -> None:
        pygame.draw.rect(self.screen, HUD_COLOR, (220, 22, 760, 62), border_radius=12)
        text = (
            f"LEVEL 01    LIVES {self.game.lives}    "
            f"MISTAKES {self.game.mistakes}    ARROWS {self.game.board.remaining_arrows()}"
        )
        surface = self.font.render(text, True, (250, 230, 133))
        self.screen.blit(surface, (250, 42))

    def _draw_result_panel(self) -> None:
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((12, 28, 54, 120))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(365, 230, 470, 360)
        pygame.draw.rect(self.screen, HUD_COLOR, panel, border_radius=16)
        title = "LEVEL CLEAR" if self.game.state is GameState.CLEARED else "TRY AGAIN"
        title_surface = self.font.render(title, True, (250, 230, 133))
        self.screen.blit(title_surface, title_surface.get_rect(center=(600, 310)))

        stats = self.small_font.render(
            f"Mistakes: {self.game.mistakes}", True, (240, 245, 250)
        )
        self.screen.blit(stats, stats.get_rect(center=(600, 370)))

        button = self.restart_rect()
        pygame.draw.rect(self.screen, (105, 181, 78), button, border_radius=8)
        label = self.small_font.render("RESTART", True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=button.center))
