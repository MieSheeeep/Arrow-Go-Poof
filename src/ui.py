"""Pygame layout, rendering, and input translation for the playable MVP."""

from __future__ import annotations

from pathlib import Path

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
MENU_BACKGROUND_PATH = Path(__file__).resolve().parent.parent / "assets" / "menu-background.png"
MENU_PANEL_COLOR = (75, 48, 31)
# The dark desk mat in the supplied work-table illustration. Puzzle cells stay
# inside it so the board feels like a bead-art project on the work surface.
WORK_MAT_RECT = pygame.Rect(180, 160, 840, 580)
COLOR_MAP = {
    "leaf_light": (138, 205, 90),
    "leaf": (105, 181, 78),
    "trunk": (142, 91, 55),
    "grass": (86, 157, 73),
    "flower": (246, 193, 72),
    "petal_light": (255, 171, 198),
    "petal": (234, 104, 144),
    "center": (247, 190, 64),
    "stem": (94, 145, 63),
    "sun": (252, 190, 55),
    "ray": (255, 221, 104),
    "sky": (126, 190, 232),
    "ball_outline": (40, 43, 45),
    "ball_highlight": (231, 131, 52),
    "ball_red": (192, 83, 48),
    "ball_shine": (235, 251, 247),
    "ball_white": (255, 255, 255),
    "ball_gray": (188, 192, 188),
}


