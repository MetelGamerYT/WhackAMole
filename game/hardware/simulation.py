"""Pygame-based simulation backend.

All sensors, actuators and the score display are rendered on screen.
Physical buttons are simulated by:
  * Mouse clicks on the mole holes.
  * Number keys 1-9 (key 1 = hole 0, key 9 = hole 8).
  * Key 'q' or closing the window quits the game.
"""

from __future__ import annotations

import sys
import time
from typing import List, Optional, Tuple

import pygame

from .base import Actuator, HardwareBackend, ScoreDisplay, Sensor

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
GRID_COLS = 3
GRID_ROWS = 3
CELL_SIZE = 160          # pixels per grid cell
MARGIN = 20              # space between cells
PANEL_HEIGHT = 100       # score / timer panel at the top

WINDOW_WIDTH = GRID_COLS * CELL_SIZE + (GRID_COLS + 1) * MARGIN
WINDOW_HEIGHT = PANEL_HEIGHT + GRID_ROWS * CELL_SIZE + (GRID_ROWS + 1) * MARGIN

# Colours
C_BG = (34, 139, 34)          # grass green background
C_HOLE = (60, 40, 20)         # dark brown hole
C_MOLE = (160, 100, 50)       # mole colour
C_HIT = (255, 220, 50)        # flash colour on hit
C_PANEL = (20, 80, 20)        # score panel
C_TEXT = (255, 255, 255)
C_OVERLAY = (0, 0, 0, 180)    # semi-transparent overlay


def _hole_rect(index: int) -> pygame.Rect:
    """Return the pygame.Rect for hole *index* in the grid."""
    col = index % GRID_COLS
    row = index // GRID_COLS
    x = MARGIN + col * (CELL_SIZE + MARGIN)
    y = PANEL_HEIGHT + MARGIN + row * (CELL_SIZE + MARGIN)
    return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)


# ---------------------------------------------------------------------------
# Sensor
# ---------------------------------------------------------------------------
class SimSensor(Sensor):
    """Sensor triggered by a mouse click or a number key press."""

    # Shared event queue filled by SimHardwareBackend.tick()
    _triggered: List[int] = []

    def update(self) -> None:
        while self.hole_index in SimSensor._triggered:
            SimSensor._triggered.remove(self.hole_index)
            self._fire()

    def cleanup(self) -> None:
        pass  # nothing to release


