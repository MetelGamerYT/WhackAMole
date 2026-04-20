#!/usr/bin/env python3
"""Whack-A-Mole – Hauptprogramm / Main entry point.

Verwendung / Usage
------------------
Simulation (kein Hardware erforderlich):
    python whack_a_mole.py

Raspberry Pi GPIO-Modus:
    python whack_a_mole.py --gpio

GPIO-Modus mit benutzerdefinierten Pins:
    python whack_a_mole.py --gpio \\
        --button-pins 2,3,4,17,27,22,10,9,11 \\
        --led-pins    14,15,18,23,24,25,8,7,12

Steuerung (Simulation) / Controls (simulation)
-----------------------------------------------
  Maus-Klick / Mouse click : Maulwurf treffen / Hit a mole
  Tasten 1–9               : Maulwurf treffen / Hit a mole
  LEERTASTE / SPACE        : Spiel starten oder neu starten
  Q                        : Beenden / Quit
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from game.game_logic import WhackAMoleGame


def _parse_pin_list(raw: str) -> List[int]:
    """Parse a comma-separated list of pin numbers."""
    try:
        return [int(p.strip()) for p in raw.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Ungültige Pin-Liste: {raw!r}  (erwartet: '2,3,4,...')"
        ) from exc


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Whack-A-Mole – Python-Spiel mit Sensoren und Aktoren"
    )
    parser.add_argument(
        "--gpio",
        action="store_true",
        help="Raspberry Pi GPIO-Modus aktivieren (Standard: Simulation)",
    )
    parser.add_argument(
        "--button-pins",
        type=_parse_pin_list,
        metavar="PINS",
        help="Komma-getrennte GPIO BCM-Pins für die 9 Taster (nur GPIO-Modus)",
    )
    parser.add_argument(
        "--led-pins",
        type=_parse_pin_list,
        metavar="PINS",
        help="Komma-getrennte GPIO BCM-Pins für die 9 LEDs (nur GPIO-Modus)",
    )
    args = parser.parse_args(argv)

    # ------------------------------------------------------------------
    # Select hardware backend
    # ------------------------------------------------------------------
    if args.gpio:
        from game.hardware.gpio import GPIOHardwareBackend
        backend = GPIOHardwareBackend(
            button_pins=args.button_pins,
            led_pins=args.led_pins,
        )
    else:
        from game.hardware.simulation import SimHardwareBackend
        backend = SimHardwareBackend()

    # ------------------------------------------------------------------
    # Build game components
    # ------------------------------------------------------------------
    from game.game_logic import NUM_HOLES
    sensors = backend.create_sensors(NUM_HOLES)
    actuators = backend.create_actuators(NUM_HOLES)
    score_display = backend.create_score_display()

    game = WhackAMoleGame(sensors, actuators, score_display)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    try:
        while True:
            if not backend.tick():
                break
            game.tick()
    except KeyboardInterrupt:
        pass
    finally:
        backend.cleanup()


if __name__ == "__main__":
    main()
