"""Pygame layout, rendering, and input translation for the playable MVP."""

from __future__ import annotations

import math
from pathlib import Path

import pygame

from src.game import Game, GameState


WINDOW_SIZE = (1200, 800)
BACKGROUND = (126, 190, 232)
HUD_COLOR = (39, 77, 119)
# Sampled from the dark work mat at the centre of the supplied desk artwork.
# Covered cells therefore hide the pixel picture instead of previewing it.
WORK_MAT_COLOR = (54, 56, 68)
ARROW_TILE = WORK_MAT_COLOR
ARROW_COLOR = (218, 240, 246)
# Keep the covered picture as a faint colour hint; the dark mat still masks
# enough detail that the silhouette cannot be read before it is cleared.
ARROW_CARD_ALPHA = 140
HOVERED_ARROW_CARD_ALPHA = 105
ERROR_TILE = (238, 112, 112)
ERROR_ARROW = (128, 38, 38)
HOVER_COLOR = (102, 213, 255)
MENU_BACKGROUND_PATH = Path(__file__).resolve().parent.parent / "assets" / "menu-background.png"
UI_ASSET_DIR = Path(__file__).resolve().parent.parent / "assets" / "ui"
BUTTON_STATES_PATH = UI_ASSET_DIR / "button-states.png"
HEARTS_PATH = UI_ASSET_DIR / "hearts.png"
PAUSE_BUTTON_PATH = UI_ASSET_DIR / "pause-button.png"
PAUSE_PANEL_PATH = UI_ASSET_DIR / "pause-panel.png"
RATING_STARS_PATH = UI_ASSET_DIR / "rating-stars.png"
TOP_STATUS_BAR_PATH = UI_ASSET_DIR / "top-status-bar.png"
MENU_PANEL_COLOR = (75, 48, 31)
# The dark desk mat in the supplied work-table illustration. Puzzle cells stay
# inside it so the board feels like a bead-art project on the work surface.
WORK_MAT_RECT = pygame.Rect(180, 160, 840, 580)


def format_elapsed_time(seconds: float) -> str:
    """Format a non-negative level duration as MM:SS.hh."""
    minutes, remaining = divmod(seconds, 60.0)
    return f"{int(minutes):02d}:{remaining:05.2f}"


def rating_star_points(
    center: tuple[int, int], *, outer_radius: int, inner_radius: int
) -> list[tuple[int, int]]:
    """Return the ten alternating vertices of a font-independent star."""
    center_x, center_y = center
    points = []
    for index in range(10):
        radius = outer_radius if index % 2 == 0 else inner_radius
        angle = -math.pi / 2 + index * math.pi / 5
        points.append(
            (
                round(center_x + math.cos(angle) * radius),
                round(center_y + math.sin(angle) * radius),
            )
        )
    return points


