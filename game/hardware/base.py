"""Abstract base classes for sensors and actuators.

Sensors  – detect player input (physical buttons or keyboard keys).
Actuators – drive output (LEDs, buzzer, or on-screen elements).

Implementing these interfaces allows the game to run unchanged whether it
is connected to real Raspberry Pi GPIO hardware or runs in pure software
simulation mode.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, List, Optional


class Sensor(ABC):
    """Abstract sensor that detects a player "hit" on a mole hole."""

    def __init__(self, hole_index: int) -> None:
        """
        Parameters
        ----------
        hole_index:
            Zero-based index of the mole hole this sensor belongs to (0-8
            for a 3×3 grid).
        """
        self.hole_index = hole_index
        self._callback: Optional[Callable[[int], None]] = None

    def register_callback(self, callback: Callable[[int], None]) -> None:
        """Register a function that is called when this sensor fires.

        The callback receives the *hole_index* as its single argument.
        """
        self._callback = callback

    def _fire(self) -> None:
        """Notify the game that this sensor was triggered."""
        if self._callback is not None:
            self._callback(self.hole_index)

    @abstractmethod
    def update(self) -> None:
        """Poll the sensor state (called once per game loop tick)."""

    @abstractmethod
    def cleanup(self) -> None:
        """Release any resources held by this sensor."""


class Actuator(ABC):
    """Abstract actuator that signals the current state of a mole hole."""

    def __init__(self, hole_index: int) -> None:
        """
        Parameters
        ----------
        hole_index:
            Zero-based index of the mole hole this actuator belongs to.
        """
        self.hole_index = hole_index

    @abstractmethod
    def set_active(self, active: bool) -> None:
        """Activate or deactivate this actuator (mole visible / hidden)."""

    @abstractmethod
    def set_hit(self) -> None:
        """Briefly signal that the mole was successfully hit."""

    @abstractmethod
    def cleanup(self) -> None:
        """Release any resources held by this actuator."""


class ScoreDisplay(ABC):
    """Abstract display for score and remaining time."""

    @abstractmethod
    def update(self, score: int, time_left: float, level: int) -> None:
        """Refresh the score / timer / level display."""

    @abstractmethod
    def show_game_over(self, final_score: int) -> None:
        """Show a game-over screen with the final score."""

    @abstractmethod
    def show_start_screen(self) -> None:
        """Show the welcome / start screen."""

    @abstractmethod
    def cleanup(self) -> None:
        """Release any resources held by this display."""


class HardwareBackend(ABC):
    """Factory that creates all sensors, actuators, and the score display."""

    @abstractmethod
    def create_sensors(self, num_holes: int) -> List[Sensor]:
        """Return one *Sensor* per hole."""

    @abstractmethod
    def create_actuators(self, num_holes: int) -> List[Actuator]:
        """Return one *Actuator* per hole."""

    @abstractmethod
    def create_score_display(self) -> ScoreDisplay:
        """Return the score / time display."""

    @abstractmethod
    def tick(self) -> bool:
        """
        Called once per game loop iteration.

        Returns
        -------
        bool
            *False* if the application should quit (e.g. window closed),
            *True* to keep running.
        """

    @abstractmethod
    def cleanup(self) -> None:
        """Release all hardware resources."""
