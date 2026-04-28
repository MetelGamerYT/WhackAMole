# Schlag den Maulwurf

## 1. Einleitung

### 1.1 Projektbeschreibung

Im Rahmen des Lernfelds 7, **Vernetzte Systeme entwickeln und betreiben**, wird ein interaktives Spiel nach dem Prinzip von **Whack-A-Mole** entwickelt. Das Projekt verbindet eine grafische Benutzeroberfläche mit späterer Hardware-Anbindung über einen Raspberry Pi.

Ziel ist eine spielbare Konsole, bei der Maulwürfe zufällig auf einem 4x4-Spielfeld erscheinen. Der Spieler muss die passende Position rechtzeitig treffen. Aktuell wird das Spiel über Maus oder Tastatur gesteuert. Später soll die Eingabe über Sensoren und die Ausgabe über Aktoren erfolgen.

### 1.2 Projektdaten

| Bereich | Beschreibung |
| --- | --- |
| Lernfeld | LF 7: Vernetzte Systeme entwickeln und betreiben |
| Projektzeitraum | ab 9. Februar 2026 |
| Geplanter Tagesaufwand | ca. 90 Minuten |
| Programmiersprache | Python |
| GUI-Framework | PySide6 |
| Zielplattform | Raspberry Pi mit zusätzlichem Bildschirm |

### 1.3 Gruppenzusammensetzung

| Name |
| --- |
| Simon |
| Pascal |
| Vincent |

## 2. Hardware-Konzept

Das Projekt soll später mindestens zwei Sensoren und zwei Aktoren verwenden. Der Raspberry Pi übernimmt dabei die zentrale Steuerung.

### 2.1 Sensoren

| Sensor | Funktion im Projekt | Begründung |
| --- | --- | --- |
| 4x4-Keypad | Physisches Spielfeld mit 16 Positionen | Jede Taste entspricht einem Loch im Spiel. Ein Tastendruck ist ein Treffer- oder Fehlversuch. |
| Joystick mit Tastendruck | Menüauswahl und Bestätigung | Der Spieler kann damit die Schwierigkeit auswählen und das Spiel starten. |

### 2.2 Aktoren

| Aktor | Funktion im Projekt | Begründung |
| --- | --- | --- |
| LCD-Display 16x2 | Anzeige von Zeit, Punkten, Schwierigkeit und Trefferfeedback | Spielstatus bleibt unabhängig von der Haupt-GUI sichtbar. |
| RGB-LED | Visuelles Feedback für Start, Treffer und Reaktionszeit | Zustände können schnell und eindeutig über Farben signalisiert werden. |

### 2.3 Weitere Komponenten

| Komponente | Rolle |
| --- | --- |
| Raspberry Pi | Führt den Python-Code aus und steuert GPIO-Schnittstellen. |
| Bildschirm | Zeigt Hauptmenü, Spielfeld und Endscreen an. |

## 3. Aktueller Softwarestand

Die Anwendung ist aktuell als PySide6-Desktopspiel aufgebaut. Die Hardware-Anbindung ist noch nicht implementiert, die Spiellogik ist aber bereits so vorbereitet, dass Sensoren später an die bestehenden Eingabepunkte angebunden werden können.

### 3.1 Projektstruktur

```text
Maulwurf/
├── assets/
│   └── images/
│       ├── background.png
│       └── mainmenu.jpg
├── windows/
│   ├── credits.py
│   ├── end_screen.py
│   ├── game.py
│   └── main_menu.py
├── config.py
├── main.py
└── DOKUMENTATION.md
```

### 3.2 Modulübersicht

| Datei | Aufgabe |
| --- | --- |
| `main.py` | Startet die PySide6-Anwendung, öffnet das Hauptmenü und räumt GPIO beim Beenden auf. |
| `config.py` | Enthält Spielname, Standardschwierigkeit und Difficulty-Werte. |
| `hardware_controller.py` | Kapselt Keypad, LCD, RGB-LED und Rotary Encoder über GPIO. Auf Systemen ohne Raspberry-Pi-GPIO bleibt das Modul inaktiv. |
| `windows/main_menu.py` | Zeigt das Hauptmenü und erzeugt Start-Buttons aus der Config. |
| `windows/game.py` | Enthält Spielfeld, Timer, Spawn-Logik, Trefferwertung und Fehlklick-Strafen. |
| `windows/end_screen.py` | Zeigt nach Spielende die erreichte Punktzahl und Navigationsbuttons. |
| `windows/credits.py` | Zeigt Credits und Quellenhinweise. |

## 4. Spielkonzept und Logik

### 4.1 Spielablauf

1. Die Anwendung startet im Hauptmenü.
2. Der Spieler wählt eine Schwierigkeit aus.
3. Das Spielfeld öffnet sich mit 16 runden Löchern.
4. Je nach Schwierigkeit erscheinen zufällig Maulwürfe.
5. Ein Treffer auf ein aktives Maulwurf-Loch gibt Punkte.
6. Ein Treffer auf ein leeres Loch zieht Punkte ab.
7. Nach Ablauf der Zeit endet das Spiel.
8. Der Endscreen zeigt die erreichte Punktzahl.

### 4.2 Steuerung