def remove_isolated_artifacts(
    surface: pygame.Surface, *, minimum_pixels: int
) -> pygame.Surface:
    """Erase tiny disconnected image fragments while preserving artwork colours."""
    source_mask = pygame.mask.from_surface(surface)
    kept_mask = pygame.mask.Mask(surface.get_size())
    for component in source_mask.connected_components(minimum=minimum_pixels):
        kept_mask.draw(component, (0, 0))
    coverage = kept_mask.to_surface(
        setcolor=(255, 255, 255, 255),
        unsetcolor=(0, 0, 0, 0),
    )
    cleaned = surface.copy()
    cleaned.blit(coverage, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return cleaned


def _load_ui_asset(
    path: Path,
    *,
    crop: pygame.Rect | None = None,
    black_is_transparent: bool = False,
) -> pygame.Surface:
    """Load one supplied UI illustration, optionally crop and trim it."""
    surface = pygame.image.load(path)
    if crop is not None:
        surface = surface.subsurface(crop).copy()
    if black_is_transparent:
        surface.set_colorkey((0, 0, 0))
        surface = remove_isolated_artifacts(surface, minimum_pixels=200)
    bounds = surface.get_bounding_rect()
    return surface.subsurface(bounds).copy() if bounds.size != surface.get_size() else surface


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
    "sword_outline": (8, 40, 33),
    "sword_teal": (30, 140, 122),
    "sword_highlight": (60, 235, 206),
    "kitty_white": (250, 250, 250),
    "moon_gold": (228, 197, 84),
    "kitty_outline": (8, 8, 8),
    "moon_shadow": (209, 162, 56),
    "kitty_gray": (219, 219, 219),
    "kitty_bow": (196, 18, 23),
    "kitty_pink": (226, 176, 176),
    "apple_gold": (252, 164, 57),
    "apple_peach": (254, 201, 132),
    "apple_shadow": (182, 110, 73),
    "apple_light": (253, 231, 114),
    "apple_red": (154, 22, 56),
    "apple_purple": (176, 0, 106),
    "apple_white": (254, 254, 254),
    "apple_outline": (91, 32, 32),
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
        self.top_status_bar = pygame.transform.scale(
            _load_ui_asset(
                TOP_STATUS_BAR_PATH,
                crop=pygame.Rect(35, 210, 2105, 445),
                black_is_transparent=True,
            ),
            (1200, 104),
        )
        self.button_skins = {
            "normal": _load_ui_asset(
                BUTTON_STATES_PATH, crop=pygame.Rect(50, 220, 650, 250)
            ),
            "hover": _load_ui_asset(
                BUTTON_STATES_PATH, crop=pygame.Rect(700, 220, 650, 250)
            ),
            "danger": _load_ui_asset(
                BUTTON_STATES_PATH, crop=pygame.Rect(1360, 220, 650, 250)
            ),
        }
        self.heart_full = pygame.transform.scale(
            _load_ui_asset(HEARTS_PATH, crop=pygame.Rect(250, 40, 750, 650)),
            (34, 30),
        )
        self.heart_empty = pygame.transform.scale(
            _load_ui_asset(HEARTS_PATH, crop=pygame.Rect(1110, 40, 800, 650)),
            (34, 30),
        )
        self.star_full = pygame.transform.scale(
            _load_ui_asset(RATING_STARS_PATH, crop=pygame.Rect(390, 60, 570, 550)),
            (34, 34),
        )
        self.star_empty = pygame.transform.scale(
            _load_ui_asset(RATING_STARS_PATH, crop=pygame.Rect(1120, 60, 620, 550)),
            (34, 34),
        )
        self.pause_icon = pygame.transform.scale(_load_ui_asset(PAUSE_BUTTON_PATH), (58, 58))
        self.pause_panel = pygame.transform.scale(_load_ui_asset(PAUSE_PANEL_PATH), (600, 554))
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
        return pygame.Rect(842, 34, 128, 38)

    def menu_rect(self) -> pygame.Rect:
        return pygame.Rect(230, 34, 112, 38)

    def pause_rect(self) -> pygame.Rect:
        return pygame.Rect(1035, 23, 62, 62)

    def pause_resume_rect(self) -> pygame.Rect:
        return pygame.Rect(445, 350, 310, 54)

    def pause_restart_rect(self) -> pygame.Rect:
        return pygame.Rect(445, 430, 310, 54)

    def pause_menu_rect(self) -> pygame.Rect:
        return pygame.Rect(445, 510, 310, 54)

    def result_primary_rect(self) -> pygame.Rect:
        return pygame.Rect(490, 505, 220, 48)

    def result_retry_rect(self) -> pygame.Rect:
        return pygame.Rect(490, 561, 220, 42)

    def result_menu_rect(self) -> pygame.Rect:
        return pygame.Rect(490, 611, 220, 42)

    def start_rect(self) -> pygame.Rect:
        rect = pygame.Rect(0, 0, 260, 64)
        rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2 + 115)
        return rect

    def result_action_rect(self) -> pygame.Rect:
        """Backward-compatible name for the primary result action."""
        return self.result_primary_rect()

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
        elif self.game.state is GameState.PAUSED:
            self._draw_pause_panel()

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
            f"{self.game.level_count} pixel puzzles  |  {self.game.max_lives} lives per level",
            True,
            (240, 245, 250),
        )
        self.screen.blit(details, details.get_rect(center=(panel.centerx, panel.top + 166)))

        button = self.start_rect()
        self._draw_action_button(button, "START GAME")

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
                picture_fill = COLOR_MAP.get(color_name, COLOR_MAP["leaf"])
                self._draw_picture_pixel(rect, picture_fill)

                has_arrow = cell in {"U", "D", "L", "R"}
                is_active = (row, col) in active_cells
                # Always paint the supplied pixel colour first. An uncleared
                # arrow then adds only a transparent work-mat card above it,
                # leaving a subtle preview rather than permanently darkening
                # the bead picture.
                if has_arrow and not is_active:
                    self._draw_tile(
                        rect,
                        ERROR_TILE if (row, col) in self.game.error_cells else ARROW_TILE,
                        is_arrow=True,
                        is_error=(row, col) in self.game.error_cells,
                        is_hovered=hover_cell == (row, col),
                    )

                if has_arrow and not is_active:
                    arrow_color = (
                        ERROR_ARROW
                        if (row, col) in self.game.error_cells
                        else ARROW_COLOR
                    )
                    self._draw_arrow(
                        rect,
                        cell,
                        arrow_color,
                        is_hovered=hover_cell == (row, col),
                    )

    def _draw_picture_pixel(self, rect: pygame.Rect, fill: tuple[int, int, int]) -> None:
        """Paint the revealed bead colour without blending it with the desk."""
        radius = max(6, self.layout.cell_size // 5)
        pygame.draw.rect(self.screen, fill, rect, border_radius=radius)

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
        """Draw a soft, rounded arrow card that conceals the picture below."""
        radius = max(6, self.layout.cell_size // 5)

        if is_arrow and not is_error:
            # This is the one transparent outer card. The compact direction
            # triangle below is the only opaque visual element inside it.
            glow_rect = rect.inflate(10 if is_hovered else 4, 10 if is_hovered else 4)
            glow = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                glow,
                (*HOVER_COLOR, 82 if is_hovered else 16),
                glow.get_rect(),
                border_radius=radius + 5,
            )
            self.screen.blit(glow, glow_rect.topleft)

            colour_wash = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                colour_wash,
                (*fill, HOVERED_ARROW_CARD_ALPHA if is_hovered else ARROW_CARD_ALPHA),
                colour_wash.get_rect(),
                border_radius=radius,
            )
            self.screen.blit(colour_wash, rect.topleft)
            return

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
        # The card is purposefully quiet: direction is communicated by the
        # supplied pixel arrow, while its backing only preserves hit-area and
        # hover readability.
        alpha = 210 if is_error else (102 if is_hovered else (58 if is_arrow else 172))
        border = HOVER_COLOR if is_hovered else ((178, 70, 70) if is_error else (255, 255, 255))
        border_alpha = 235 if is_hovered else (72 if is_arrow else 92)
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
            (255, 255, 255, 28 if is_arrow else 62),
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
        *,
        is_hovered: bool = False,
    ) -> None:
        center = rect.center
        marker = max(6, self.layout.cell_size // 6)
        arm_width = 3
        x, y = center
        arms = {
            "U": (
                [(x, y - marker), (x - marker, y + marker), (x - marker + arm_width, y + marker), (x, y - marker + arm_width)],
                [(x, y - marker), (x + marker, y + marker), (x + marker - arm_width, y + marker), (x, y - marker + arm_width)],
            ),
            "D": (
                [(x, y + marker), (x - marker, y - marker), (x - marker + arm_width, y - marker), (x, y + marker - arm_width)],
                [(x, y + marker), (x + marker, y - marker), (x + marker - arm_width, y - marker), (x, y + marker - arm_width)],
            ),
            "L": (
                [(x - marker, y), (x + marker, y - marker), (x + marker, y - marker + arm_width), (x - marker + arm_width, y)],
                [(x - marker, y), (x + marker, y + marker), (x + marker, y + marker - arm_width), (x - marker + arm_width, y)],
            ),
            "R": (
                [(x + marker, y), (x - marker, y - marker), (x - marker, y - marker + arm_width), (x + marker - arm_width, y)],
                [(x + marker, y), (x - marker, y + marker), (x - marker, y + marker - arm_width), (x + marker - arm_width, y)],
            ),
        }
        for arm in arms[direction]:
            shadow_points = [(point_x + 1, point_y + 2) for point_x, point_y in arm]
            pygame.draw.polygon(self.screen, (29, 47, 59), shadow_points)
            pygame.draw.polygon(self.screen, color, arm)

    def _draw_hud(self) -> None:
        self.screen.blit(self.top_status_bar, (0, 0))
        level_text = self.small_font.render(
            f"LEVEL {self.game.level_number:02d}/{self.game.level_count}",
            True,
            (250, 230, 133),
        )
        time_text = self.small_font.render(
            f"TIME {format_elapsed_time(self.game.elapsed_seconds)}",
            True,
            (240, 245, 250),
        )
        self.screen.blit(level_text, (72, 46))
        self.screen.blit(time_text, (470, 46))
        for index in range(3):
            heart = self.heart_full if index < self.game.lives else self.heart_empty
            self.screen.blit(heart, (770 + index * 54, 37))
        self.screen.blit(self.pause_icon, self.pause_rect().topleft)

    def _draw_result_panel(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((12, 28, 54, 120))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 500, 540)
        panel.center = self.screen.get_rect().center
        pygame.draw.rect(self.screen, HUD_COLOR, panel, border_radius=16)
        if self.game.state is GameState.FAILED:
            title = "TRY AGAIN"
        elif self.game.has_next_level:
            title = "LEVEL CLEAR"
        else:
            title = "ALL CLEAR"
        title_surface = self.title_font.render(title, True, (250, 230, 133))
        self.screen.blit(
            title_surface,
            title_surface.get_rect(center=(panel.centerx, panel.top + 78)),
        )

        time_text = self.small_font.render(
            f"Time: {format_elapsed_time(self.game.elapsed_seconds)}",
            True,
            (240, 245, 250),
        )
        self.screen.blit(time_text, time_text.get_rect(center=(panel.centerx, panel.top + 152)))
        if self.game.state is GameState.CLEARED and self.game.level_summary is not None:
            stars_label = self.font.render("Stars:", True, (250, 230, 133))
            self.screen.blit(
                stars_label,
                stars_label.get_rect(center=(panel.centerx - 62, panel.top + 204)),
            )
            for index in range(3):
                star = self.star_full if index < self.game.level_summary.stars else self.star_empty
                self.screen.blit(star, (panel.centerx - 15 + index * 38, panel.top + 187))

        if self.game.state is GameState.FAILED:
            button_text = "RESTART LEVEL"
        elif self.game.has_next_level:
            button_text = "NEXT LEVEL"
        else:
            button_text = "RESTART GAME"
        self._draw_action_button(
            self.result_primary_rect(),
            button_text,
            style="danger" if self.game.state is GameState.FAILED else "normal",
        )
        if self.game.state is GameState.CLEARED:
            self._draw_action_button(self.result_retry_rect(), "RETRY LEVEL")
        self._draw_action_button(self.result_menu_rect(), "MAIN MENU")

    def _draw_pause_panel(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((8, 15, 26, 156))
        self.screen.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(300, 123, 600, 554)
        self.screen.blit(self.pause_panel, panel_rect.topleft)
        title = self.title_font.render("PAUSED", True, (250, 230, 133))
        self.screen.blit(title, title.get_rect(center=(panel_rect.centerx, panel_rect.top + 105)))
        self._draw_action_button(self.pause_resume_rect(), "CONTINUE")
        self._draw_action_button(self.pause_restart_rect(), "RESTART LEVEL")
        self._draw_action_button(self.pause_menu_rect(), "MAIN MENU")

    def _draw_action_button(
        self,
        rect: pygame.Rect,
        label: str,
        *,
        style: str = "normal",
    ) -> None:
        mouse_position = pygame.mouse.get_pos() if pygame.display.get_init() else (-1, -1)
        skin_name = "hover" if rect.collidepoint(mouse_position) else style
        skin = pygame.transform.scale(self.button_skins[skin_name], rect.size)
        self.screen.blit(skin, rect.topleft)
        surface = self.small_font.render(label, True, (255, 255, 255))
        self.screen.blit(surface, surface.get_rect(center=rect.center))