# ---------------------------------------------------------------------------
# Actuator
# ---------------------------------------------------------------------------
class SimActuator(Actuator):
    """Draws a mole hole on the pygame surface."""

    def __init__(self, hole_index: int, surface: pygame.Surface) -> None:
        super().__init__(hole_index)
        self._surface = surface
        self._active = False
        self._hit_until: float = 0.0  # timestamp until hit-flash is shown

    def set_active(self, active: bool) -> None:
        self._active = active
        self._draw()

    def set_hit(self) -> None:
        self._hit_until = time.monotonic() + 0.25
        self._draw()

    def draw(self) -> None:
        """Redraw the hole (called each frame)."""
        self._draw()

    def _draw(self) -> None:
        rect = _hole_rect(self.hole_index)
        now = time.monotonic()
        flashing = now < self._hit_until

        # Background hole
        pygame.draw.ellipse(self._surface, C_HOLE, rect)

        if flashing:
            # Hit flash
            pygame.draw.ellipse(self._surface, C_HIT, rect.inflate(-20, -20))
        elif self._active:
            # Mole is up
            pygame.draw.ellipse(self._surface, C_MOLE, rect.inflate(-20, -20))
            # Eyes
            eye_r = 8
            left_eye = (rect.centerx - 20, rect.centery - 15)
            right_eye = (rect.centerx + 20, rect.centery - 15)
            pygame.draw.circle(self._surface, (30, 20, 10), left_eye, eye_r)
            pygame.draw.circle(self._surface, (30, 20, 10), right_eye, eye_r)
            # Nose
            pygame.draw.circle(self._surface, (220, 80, 80),
                               (rect.centerx, rect.centery), 6)

        # Hole number label (1-9)
        font = pygame.font.SysFont("Arial", 22, bold=True)
        label = font.render(str(self.hole_index + 1), True, (200, 200, 200))
        self._surface.blit(label,
                           (rect.right - label.get_width() - 8,
                            rect.bottom - label.get_height() - 6))

    def cleanup(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Score display
# ---------------------------------------------------------------------------
class SimScoreDisplay(ScoreDisplay):
    """Renders score, time and level in the top panel."""

    def __init__(self, surface: pygame.Surface) -> None:
        self._surface = surface
        self._font_large = pygame.font.SysFont("Arial", 38, bold=True)
        self._font_small = pygame.font.SysFont("Arial", 24)
        self._state: Optional[Tuple[int, float, int]] = None
        self._game_over = False
        self._final_score = 0

    def update(self, score: int, time_left: float, level: int) -> None:
        self._game_over = False
        self._state = (score, time_left, level)
        self._draw_panel()

    def show_game_over(self, final_score: int) -> None:
        self._game_over = True
        self._final_score = final_score
        self._draw_overlay()

    def show_start_screen(self) -> None:
        self._surface.fill(C_BG)
        self._draw_centered_text(
            "WHACK-A-MOLE",
            self._font_large,
            C_TEXT,
            self._surface.get_height() // 2 - 60,
        )
        self._draw_centered_text(
            "Klicke eine Maulwurf-Höhle an oder drücke 1-9",
            self._font_small,
            C_TEXT,
            self._surface.get_height() // 2,
        )
        self._draw_centered_text(
            "Drücke LEERTASTE oder klicke, um zu starten",
            self._font_small,
            C_TEXT,
            self._surface.get_height() // 2 + 40,
        )
        pygame.display.flip()

    def _draw_panel(self) -> None:
        if self._state is None:
            return
        score, time_left, level = self._state
        panel_rect = pygame.Rect(0, 0, self._surface.get_width(), PANEL_HEIGHT)
        pygame.draw.rect(self._surface, C_PANEL, panel_rect)

        score_surf = self._font_large.render(f"Score: {score}", True, C_TEXT)
        self._surface.blit(score_surf, (MARGIN, 15))

        time_surf = self._font_large.render(f"Zeit: {max(0, time_left):.1f}s",
                                            True, C_TEXT)
        self._surface.blit(time_surf,
                           (self._surface.get_width() // 2
                            - time_surf.get_width() // 2, 15))

        level_surf = self._font_small.render(f"Level {level}", True, C_TEXT)
        self._surface.blit(level_surf,
                           (self._surface.get_width()
                            - level_surf.get_width() - MARGIN, 15))

    def _draw_overlay(self) -> None:
        overlay = pygame.Surface(self._surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self._surface.blit(overlay, (0, 0))

        self._draw_centered_text(
            "SPIEL VORBEI",
            self._font_large,
            (255, 80, 80),
            self._surface.get_height() // 2 - 60,
        )
        self._draw_centered_text(
            f"Punktzahl: {self._final_score}",
            self._font_large,
            C_TEXT,
            self._surface.get_height() // 2,
        )
        self._draw_centered_text(
            "Drücke LEERTASTE für ein neues Spiel",
            self._font_small,
            C_TEXT,
            self._surface.get_height() // 2 + 60,
        )
        pygame.display.flip()

    def _draw_centered_text(self, text: str, font: pygame.font.Font,
                             colour: Tuple, y: int) -> None:
        surf = font.render(text, True, colour)
        self._surface.blit(surf,
                           (self._surface.get_width() // 2
                            - surf.get_width() // 2, y))

    def cleanup(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------
class SimHardwareBackend(HardwareBackend):
    """Pygame simulation backend – no physical hardware required."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Whack-A-Mole – Simulation")
        self._surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self._clock = pygame.time.Clock()
        self._actuators: List[SimActuator] = []

    # -- HardwareBackend interface ------------------------------------------

    def create_sensors(self, num_holes: int) -> List[Sensor]:
        return [SimSensor(i) for i in range(num_holes)]

    def create_actuators(self, num_holes: int) -> List[Actuator]:
        self._actuators = [SimActuator(i, self._surface) for i in range(num_holes)]
        return list(self._actuators)

    def create_score_display(self) -> ScoreDisplay:
        self._score_display = SimScoreDisplay(self._surface)
        return self._score_display

    def tick(self) -> bool:
        SimSensor._triggered.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                # Number keys 1-9 → hole index 0-8
                if pygame.K_1 <= event.key <= pygame.K_9:
                    SimSensor._triggered.append(event.key - pygame.K_1)
                if event.key == pygame.K_SPACE:
                    SimSensor._triggered.append(-1)  # special: start/restart
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                for i in range(GRID_COLS * GRID_ROWS):
                    if _hole_rect(i).collidepoint(pos):
                        SimSensor._triggered.append(i)
                        break
                else:
                    # Click outside grid (e.g. on start/game-over overlay)
                    SimSensor._triggered.append(-1)

        # Redraw background
        self._surface.fill(C_BG)
        panel_rect = pygame.Rect(0, 0, WINDOW_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(self._surface, C_PANEL, panel_rect)

        # Redraw each hole
        for act in self._actuators:
            act.draw()

        # Redraw panel text on top
        if hasattr(self, "_score_display"):
            self._score_display._draw_panel()

        pygame.display.flip()
        self._clock.tick(60)
        return True

    def cleanup(self) -> None:
        pygame.quit()
