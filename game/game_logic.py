"""Core Whack-A-Mole game logic.

This module is completely independent of any display or hardware library.
It communicates with the outside world exclusively through the abstract
Sensor / Actuator / ScoreDisplay interfaces defined in hardware.base.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional

from .hardware.base import Actuator, ScoreDisplay, Sensor


class GameState(Enum):
    START_SCREEN = auto()
    RUNNING = auto()
    GAME_OVER = auto()


@dataclass
class LevelConfig:
    """Tuning parameters for a single difficulty level."""
    level: int
    mole_visible_seconds: float   # how long a mole stays up
    max_active_moles: int         # how many moles can be active at once
    spawn_interval_seconds: float # time between new moles appearing


# Difficulty ladder – one entry per level (levels 1-5)
_LEVELS: Dict[int, LevelConfig] = {
    1: LevelConfig(1, mole_visible_seconds=2.5, max_active_moles=1, spawn_interval_seconds=2.0),
    2: LevelConfig(2, mole_visible_seconds=2.0, max_active_moles=2, spawn_interval_seconds=1.5),
    3: LevelConfig(3, mole_visible_seconds=1.5, max_active_moles=3, spawn_interval_seconds=1.2),
    4: LevelConfig(4, mole_visible_seconds=1.2, max_active_moles=3, spawn_interval_seconds=1.0),
    5: LevelConfig(5, mole_visible_seconds=0.9, max_active_moles=4, spawn_interval_seconds=0.8),
}

GAME_DURATION_SECONDS = 60
NUM_HOLES = 9  # 3×3 grid


@dataclass
class MoleState:
    active: bool = False
    appeared_at: float = field(default_factory=time.monotonic)


class WhackAMoleGame:
    """Runs one full game session.

    Parameters
    ----------
    sensors:
        One sensor per hole (index 0 … NUM_HOLES-1).
    actuators:
        One actuator per hole, parallel to *sensors*.
    score_display:
        The display used to show score, time, and game-over screen.
    """

    def __init__(
        self,
        sensors: List[Sensor],
        actuators: List[Actuator],
        score_display: ScoreDisplay,
    ) -> None:
        assert len(sensors) == NUM_HOLES
        assert len(actuators) == NUM_HOLES

        self._sensors = sensors
        self._actuators = actuators
        self._score_display = score_display

        self._state = GameState.START_SCREEN
        self._score = 0
        self._level = 1
        self._start_time: Optional[float] = None
        self._moles: List[MoleState] = [MoleState() for _ in range(NUM_HOLES)]
        self._next_spawn_time: float = 0.0

        # Register hit callbacks for each sensor
        for sensor in self._sensors:
            sensor.register_callback(self._on_hit)

        # Show start screen once
        self._score_display.show_start_screen()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def tick(self) -> None:
        """Advance the game by one loop iteration."""
        now = time.monotonic()

        # Poll all sensors (they fire callbacks if triggered)
        for sensor in self._sensors:
            sensor.update()

        if self._state == GameState.RUNNING:
            self._update_running(now)
        # START_SCREEN and GAME_OVER are handled via _on_hit callback

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_hit(self, hole_index: int) -> None:
        """Called by a Sensor when the player hits hole *hole_index*."""
        if hole_index == -1:
            # Special signal: start / restart
            self._start_or_restart()
            return

        if self._state == GameState.START_SCREEN:
            self._start_or_restart()
            return

        if self._state == GameState.GAME_OVER:
            self._start_or_restart()
            return

        if self._state == GameState.RUNNING:
            if self._moles[hole_index].active:
                self._score += self._level  # higher level = more points
                self._moles[hole_index].active = False
                self._actuators[hole_index].set_active(False)
                self._actuators[hole_index].set_hit()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _start_or_restart(self) -> None:
        """Reset state and begin a new game."""
        self._score = 0
        self._level = 1
        self._start_time = time.monotonic()
        self._next_spawn_time = time.monotonic()
        self._state = GameState.RUNNING

        # Deactivate all moles
        for i, mole in enumerate(self._moles):
            mole.active = False
            self._actuators[i].set_active(False)

    def _update_running(self, now: float) -> None:
        assert self._start_time is not None
        elapsed = now - self._start_time
        time_left = GAME_DURATION_SECONDS - elapsed

        # Advance difficulty level every 12 seconds
        self._level = min(5, int(elapsed // 12) + 1)
        cfg = _LEVELS[self._level]

        if time_left <= 0:
            self._end_game()
            return

        # Hide moles that have been up too long
        for i, mole in enumerate(self._moles):
            if mole.active and (now - mole.appeared_at) >= cfg.mole_visible_seconds:
                mole.active = False
                self._actuators[i].set_active(False)

        # Spawn a new mole if the interval has elapsed
        active_count = sum(1 for m in self._moles if m.active)
        if now >= self._next_spawn_time and active_count < cfg.max_active_moles:
            self._spawn_mole(now)
            self._next_spawn_time = now + cfg.spawn_interval_seconds

        # Update score display
        self._score_display.update(self._score, time_left, self._level)

    def _spawn_mole(self, now: float) -> None:
        inactive = [i for i, m in enumerate(self._moles) if not m.active]
        if not inactive:
            return
        idx = random.choice(inactive)
        self._moles[idx].active = True
        self._moles[idx].appeared_at = now
        self._actuators[idx].set_active(True)

    def _end_game(self) -> None:
        """Transition to GAME_OVER state."""
        self._state = GameState.GAME_OVER

        # Deactivate all moles
        for i, mole in enumerate(self._moles):
            mole.active = False
            self._actuators[i].set_active(False)

        self._score_display.show_game_over(self._score)
