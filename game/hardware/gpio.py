"""Raspberry Pi GPIO hardware backend.

This backend connects the game to real physical hardware:

Sensors  → push buttons wired to GPIO input pins (one per mole hole).
Actuators → LEDs wired to GPIO output pins (one per mole hole).

Wiring (default, customisable via constructor arguments)
---------------------------------------------------------
Hole  | Button GPIO | LED GPIO
------+-------------+---------
  0   |      2      |   14
  1   |      3      |   15
  2   |      4      |   18
  3   |     17      |   23
  4   |     27      |   24
  5   |     22      |   25
  6   |     10      |    8
  7   |      9      |    7
  8   |     11      |   12

Requirements
------------
  pip install RPi.GPIO
  (or the drop-in replacement: pip install gpiozero)

The module degrades gracefully: if RPi.GPIO is not available an
ImportError is raised with a helpful message at instantiation time.
"""

from __future__ import annotations

import time
from typing import List, Optional

from .base import Actuator, HardwareBackend, ScoreDisplay, Sensor

# Default GPIO pin assignments
_DEFAULT_BUTTON_PINS = [2, 3, 4, 17, 27, 22, 10, 9, 11]
_DEFAULT_LED_PINS    = [14, 15, 18, 23, 24, 25, 8, 7, 12]


# ---------------------------------------------------------------------------
# Sensor
# ---------------------------------------------------------------------------
class GPIOSensor(Sensor):
    """Button sensor backed by a GPIO input pin with pull-up resistor."""

    def __init__(self, hole_index: int, pin: int, gpio_module) -> None:
        super().__init__(hole_index)
        self._pin = pin
        self._gpio = gpio_module
        self._last_state = gpio_module.HIGH  # pulled up → HIGH when not pressed

        gpio_module.setup(pin, gpio_module.IN, pull_up_down=gpio_module.PUD_UP)

    def update(self) -> None:
        state = self._gpio.input(self._pin)
        if state == self._gpio.LOW and self._last_state == self._gpio.HIGH:
            # Falling edge → button pressed
            self._fire()
        self._last_state = state

    def cleanup(self) -> None:
        # GPIO cleanup is handled centrally by GPIOHardwareBackend.cleanup()
        pass


# ---------------------------------------------------------------------------
# Actuator
# ---------------------------------------------------------------------------
class GPIOActuator(Actuator):
    """LED actuator backed by a GPIO output pin."""

    def __init__(self, hole_index: int, pin: int, gpio_module) -> None:
        super().__init__(hole_index)
        self._pin = pin
        self._gpio = gpio_module

        gpio_module.setup(pin, gpio_module.OUT)
        gpio_module.output(pin, gpio_module.LOW)

    def set_active(self, active: bool) -> None:
        self._gpio.output(self._pin,
                          self._gpio.HIGH if active else self._gpio.LOW)

    def set_hit(self) -> None:
        # Brief blink – a more sophisticated implementation would use a timer
        self._gpio.output(self._pin, self._gpio.LOW)
        time.sleep(0.05)
        self._gpio.output(self._pin, self._gpio.HIGH)
        time.sleep(0.05)
        self._gpio.output(self._pin, self._gpio.LOW)

    def cleanup(self) -> None:
        self._gpio.output(self._pin, self._gpio.LOW)


# ---------------------------------------------------------------------------
# Score display (serial / console fallback)
# ---------------------------------------------------------------------------
class ConsoleScoreDisplay(ScoreDisplay):
    """Prints score updates to stdout (suitable for a serial terminal)."""

    def update(self, score: int, time_left: float, level: int) -> None:
        print(f"\rScore: {score:4d}  |  Zeit: {time_left:5.1f}s  |  Level: {level}",
              end="", flush=True)

    def show_game_over(self, final_score: int) -> None:
        print(f"\n\n*** SPIEL VORBEI – Punktzahl: {final_score} ***\n")

    def show_start_screen(self) -> None:
        print("=" * 50)
        print("       WHACK-A-MOLE  (GPIO-Modus)")
        print("  Drücke einen der 9 Knöpfe, um zu starten")
        print("=" * 50)

    def cleanup(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------
class GPIOHardwareBackend(HardwareBackend):
    """Hardware backend for Raspberry Pi with physical buttons and LEDs.

    Parameters
    ----------
    button_pins:
        List of GPIO BCM pin numbers for the 9 buttons (hole 0 … 8).
        Defaults to ``_DEFAULT_BUTTON_PINS``.
    led_pins:
        List of GPIO BCM pin numbers for the 9 LEDs (hole 0 … 8).
        Defaults to ``_DEFAULT_LED_PINS``.
    """

    def __init__(
        self,
        button_pins: Optional[List[int]] = None,
        led_pins: Optional[List[int]] = None,
    ) -> None:
        try:
            import RPi.GPIO as GPIO  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "RPi.GPIO ist nicht installiert. "
                "Installiere es mit: pip install RPi.GPIO\n"
                "Verwende im Simulationsmodus: python whack_a_mole.py"
            ) from exc

        self._gpio = GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self._button_pins = button_pins or _DEFAULT_BUTTON_PINS
        self._led_pins = led_pins or _DEFAULT_LED_PINS

    def create_sensors(self, num_holes: int) -> List[Sensor]:
        return [
            GPIOSensor(i, self._button_pins[i], self._gpio)
            for i in range(num_holes)
        ]

    def create_actuators(self, num_holes: int) -> List[Actuator]:
        return [
            GPIOActuator(i, self._led_pins[i], self._gpio)
            for i in range(num_holes)
        ]

    def create_score_display(self) -> ScoreDisplay:
        return ConsoleScoreDisplay()

    def tick(self) -> bool:
        # On real hardware there is no window close event; keep running forever.
        # A physical reset button or Ctrl-C is the intended exit mechanism.
        return True

    def cleanup(self) -> None:
        self._gpio.cleanup()