class GridLayout:
    def __init__(self, origin: tuple[int, int], cell_size: int) -> None:
        if type(cell_size) is not int or not 0 < cell_size <= min(WINDOW_SIZE):
            raise ValueError("cell_size must be an integer within the window size")
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
        self.title_font = pygame.font.Font(None, 56)
        self.menu_background = pygame.transform.smoothscale(
            # Keep the source surface unconverted so UI can also be rendered
            # onto headless test surfaces before a display mode exists.
            pygame.image.load(MENU_BACKGROUND_PATH), WINDOW_SIZE
        )
        self._refresh_layout()

    def cell_at(self, position: tuple[int, int]) -> tuple[int, int] | None:
        self._refresh_layout()
        return self.layout.cell_at(position, self.game.board.rows, self.game.board.cols)

    def _refresh_layout(self) -> None:
        """Fit the current picture level inside the illustrated desk mat."""
        cell_size = min(
            42,
            WORK_MAT_RECT.height // self.game.board.rows,
            (WORK_MAT_RECT.width - 36) // self.game.board.cols,
        )
        board_width = self.game.board.cols * cell_size
        board_height = self.game.board.rows * cell_size
        origin_x = WORK_MAT_RECT.x + (WORK_MAT_RECT.width - board_width) // 2
        origin_y = WORK_MAT_RECT.y + (WORK_MAT_RECT.height - board_height) // 2
        self.layout = GridLayout(origin=(origin_x, origin_y), cell_size=cell_size)

    def restart_rect(self) -> pygame.Rect:
        return self.result_action_rect()

    def start_rect(self) -> pygame.Rect:
        rect = pygame.Rect(0, 0, 260, 64)
        rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2 + 115)
        return rect

    def result_action_rect(self) -> pygame.Rect:
        rect = pygame.Rect(0, 0, 220, 52)
        rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2 + 105)
        return rect

    def draw(self) -> None:
        if self.game.state is GameState.START:
            self._draw_menu_background()
            self._draw_start_panel()
            return
        self._draw_background()
        self._draw_board()
        self._draw_animations()
        self._draw_hud()
        if self.game.state in {GameState.CLEARED, GameState.FAILED}:
            self._draw_result_panel()

    def _draw_start_panel(self) -> None:
        panel = pygame.Rect(150, 92, 900, 228)
        pygame.draw.rect(self.screen, MENU_PANEL_COLOR, panel, border_radius=18)
        pygame.draw.rect(
            self.screen,
            (145, 95, 55),
            (panel.left, panel.top, panel.width, 11),
            border_radius=18,
        )

        # A tiny board motif makes this feel like a real main menu while
        # keeping START GAME as the only actionable control.
        for rect, direction, color in (
            (pygame.Rect(218, 165, 44, 44), "U", (255, 221, 104)),
            (pygame.Rect(264, 210, 44, 44), "R", (255, 171, 198)),
            (pygame.Rect(890, 165, 44, 44), "D", (138, 205, 90)),
            (pygame.Rect(936, 210, 44, 44), "L", (247, 190, 64)),
        ):
            pygame.draw.rect(self.screen, ARROW_TILE, rect, border_radius=7)
            self._draw_arrow(rect, direction, color)

        title = self.title_font.render("ARROW GO POOF", True, (250, 230, 133))
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + 66)))
        subtitle = self.small_font.render(
            "Follow the arrows. Reveal the picture.", True, (240, 245, 250)
        )
        self.screen.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.top + 126)))
        details = self.small_font.render(
            f"{self.game.level_count} pixel puzzles  |  {self.game.max_lives} mistakes per level",
            True,
            (240, 245, 250),
        )
        self.screen.blit(details, details.get_rect(center=(panel.centerx, panel.top + 166)))

        button = self.start_rect()
        pygame.draw.rect(self.screen, (105, 181, 78), button, border_radius=8)
        pygame.draw.rect(self.screen, (168, 224, 131), button, 2, border_radius=8)
        label = self.small_font.render("START GAME", True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=button.center))

    def _draw_menu_background(self) -> None:
        """Draw the generated work desk behind the one-button main menu."""
        self.screen.blit(self.menu_background, (0, 0))

    def _draw_background(self) -> None:
        """Keep gameplay and the start screen on the same craft desk."""
        self.screen.blit(self.menu_background, (0, 0))

    def _draw_board(self) -> None:
        self._refresh_layout()
        try:
            mouse_position = pygame.mouse.get_pos()
        except pygame.error:
            # Rendering unit tests do not create a video device; they simply
            # have no hovered cell rather than needing one.
            mouse_position = (-1, -1)
        hover_cell = self.cell_at(mouse_position)
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
                fill = COLOR_MAP.get(color_name, COLOR_MAP["leaf"])

                has_arrow = cell in {"U", "D", "L", "R"}
                is_active = (row, col) in active_cells
                if has_arrow and not is_active:
                    fill = ERROR_TILE if (row, col) in self.game.error_cells else ARROW_TILE
                self._draw_tile(
                    rect,
                    fill,
                    is_arrow=has_arrow,
                    is_error=(row, col) in self.game.error_cells,
                    is_hovered=hover_cell == (row, col),
                )

                if has_arrow and not is_active:
                    arrow_color = (
                        ERROR_ARROW
                        if (row, col) in self.game.error_cells
                        else ARROW_COLOR
                    )
                    self._draw_arrow(rect, cell, arrow_color)

    def _draw_animations(self) -> None:
        for animation in self.game.animations:
            rect = self.layout.cell_rect(animation.row, animation.col)
            offset_row, offset_col = animation.offset_cells
            rect = rect.move(
                round(offset_col * self.layout.cell_size),
                round(offset_row * self.layout.cell_size),
            )
            is_error = animation.color_state == "error"
            self._draw_tile(
                rect,
                ERROR_TILE if is_error else ARROW_TILE,
                is_arrow=True,
                is_error=is_error,
            )
            self._draw_arrow(rect, animation.direction, ERROR_ARROW if is_error else ARROW_COLOR)

    def _draw_tile(
        self,
        rect: pygame.Rect,
        fill: tuple[int, int, int],
        *,
        is_arrow: bool,
        is_error: bool = False,
        is_hovered: bool = False,
    ) -> None:
        """Draw a soft, rounded bead card without hiding the desk texture."""
        radius = max(6, self.layout.cell_size // 5)

        # A compact shadow gives each bead/card depth. It begins below-right
        # of the cell, leaving the tile's rounded top-left corner transparent.
        shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            shadow,
            (15, 24, 31, 76),
            shadow.get_rect(),
            border_radius=radius,
        )
        self.screen.blit(shadow, rect.move(2, 3).topleft)

        tile = pygame.Surface(rect.size, pygame.SRCALPHA)
        alpha = 156 if is_hovered else (218 if is_arrow else 196)
        border = HOVER_COLOR if is_hovered else ((178, 70, 70) if is_error else (255, 255, 255))
        border_alpha = 235 if is_hovered else (155 if is_arrow else 92)
        pygame.draw.rect(
            tile,
            (*fill, alpha),
            tile.get_rect(),
            border_radius=radius,
        )
        pygame.draw.rect(
            tile,
            (*border, border_alpha),
            tile.get_rect(),
            width=3 if is_hovered else 1,
            border_radius=radius,
        )
        pygame.draw.line(
            tile,
            (255, 255, 255, 98 if is_arrow else 62),
            (radius, 2),
            (rect.width - radius, 2),
            width=1,
        )
        self.screen.blit(tile, rect.topleft)

    def _draw_arrow(
        self,
        rect: pygame.Rect,
        direction: str,
        color: tuple[int, int, int],
    ) -> None:
        center = rect.center
        arm = self.layout.cell_size // 3
        shaft = max(4, self.layout.cell_size // 7)
        points = {
            "U": [
                (center[0], center[1] - arm),
                (center[0] - arm // 2, center[1]),
                (center[0] - shaft, center[1]),
                (center[0] - shaft, center[1] + arm),
                (center[0] + shaft, center[1] + arm),
                (center[0] + shaft, center[1]),
                (center[0] + arm // 2, center[1]),
            ],
            "D": [
                (center[0], center[1] + arm),
                (center[0] - arm // 2, center[1]),
                (center[0] - shaft, center[1]),
                (center[0] - shaft, center[1] - arm),
                (center[0] + shaft, center[1] - arm),
                (center[0] + shaft, center[1]),
                (center[0] + arm // 2, center[1]),
            ],
            "L": [
                (center[0] - arm, center[1]),
                (center[0], center[1] - arm // 2),
                (center[0], center[1] - shaft),
                (center[0] + arm, center[1] - shaft),
                (center[0] + arm, center[1] + shaft),
                (center[0], center[1] + shaft),
                (center[0], center[1] + arm // 2),
            ],
            "R": [
                (center[0] + arm, center[1]),
                (center[0], center[1] - arm // 2),
                (center[0], center[1] - shaft),
                (center[0] - arm, center[1] - shaft),
                (center[0] - arm, center[1] + shaft),
                (center[0], center[1] + shaft),
                (center[0], center[1] + arm // 2),
            ],
        }
        shadow_points = [(x + 1, y + 2) for x, y in points[direction]]
        pygame.draw.polygon(self.screen, (35, 48, 58), shadow_points)
        pygame.draw.polygon(self.screen, color, points[direction])

    def _draw_hud(self) -> None:
        pygame.draw.rect(self.screen, HUD_COLOR, (220, 22, 760, 62), border_radius=12)
        text = (
            f"LEVEL {self.game.level_number:02d}/{self.game.level_count} {self.game.level_name}    "
            f"LIVES {self.game.lives}    "
            f"MISTAKES {self.game.mistakes}    ARROWS {self.game.board.remaining_arrows()}"
        )
        surface = self.font.render(text, True, (250, 230, 133))
        self.screen.blit(surface, (250, 42))

    def _draw_result_panel(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((12, 28, 54, 120))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 470, 360)
        panel.center = self.screen.get_rect().center
        pygame.draw.rect(self.screen, HUD_COLOR, panel, border_radius=16)
        if self.game.state is GameState.FAILED:
            title = "TRY AGAIN"
        elif self.game.has_next_level:
            title = "LEVEL CLEAR"
        else:
            title = "ALL CLEAR"
        title_surface = self.font.render(title, True, (250, 230, 133))
        self.screen.blit(
            title_surface,
            title_surface.get_rect(center=(panel.centerx, panel.top + 80)),
        )

        stats = self.small_font.render(
            f"Mistakes: {self.game.mistakes}", True, (240, 245, 250)
        )
        self.screen.blit(
            stats,
            stats.get_rect(center=(panel.centerx, panel.top + 140)),
        )

        button = self.result_action_rect()
        pygame.draw.rect(self.screen, (105, 181, 78), button, border_radius=8)
        if self.game.state is GameState.FAILED:
            button_text = "RESTART LEVEL"
        elif self.game.has_next_level:
            button_text = "NEXT LEVEL"
        else:
            button_text = "RESTART GAME"
        label = self.small_font.render(button_text, True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=button.center))
