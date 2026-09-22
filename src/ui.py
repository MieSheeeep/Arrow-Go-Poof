"""Pygame layout, rendering, and input translation for the playable MVP."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pygame

from src.animation import (
    CollisionAnimation,
    FlyOutAnimation,
    HeartLossAnimation,
    StarRevealAnimation,
)
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
# 开发时相对本文件定位项目根目录；打包成可执行文件后，资源被解压到
# PyInstaller 的临时目录（sys._MEIPASS），因此优先从那里读取资源。
_ROOT = Path(__file__).resolve().parent.parent
if getattr(sys, "frozen", False):
    _ROOT = Path(sys._MEIPASS)

MENU_BACKGROUND_PATH = _ROOT / "assets" / "menu-background.png"
COVER_PATH = _ROOT / "assets" / "cover.png"
UI_ASSET_DIR = _ROOT / "assets" / "ui"
BUTTON_STATES_PATH = UI_ASSET_DIR / "button-states.png"
HEARTS_PATH = UI_ASSET_DIR / "hearts.png"
PAUSE_BUTTON_PATH = UI_ASSET_DIR / "pause-button.png"
PAUSE_PANEL_PATH = UI_ASSET_DIR / "pause-panel.png"
RATING_STARS_PATH = UI_ASSET_DIR / "rating-stars.png"
TOP_STATUS_BAR_PATH = UI_ASSET_DIR / "top-status-bar.png"
PAUSE_BUTTON_FONT_PATH = Path(r"C:\Windows\Fonts\segoeuib.ttf")
# Transparent hit area over the baked-in "开始游戏" button in cover.png.
# The cover is rendered to WINDOW_SIZE, so tune this rectangle in window pixels.
COVER_START_RECT = pygame.Rect(350, 450, 470, 120)
BUTTON_SPRITE_CROPS = {
    "normal": pygame.Rect(50, 230, 675, 240),
    "hover": pygame.Rect(750, 230, 675, 240),
    "danger": pygame.Rect(1450, 230, 675, 240),
}
MENU_PANEL_COLOR = (75, 48, 31)
# The dark desk mat in the supplied work-table illustration. Puzzle cells stay
# inside it so the board feels like a bead-art project on the work surface.
WORK_MAT_RECT = pygame.Rect(180, 160, 840, 580)
REVEAL_GLOW_DURATION = 0.22

# UI 装饰调色板与动画参数（统一的金色高亮 + 深蓝面板渐变）。
GOLD = (250, 220, 120)
GOLD_BRIGHT = (255, 238, 164)
GOLD_DEEP = (200, 162, 66)
INK = (27, 43, 61)
PANEL_GRADIENT_TOP = (62, 98, 148)
PANEL_GRADIENT_BOTTOM = (30, 56, 92)
ACCENT_RED = (241, 94, 100)
COMBO_POP_DURATION = 0.42
SCORE_POP_DURATION = 0.7
LIFE_FLASH_DURATION = 0.45
RESULT_ENTRANCE_DURATION = 0.30


def _clamp(value: float, low: float, high: float) -> float:
    return low if value < low else high if value > high else value


def _ease_out_cubic(t: float) -> float:
    """先快后慢的缓动，用于面板淡入与进度条平滑。"""
    t = _clamp(t, 0.0, 1.0)
    return 1.0 - (1.0 - t) ** 3


def _ease_out_back(t: float) -> float:
    """带轻微回弹的缓动，用于标题与连击数字的「弹跳」出现。"""
    t = _clamp(t, 0.0, 1.0)
    c1 = 1.70158
    c3 = c1 + 1.0
    return 1.0 + c3 * (t - 1.0) ** 3 + c1 * (t - 1.0) ** 2


def _mix_color(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
    t: float,
) -> tuple[int, int, int]:
    """在两个颜色之间做线性插值，用于渐变填充。"""
    t = _clamp(t, 0.0, 1.0)
    return tuple(
        round(first[channel] + (second[channel] - first[channel]) * t)
        for channel in range(3)
    )


def format_elapsed_time(seconds: float) -> str:
    """Format a non-negative level duration as MM:SS.hh."""
    minutes, remaining = divmod(seconds, 60.0)
    return f"{int(minutes):02d}:{remaining:05.2f}"


def format_countdown_time(seconds: float) -> str:
    """Format a remaining duration as the compact HUD clock MM:SS."""
    whole_seconds = max(0, int(seconds))
    minutes, remainder = divmod(whole_seconds, 60)
    return f"{minutes:02d}:{remainder:02d}"


def countdown_color(remaining_seconds: float) -> tuple[int, int, int]:
    """Return the HUD urgency colour for a level countdown."""
    if remaining_seconds <= 10.0:
        return (241, 94, 100)
    if remaining_seconds <= 25.0:
        return (248, 188, 81)
    return (114, 204, 132)


def reveal_glow_strength(animation: FlyOutAnimation) -> float:
    """Return the immediate-to-zero intensity for a successful reveal."""
    return max(0.0, 1.0 - animation.elapsed / REVEAL_GLOW_DURATION)


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
    remove_artifacts: bool = False,
) -> pygame.Surface:
    """Load one supplied UI illustration, optionally crop and trim it."""
    surface = pygame.image.load(path)
    if crop is not None:
        surface = surface.subsurface(crop).copy()
    if black_is_transparent:
        surface.set_colorkey((0, 0, 0))
        if remove_artifacts:
            surface = remove_isolated_artifacts(surface, minimum_pixels=200)
    bounds = surface.get_bounding_rect()
    if bounds.size != surface.get_size():
        surface = surface.subsurface(bounds).copy()
        if black_is_transparent:
            surface.set_colorkey((0, 0, 0))
    return surface


def fit_surface(
    surface: pygame.Surface, target: pygame.Rect
) -> tuple[pygame.Surface, pygame.Rect]:
    """Fit a pixel-art surface inside a rectangle without stretching it."""
    if surface.get_width() <= 0 or surface.get_height() <= 0:
        raise ValueError("surface must have positive dimensions")
    scale = min(
        target.width / surface.get_width(),
        target.height / surface.get_height(),
    )
    size = (
        max(1, round(surface.get_width() * scale)),
        max(1, round(surface.get_height() * scale)),
    )
    fitted = pygame.transform.scale(surface, size)
    return fitted, fitted.get_rect(center=target.center)


def draw_gradient_rect(
    surface: pygame.Surface,
    rect: pygame.Rect,
    top_color: tuple[int, int, int],
    bottom_color: tuple[int, int, int],
    *,
    border_radius: int = 0,
) -> None:
    """逐行绘制垂直渐变圆角矩形，替代单调的纯色面板。"""
    if rect.width <= 0 or rect.height <= 0:
        return
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    rows = max(1, rect.height)
    for offset in range(rows):
        ratio = offset / (rows - 1) if rows > 1 else 0.0
        color = _mix_color(top_color, bottom_color, ratio)
        pygame.draw.line(
            layer, (*color, 255), (0, offset), (rect.width - 1, offset)
        )
    if border_radius > 0:
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            mask, (255, 255, 255, 255), mask.get_rect(), border_radius=border_radius
        )
        layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(layer, rect.topleft)


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
        pause_font_path = (
            PAUSE_BUTTON_FONT_PATH
            if PAUSE_BUTTON_FONT_PATH.exists()
            else None
        )
        self.pause_button_font = pygame.font.Font(pause_font_path, 32)
        cover_path = COVER_PATH if COVER_PATH.is_file() else MENU_BACKGROUND_PATH
        self.cover_background = pygame.transform.smoothscale(
            # Keep the source surface unconverted so UI can also be rendered
            # onto headless test surfaces before a display mode exists.
            pygame.image.load(cover_path), WINDOW_SIZE
        )
        self.gameplay_background = pygame.transform.smoothscale(
            pygame.image.load(MENU_BACKGROUND_PATH), WINDOW_SIZE
        )
        self.top_status_bar = pygame.transform.scale(
            _load_ui_asset(
                TOP_STATUS_BAR_PATH,
                crop=pygame.Rect(35, 210, 2105, 445),
                black_is_transparent=True,
                remove_artifacts=True,
            ),
            (1200, 104),
        )
        self.button_skins = {
            "normal": _load_ui_asset(
                BUTTON_STATES_PATH,
                crop=BUTTON_SPRITE_CROPS["normal"],
                black_is_transparent=True,
            ),
            "hover": _load_ui_asset(
                BUTTON_STATES_PATH,
                crop=BUTTON_SPRITE_CROPS["hover"],
                black_is_transparent=True,
            ),
            "danger": _load_ui_asset(
                BUTTON_STATES_PATH,
                crop=BUTTON_SPRITE_CROPS["danger"],
                black_is_transparent=True,
            ),
        }
        self.heart_full = pygame.transform.scale(
            _load_ui_asset(
                HEARTS_PATH,
                crop=pygame.Rect(250, 40, 750, 650),
                black_is_transparent=True,
            ),
            (34, 30),
        )
        self.heart_empty = pygame.transform.scale(
            _load_ui_asset(
                HEARTS_PATH,
                crop=pygame.Rect(1110, 40, 800, 650),
                black_is_transparent=True,
            ),
            (34, 30),
        )
        self.star_full = pygame.transform.scale(
            _load_ui_asset(
                RATING_STARS_PATH,
                crop=pygame.Rect(390, 60, 570, 550),
                black_is_transparent=True,
            ),
            (34, 34),
        )
        self.star_empty = pygame.transform.scale(
            _load_ui_asset(
                RATING_STARS_PATH,
                crop=pygame.Rect(1120, 60, 620, 550),
                black_is_transparent=True,
            ),
            (34, 34),
        )
        self.pause_icon = pygame.transform.scale(
            _load_ui_asset(PAUSE_BUTTON_PATH, black_is_transparent=True), (58, 58)
        )
        self.pause_panel = pygame.transform.scale(
            _load_ui_asset(PAUSE_PANEL_PATH, black_is_transparent=True), (600, 554)
        )
        self.hint_cell: tuple[int, int] | None = None
        # 界面层的「响应式」装饰状态：在每一帧对比上一帧的数值，
        # 检测到变化时触发一次性特效（连击弹跳、掉血红光、通关入场）。
        self._last_combo = 0
        self._last_score = 0
        self._last_lives = self.game.lives
        self._last_state = self.game.state
        self._combo_pop_at = -1.0
        self._combo_pop_value = 0
        self._score_gained = 0
        self._life_flash_at = -1.0
        self._result_at = -1.0
        self._countdown_ratio = 1.0
        self._last_frame_at = -1.0
        self._frame_delta = 0.0
        self._refresh_layout()

    @staticmethod
    def _now() -> float:
        """返回以秒为单位的墙钟时间，驱动界面层的轻量动画。"""
        return pygame.time.get_ticks() / 1000.0

    def _detect_transitions(self, now: float) -> None:
        """对比上一帧，把数值变化翻译成一次性视觉特效的触发点。"""
        if self.game.combo > self._last_combo:
            self._combo_pop_at = now
            self._combo_pop_value = self.game.combo
            self._score_gained = self.game.score - self._last_score
        if self.game.lives < self._last_lives:
            self._life_flash_at = now
        if self.game.state in {GameState.CLEARED, GameState.FAILED} and self._last_state not in {
            GameState.CLEARED,
            GameState.FAILED,
        }:
            self._result_at = now
        self._last_combo = self.game.combo
        self._last_score = self.game.score
        self._last_lives = self.game.lives
        self._last_state = self.game.state

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
        return pygame.Rect(1090, 23, 62, 62)

    def pause_resume_rect(self) -> pygame.Rect:
        return pygame.Rect(445, 292, 310, 100)

    def pause_restart_rect(self) -> pygame.Rect:
        return pygame.Rect(445, 408, 310, 100)

    def pause_menu_rect(self) -> pygame.Rect:
        return pygame.Rect(445, 524, 310, 100)

    def result_primary_rect(self) -> pygame.Rect:
        return pygame.Rect(450, 455, 300, 70)

    def result_retry_rect(self) -> pygame.Rect:
        return pygame.Rect(450, 535, 300, 60)

    def result_menu_rect(self) -> pygame.Rect:
        return pygame.Rect(450, 605, 300, 60)

    def start_rect(self) -> pygame.Rect:
        return COVER_START_RECT.copy()

    def result_action_rect(self) -> pygame.Rect:
        """Backward-compatible name for the primary result action."""
        return self.result_primary_rect()

    def hint_rect(self) -> pygame.Rect:
        return pygame.Rect(280, 745, 120, 40)

    def undo_rect(self) -> pygame.Rect:
        return pygame.Rect(410, 745, 120, 40)

    def auto_rect(self) -> pygame.Rect:
        return pygame.Rect(540, 745, 120, 40)

    def save_rect(self) -> pygame.Rect:
        return pygame.Rect(670, 745, 120, 40)

    def load_rect(self) -> pygame.Rect:
        return pygame.Rect(800, 745, 120, 40)

    def draw(self) -> None:
        now = self._now()
        if self._last_frame_at < 0:
            self._frame_delta = 0.0
        else:
            self._frame_delta = min(now - self._last_frame_at, 0.1)
        self._last_frame_at = now
        self._detect_transitions(now)
        if self.game.state is GameState.START:
            self._draw_menu_background()
            return
        self._draw_background()
        self._draw_board()
        self._draw_animations()
        self._draw_hint_highlight()
        self._draw_hud()
        self._draw_feature_bar()
        if self.game.state in {GameState.CLEARED, GameState.FAILED}:
            self._draw_result_panel()
        elif self.game.state is GameState.PAUSED:
            self._draw_pause_panel()

    def _draw_menu_background(self) -> None:
        """Draw the complete cover, plus a pulsing accent over its start button."""
        self.screen.blit(self.cover_background, (0, 0))
        pulse = 0.5 + 0.5 * math.sin(self._now() * 2.4)
        outline = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(
            outline,
            (255, 238, 164, round(40 + 58 * pulse)),
            self.start_rect().inflate(8, 8),
            width=3,
            border_radius=18,
        )
        self.screen.blit(outline, (0, 0))

    def _draw_background(self) -> None:
        """Draw the empty work desk behind the puzzle and overlays."""
        self.screen.blit(self.gameplay_background, (0, 0))

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
            (animation.row, animation.col)
            for animation in self.game.animations
            if isinstance(animation, (FlyOutAnimation, CollisionAnimation))
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

    def _draw_reveal_glow(self, animation: FlyOutAnimation) -> None:
        """Flash an arrow's origin with the newly revealed bead colour."""
        strength = reveal_glow_strength(animation)
        if strength <= 0.0:
            return
        color_name = self.game.board.color_grid[animation.row][animation.col]
        if color_name is None:
            return
        color = COLOR_MAP.get(color_name, COLOR_MAP["leaf"])
        bright_color = tuple(
            round(channel + (255 - channel) * 0.45) for channel in color
        )
        rect = self.layout.cell_rect(animation.row, animation.col)
        radius = max(6, self.layout.cell_size // 5)
        glow = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (*bright_color, round(210 * strength)),
            glow.get_rect(),
            border_radius=radius,
        )
        pygame.draw.rect(
            glow,
            (255, 255, 255, round(125 * strength)),
            glow.get_rect(),
            width=max(1, self.layout.cell_size // 12),
            border_radius=radius,
        )
        self.screen.blit(glow, rect.topleft)

    def _draw_animations(self) -> None:
        for animation in self.game.animations:
            if not isinstance(animation, (FlyOutAnimation, CollisionAnimation)):
                continue
            rect = self.layout.cell_rect(animation.row, animation.col)
            offset_row, offset_col = animation.offset_cells
            center = (
                rect.centerx + round(offset_col * self.layout.cell_size),
                rect.centery + round(offset_row * self.layout.cell_size),
            )
            scale = animation.scale if isinstance(animation, FlyOutAnimation) else 1.0
            rect = pygame.Rect(0, 0, round(rect.width * scale), round(rect.height * scale))
            rect.center = center
            if isinstance(animation, FlyOutAnimation):
                self._draw_fly_trail(rect, animation)
            is_error = animation.color_state == "error"
            self._draw_tile(
                rect,
                ERROR_TILE if is_error else ARROW_TILE,
                is_arrow=True,
                is_error=is_error,
            )
            self._draw_arrow(rect, animation.direction, ERROR_ARROW if is_error else ARROW_COLOR)
            if isinstance(animation, FlyOutAnimation):
                self._draw_reveal_glow(animation)

    def _draw_fly_trail(self, rect: pygame.Rect, animation: FlyOutAnimation) -> None:
        """Draw a compact fading trail behind an accelerating flying arrow."""
        if animation.phase != "flying":
            return
        direction = {
            "U": (0, 1),
            "D": (0, -1),
            "L": (1, 0),
            "R": (-1, 0),
        }[animation.direction]
        trail_length = animation.trail_length_cells * self.layout.cell_size
        for index in range(3, 0, -1):
            ratio = index / 3
            center = (
                round(rect.centerx + direction[0] * trail_length * ratio),
                round(rect.centery + direction[1] * trail_length * ratio),
            )
            radius = max(2, round(self.layout.cell_size * 0.11 * (1.1 - ratio * 0.45)))
            trail = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(trail, (*ARROW_COLOR, round(116 * (1.0 - ratio * 0.55))), trail.get_rect().center, radius)
            self.screen.blit(trail, trail.get_rect(center=center))

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
        now = self._now()
        if self.game.custom_level:
            level_label = "LEVEL RANDOM"
        else:
            level_label = f"LEVEL {self.game.level_number:02d}/{self.game.level_count}"
        self._draw_hud_text(level_label, (72, 46), GOLD)
        self._draw_hud_text(
            f"TIME {format_countdown_time(self.game.remaining_seconds)}",
            (470, 46),
            (240, 245, 250),
        )
        self._draw_countdown_bar()
        for index in range(3):
            self._draw_heart(index, now)
        for animation in self.game.animations:
            if isinstance(animation, HeartLossAnimation):
                self._draw_heart_loss(animation)
        self._draw_life_flash(now)
        self.screen.blit(self.pause_icon, self.pause_rect().topleft)

    def _draw_hud_text(
        self,
        text: str,
        position: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        """绘制带阴影的 HUD 文本，让文字从顶栏背景上更清晰地浮出。"""
        shadow = self.small_font.render(text, True, (12, 24, 38))
        self.screen.blit(shadow, (position[0] + 1, position[1] + 2))
        self.screen.blit(self.small_font.render(text, True, color), position)

    def _draw_heart(self, index: int, now: float) -> None:
        """绘制一颗生命；满血的心会随墙钟轻柔地「跳动」。"""
        center = (817 + index * 83, 52)
        if index < self.game.lives:
            pulse = 1.0 + 0.05 * math.sin(now * 3.2 + index * 0.9)
            heart = pygame.transform.rotozoom(self.heart_full, 0, pulse)
        else:
            heart = self.heart_empty
        self.screen.blit(heart, heart.get_rect(center=center))

    def _draw_life_flash(self, now: float) -> None:
        """掉血瞬间在整屏叠加一层快速淡出的红光。"""
        elapsed = now - self._life_flash_at
        if not 0.0 <= elapsed <= LIFE_FLASH_DURATION:
            return
        alpha = round(92 * (1.0 - elapsed / LIFE_FLASH_DURATION))
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((216, 58, 58, alpha))
        self.screen.blit(overlay, (0, 0))

    def _draw_countdown_bar(self) -> None:
        """把剩余时间画成平滑渐变的进度条，时间越紧迫颜色与光晕越醒目。"""
        rect = pygame.Rect(455, 76, 230, 14)
        actual = _clamp(
            self.game.remaining_seconds / self.game.time_limit_seconds, 0.0, 1.0
        )
        # 显示比例逐帧向真实值逼近，避免进度条「一步跳」。
        if self._frame_delta > 0:
            self._countdown_ratio += (actual - self._countdown_ratio) * min(
                1.0, self._frame_delta * 14.0
            )
        else:
            self._countdown_ratio = actual
        ratio = _clamp(self._countdown_ratio, 0.0, 1.0)

        pygame.draw.rect(self.screen, (14, 29, 45), rect, border_radius=7)
        pygame.draw.rect(self.screen, (27, 43, 61), rect.inflate(-2, -2), border_radius=6)

        color = countdown_color(self.game.remaining_seconds)
        inner = rect.inflate(-4, -4)
        if ratio > 0:
            fill = inner.copy()
            fill.width = max(1, round(inner.width * ratio))
            gradient = pygame.Surface(fill.size, pygame.SRCALPHA)
            for offset in range(fill.width):
                shade = _mix_color(
                    color,
                    tuple(max(0, channel - 64) for channel in color),
                    offset / max(1, fill.width - 1),
                )
                pygame.draw.line(
                    gradient, (*shade, 255), (offset, 0), (offset, fill.height)
                )
            mask = pygame.Surface(fill.size, pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=5)
            gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(gradient, fill.topleft)
            # 顶部一条高光，模拟玻璃质感。
            shine = pygame.Surface(fill.size, pygame.SRCALPHA)
            pygame.draw.rect(
                shine,
                (255, 255, 255, 48),
                (0, 0, fill.width, max(2, fill.height // 2)),
                border_radius=4,
            )
            self.screen.blit(shine, fill.topleft)

        if self.game.remaining_seconds <= 10.0:
            glow = pygame.Surface(rect.inflate(16, 16).size, pygame.SRCALPHA)
            pulse = round(42 + 34 * abs(math.sin(self._now() * 9)))
            pygame.draw.rect(glow, (*color, pulse), glow.get_rect(), border_radius=11)
            self.screen.blit(glow, glow.get_rect(center=rect.center))

    def _draw_heart_loss(self, animation: HeartLossAnimation) -> None:
        """Overlay the just-lost full heart while it flashes and fades away."""
        center = (817 + animation.heart_index * 83, 52)
        if animation.phase == "flash":
            glow = pygame.Surface((54, 50), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 72, 84, 100), glow.get_rect())
            self.screen.blit(glow, glow.get_rect(center=center))
        heart = pygame.transform.rotozoom(self.heart_full, 0, animation.scale)
        heart.set_alpha(animation.alpha)
        heart_rect = heart.get_rect(
            center=(center[0] + animation.shake_offset_x, center[1])
        )
        self.screen.blit(heart, heart_rect)

    def _result_entrance(self, now: float) -> float:
        """结算面板的淡入进度（0→1）；从未触发时直接视为已完全显示。"""
        if self._result_at < 0 or now - self._result_at >= RESULT_ENTRANCE_DURATION:
            return 1.0
        return _ease_out_cubic(max(0.0, now - self._result_at) / RESULT_ENTRANCE_DURATION)

    def _draw_result_panel(self) -> None:
        entrance = self._result_entrance(self._now())
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((12, 28, 54, round(120 * entrance)))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 540, 560)
        panel.center = self.screen.get_rect().center
        shadow = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow, (0, 0, 0, round(90 * entrance)), panel.move(6, 12), border_radius=20
        )
        self.screen.blit(shadow, (0, 0))
        draw_gradient_rect(
            self.screen, panel, PANEL_GRADIENT_TOP, PANEL_GRADIENT_BOTTOM, border_radius=20
        )
        pygame.draw.rect(self.screen, GOLD_DEEP, panel, width=2, border_radius=20)
        pygame.draw.rect(
            self.screen, (255, 255, 255), panel.inflate(-8, -8), width=1, border_radius=16
        )

        if self.game.state is GameState.FAILED:
            title = "TIME UP" if self.game.failure_reason == "time_up" else "TRY AGAIN"
        elif self.game.has_next_level:
            title = "LEVEL CLEAR"
        else:
            title = "ALL CLEAR"
        self._draw_result_title(title, panel, entrance)

        divider = pygame.Surface((panel.width - 120, 1), pygame.SRCALPHA)
        divider.fill((*GOLD_DEEP, 120))
        self.screen.blit(divider, (panel.left + 60, panel.top + 112))
        stats = (
            ("TIME", format_elapsed_time(self.game.elapsed_seconds)),
            ("MISTAKES", str(self.game.mistakes)),
            ("BEST COMBO", f"x{self.game.max_combo}"),
            ("SCORE", str(self.game.score)),
        )
        for index, (label, value) in enumerate(stats):
            column = panel.centerx - 130 if index % 2 == 0 else panel.centerx + 130
            row = panel.top + 134 if index < 2 else panel.top + 196
            self._draw_stat(label, value, column, row)

        if self.game.state is GameState.CLEARED and self.game.level_summary is not None:
            self._draw_result_stars(panel)

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

    def _draw_result_title(self, title: str, panel: pygame.Rect, entrance: float) -> None:
        """标题在入场时轻微放大回弹，并带描边与阴影。"""
        base = self.title_font.render(title, True, GOLD_BRIGHT)
        if entrance < 1.0:
            scale = max(0.05, _ease_out_back(entrance))
            surface = pygame.transform.rotozoom(base, 0, scale)
        else:
            surface = base
        shadow = self.title_font.render(title, True, (10, 18, 28))
        center = (panel.centerx, panel.top + 60)
        self.screen.blit(shadow, shadow.get_rect(center=(center[0] + 3, center[1] + 4)))
        self.screen.blit(surface, surface.get_rect(center=center))

    def _draw_stat(
        self,
        label: str,
        value: str,
        center_x: int,
        top: int,
    ) -> None:
        """在结算面板上绘制一组「标签 + 数值」的统计单元格。"""
        label_surface = self.small_font.render(label, True, (150, 180, 210))
        value_surface = self.font.render(value, True, (240, 245, 250))
        self.screen.blit(label_surface, label_surface.get_rect(midtop=(center_x, top)))
        self.screen.blit(value_surface, value_surface.get_rect(midtop=(center_x, top + 22)))

    def _draw_result_stars(self, panel: pygame.Rect) -> None:
        """Show empty stars first, then pop earned stars in a short sequence."""
        assert self.game.level_summary is not None
        label = self.small_font.render("STARS", True, (150, 180, 210))
        self.screen.blit(label, label.get_rect(midtop=(panel.centerx, panel.top + 252)))
        reveal = next(
            (
                animation
                for animation in self.game.animations
                if isinstance(animation, StarRevealAnimation)
            ),
            None,
        )
        positions = [
            (panel.centerx - 38 + index * 38, panel.top + 280) for index in range(3)
        ]
        for position in positions:
            self.screen.blit(self.star_empty, position)
        for index in range(self.game.level_summary.stars):
            progress = 1.0 if reveal is None else reveal.star_progress(index)
            if progress == 0.0:
                continue
            scale = 1.0 if reveal is None else reveal.star_scale(index)
            star = pygame.transform.rotozoom(self.star_full, 0, scale)
            center = (positions[index][0] + 17, positions[index][1] + 17)
            if scale > 1.0:
                glow = pygame.Surface((64, 64), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow,
                    (255, 218, 91, round(104 * progress)),
                    glow.get_rect().center,
                    24,
                )
                self.screen.blit(glow, glow.get_rect(center=center))
            self.screen.blit(star, star.get_rect(center=center))

    def _draw_hint_highlight(self) -> None:
        """Outline the currently hinted arrow with a pulsing double border."""
        if self.hint_cell is None or self.game.state is not GameState.PLAYING:
            return
        row, col = self.hint_cell
        if self.game.board.get_cell(row, col) not in {"U", "D", "L", "R"}:
            return
        rect = self.layout.cell_rect(row, col).inflate(6, 6)
        pulse = 0.5 + 0.5 * math.sin(self._now() * 6.0)
        fill = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            fill,
            (102, 213, 255, round(24 + 32 * pulse)),
            fill.get_rect(),
            border_radius=10,
        )
        self.screen.blit(fill, rect.topleft)
        pygame.draw.rect(self.screen, HOVER_COLOR, rect, width=4, border_radius=10)
        pygame.draw.rect(
            self.screen,
            (102, 213, 255),
            rect.inflate(8, 8),
            width=2,
            border_radius=14,
        )

    def _draw_feature_bar(self) -> None:
        """Draw the in-game action buttons plus score and combo readouts."""
        if self.game.state is not GameState.PLAYING:
            return
        strip = pygame.Surface((WINDOW_SIZE[0], 62), pygame.SRCALPHA)
        strip.fill((12, 24, 38, 120))
        pygame.draw.line(strip, (255, 255, 255, 28), (0, 0), (WINDOW_SIZE[0], 0))
        self.screen.blit(strip, (0, 738))
        for rect, label in (
            (self.hint_rect(), "HINT"),
            (self.undo_rect(), "UNDO"),
            (self.auto_rect(), "AUTO"),
            (self.save_rect(), "SAVE"),
            (self.load_rect(), "LOAD"),
        ):
            self._draw_text_button(rect, label)
        self._draw_score_readout()
        self._draw_combo_readout(self._now())

    def _draw_score_readout(self) -> None:
        """在功能条左侧显示分数，配合得分弹出动画一起呈现。"""
        label = self.small_font.render("SCORE", True, (150, 180, 210))
        self.screen.blit(label, (40, 744))
        value = self.font.render(f"{self.game.score:06d}", True, (240, 245, 250))
        self.screen.blit(value, (40, 762))

        elapsed = self._now() - self._combo_pop_at
        if 0.0 <= elapsed <= SCORE_POP_DURATION:
            progress = elapsed / SCORE_POP_DURATION
            rise = round(progress * 28)
            alpha = round(255 * (1.0 - progress))
            pop = self.font.render(f"+{self._score_gained}", True, (114, 204, 132))
            pop.set_alpha(alpha)
            self.screen.blit(pop, pop.get_rect(center=(150, 732 - rise)))

    def _draw_combo_readout(self, now: float) -> None:
        """在功能条右侧显示连击数；连击增长时数字会「弹跳」并变色。"""
        label = self.small_font.render("COMBO", True, (150, 180, 210))
        self.screen.blit(label, label.get_rect(topright=(1184, 744)))
        pop_elapsed = now - self._combo_pop_at
        if 0.0 <= pop_elapsed <= COMBO_POP_DURATION:
            progress = pop_elapsed / COMBO_POP_DURATION
            scale = _ease_out_back(progress)
            color = _mix_color(GOLD_BRIGHT, GOLD, progress)
        else:
            scale = 1.0
            color = GOLD if self.game.combo > 0 else (150, 180, 210)
        text = self.font.render(f"x{self.game.combo}", True, color)
        if scale != 1.0:
            text = pygame.transform.rotozoom(text, 0, scale)
        self.screen.blit(text, text.get_rect(topright=(1184, 762)))

    def _draw_pause_panel(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((8, 15, 26, 156))
        self.screen.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(300, 123, 600, 554)
        self.screen.blit(self.pause_panel, panel_rect.topleft)
        title_center = (panel_rect.centerx, panel_rect.top + 105)
        title_shadow = self.title_font.render("PAUSED", True, (10, 18, 28))
        self.screen.blit(
            title_shadow,
            title_shadow.get_rect(center=(title_center[0] + 3, title_center[1] + 4)),
        )
        title = self.title_font.render("PAUSED", True, GOLD_BRIGHT)
        self.screen.blit(title, title.get_rect(center=title_center))
        self._draw_text_button(self.pause_resume_rect(), "CONTINUE")
        self._draw_text_button(self.pause_restart_rect(), "RESTART LEVEL")
        self._draw_text_button(self.pause_menu_rect(), "MAIN MENU")

    def _draw_text_button(self, rect: pygame.Rect, label: str) -> None:
        """Draw pause-menu text; the supplied rect remains the invisible hit area."""
        mouse_position = pygame.mouse.get_pos() if pygame.display.get_init() else (-1, -1)
        color = (250, 230, 133) if rect.collidepoint(mouse_position) else (240, 245, 250)
        shadow = self.pause_button_font.render(label, True, (10, 18, 28))
        shadow_rect = shadow.get_rect(center=(rect.centerx + 2, rect.centery + 2))
        self.screen.blit(shadow, shadow_rect)
        surface = self.pause_button_font.render(label, True, color)
        self.screen.blit(surface, surface.get_rect(center=rect.center))

    def _draw_action_button(
        self,
        rect: pygame.Rect,
        label: str,
        *,
        style: str = "normal",
    ) -> None:
        mouse_position = pygame.mouse.get_pos() if pygame.display.get_init() else (-1, -1)
        skin_name = "hover" if rect.collidepoint(mouse_position) else style
        skin, skin_rect = fit_surface(self.button_skins[skin_name], rect)
        self.screen.blit(skin, skin_rect)
        surface = self.small_font.render(label, True, (255, 255, 255))
        self.screen.blit(surface, surface.get_rect(center=rect.center))
