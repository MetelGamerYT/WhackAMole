# Whack-A-Mole 🐾

Berufsschulprojekt – Python-Spiel mit **Sensoren** (Taster / Tastatur) und **Aktoren** (LEDs / Bildschirm).

---

## Spielprinzip

In einem **3×3-Raster** tauchen zufällig Maulwürfe auf.  
Der Spieler hat **60 Sekunden**, um möglichst viele Maulwürfe zu treffen.  
Mit jedem Level (alle 12 Sekunden) steigt die Schwierigkeit: Die Maulwürfe tauchen kürzer auf und mehrere können gleichzeitig aktiv sein.

| Level | Sichtbar (s) | Max. gleichzeitig | Spawntakt (s) |
|------:|-------------:|------------------:|--------------:|
| 1     | 2,5          | 1                 | 2,0           |
| 2     | 2,0          | 2                 | 1,5           |
| 3     | 1,5          | 3                 | 1,2           |
| 4     | 1,2          | 3                 | 1,0           |
| 5     | 0,9          | 4                 | 0,8           |

---

## Projektstruktur

```
whack_a_mole.py          ← Hauptprogramm / Startpunkt
requirements.txt
game/
  game_logic.py          ← Spiellogik (unabhängig von Hardware)
  hardware/
    base.py              ← Abstrakte Interfaces: Sensor, Actuator, ScoreDisplay
    simulation.py        ← Pygame-Simulation (kein Raspberry Pi nötig)
    gpio.py              ← Raspberry Pi GPIO (Taster + LEDs)
```

---

## Voraussetzungen & Installation

```bash
pip install -r requirements.txt
```

*Für den GPIO-Modus auf dem Raspberry Pi zusätzlich:*

```bash
pip install RPi.GPIO
```

---

## Starten

### Simulationsmodus (PC / kein Hardware erforderlich)

```bash
python whack_a_mole.py
```

### Raspberry Pi GPIO-Modus

```bash
python whack_a_mole.py --gpio
```

Mit benutzerdefinierten Pins:

```bash
python whack_a_mole.py --gpio \
    --button-pins 2,3,4,17,27,22,10,9,11 \
    --led-pins    14,15,18,23,24,25,8,7,12
```

---

## Steuerung (Simulationsmodus)

| Eingabe              | Aktion                    |
|----------------------|---------------------------|
| Maus-Klick auf Loch  | Maulwurf treffen          |
| Tasten **1 – 9**     | Maulwurf treffen          |
| **LEERTASTE**        | Spiel starten / neu starten |
| **Q**                | Beenden                   |

---

## Hardware-Verdrahtung (Raspberry Pi)

```
Loch | Taster (BCM) | LED (BCM)
-----|-------------|----------
  1  |      2      |    14
  2  |      3      |    15
  3  |      4      |    18
  4  |     17      |    23
  5  |     27      |    24
  6  |     22      |    25
  7  |     10      |     8
  8  |      9      |     7
  9  |     11      |    12
```

Die Taster sind mit einem internen Pull-Up-Widerstand konfiguriert (LOW = gedrückt).  
Die LEDs leuchten, wenn der zugehörige GPIO-Pin HIGH ist.

---

## Architektur – Sensoren & Aktoren

Die Spiellogik (`game/game_logic.py`) kommuniziert **ausschließlich** über abstrakte Interfaces:

- **`Sensor`** – meldet einen Treffer (Tastendruck / Knopf) über einen Callback.
- **`Actuator`** – schaltet LED oder Bildschirmelement ein/aus.
- **`ScoreDisplay`** – zeigt Punkte, Zeit und Level an.
- **`HardwareBackend`** – Fabrik, die alle Sensoren, Aktoren und das Display erzeugt.

Dadurch lässt sich der Code **ohne Änderungen** sowohl in der Simulation als auch auf echter Hardware betreiben.