| Eingabe | Aktueller Stand | Spätere Hardware-Zuordnung |
| --- | --- | --- |
| Maus | Klick auf ein Loch | Keypad-Taste |
| Tastatur | Tasten `1-9`, `0`, `A-D`, `*`, `#` | 4x4-Keypad-Matrix |
| Schwierigkeit | Button im Hauptmenü | Joystick-Auswahl |

### 4.3 Punktewertung

| Aktion | Wirkung |
| --- | --- |
| Aktiven Maulwurf treffen | `+10` Punkte |
| Leeres Loch treffen | Abzug über `MissPenalty` aus `config.py` |
| Maulwurf nicht treffen | Aktuell kein direkter Punktabzug |

## 5. Konfiguration

Die zentralen Spielwerte liegen in `config.py`. Dadurch kann das Balancing angepasst werden, ohne die Spiellogik selbst zu ändern.

| Key | Bedeutung |
| --- | --- |
| `Time` | Rundendauer in Sekunden |
| `MPT` | Maximale Anzahl gleichzeitig sichtbarer Maulwürfe |
| `MST` | Sichtdauer eines Maulwurfs in Sekunden |
| `MissPenalty` | Punktabzug bei Fehlklick |

Aktueller Stand:

| Schwierigkeit | Time | MPT | MST | MissPenalty |
| --- | ---: | ---: | ---: | ---: |
| Einfach | 120 | 3 | 1.5 | -5 |
| Mittel | 90 | 2 | 1 | -10 |
| Schwer | 60 | 1 | 0.5 | -15 |
| Albtraum | 60 | 1 | 0.35 | -30 |

## 6. GUI

### 6.1 Hauptmenü

Das Hauptmenü zeigt automatisch für jede Schwierigkeit aus `config.py` einen Start-Button an. Neue Schwierigkeiten können dadurch ergänzt werden, ohne das Menü manuell erweitern zu müssen.

### 6.2 Spielbildschirm

Der Spielbildschirm zeigt:

- Punktzahl
- aktuelle Schwierigkeit
- verbleibende Zeit
- 4x4-Spielfeld
- Button zurück zum Menü

Die Maulwürfe erscheinen zufällig auf freien Feldern. Intern wird dafür eine Menge aktiver Positionen verwaltet. Dadurch kann später leicht geprüft werden, ob ein Keypad-Signal auf ein aktives Loch zeigt.

### 6.3 Endscreen

Nach Ablauf der Spielzeit wird ein eigener Endscreen geöffnet. Er zeigt:

- Hinweis, dass das Spiel vorbei ist
- Endpunktzahl
- gewählte Schwierigkeit
- Button zum erneuten Spielen
- Button zurück zum Menü
- Button zum Beenden

## 7. Hardware-Integration

### 7.1 Keypad

Das 4x4-Keypad verwendet dieselbe Positionslogik wie die aktuelle Tastaturbelegung:

```text
1  2  3  A
4  5  6  B
7  8  9  C
*  0  #  D
```

Ein Tastendruck wird im Spiel direkt auf die vorhandene Methode `hit_hole(row, col)` gemappt. Dadurch nutzen Maus, Tastatur und Keypad dieselbe Trefferlogik.

### 7.2 Joystick

Der drehbare Rotary Encoder wählt im Hauptmenü die Schwierigkeit aus. Drehen nach links oder rechts wechselt den aktuell markierten Modus, der Tastendruck startet das Spiel.

### 7.3 LCD-Display

Das LCD zeigt Spielinformationen unabhängig vom GUI-Bildschirm:

- ausgewählte Schwierigkeit
- Start-Countdown
- verbleibende Zeit
- aktuelle Punktzahl
- Endpunktzahl

### 7.4 RGB-LED

Die RGB-LED macht Zustände sichtbar:

| Zustand | LED-Idee |
| --- | --- |
| Start-Countdown | Rot, Orange, Grün |
| richtiger Treffer | Grün blinken |
| falscher Treffer | Rot blinken |

## 8. GPIO-Pinbelegung

| Komponente | Typ | Pins | Bemerkung |
| --- | --- | --- | --- |
| 4x4-Keypad | Sensor | Rows: GPIO 5, 6, 13, 19; Cols: GPIO 12, 16, 20, 21 | Matrixabfrage mit Pull-ups an den Spalten |
| LCD 16x2 HD44780 | Aktor | RS: GPIO 26, E: GPIO 24, Data: GPIO 4, 17, 18, 27, 22, 23, 25, 8 | 8-Bit-Ansteuerung über `RPLCD.gpio.CharLCD` |
| RGB-LED | Aktor | Rot: GPIO 7, Grün: GPIO 9, Blau: GPIO 10 | Common Cathode |
| Rotary Encoder | Sensor | CLK: GPIO 11, DT: GPIO 14, SW: GPIO 15 | Drehen zur Auswahl, Druck zum Start |

## 9. Offene Aufgaben

- Reaktionszeit erfassen und zur LED-Farbe oder Punktewertung verwenden.
- Hardware-Verhalten auf dem Raspberry Pi im Zusammenspiel mit der GUI testen.
- LCD-Texte bei Bedarf für 16 Zeichen optimieren.
- Optional: Encoder auch auf dem Endscreen für Neustart oder Menü-Navigation verwenden.
