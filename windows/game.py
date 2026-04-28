import random

from PySide6 import QtGui
from PySide6.QtCore import QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QKeyEvent, QPainterPath, QRegion
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import config
from hardware_controller import get_hardware

HOLE_STYLE = """
    QPushButton {
        background: qradialgradient(
            cx:0.5, cy:0.5, radius:0.5,
            fx:0.5, fy:0.3,
            stop:0 #2C1810,
            stop:0.5 #4A2511,
            stop:0.8 #5C3317,
            stop:1 #3E2723
        );
        color: #FF8C00;
        font-size: 36px;
        font-weight: bold;
        border: none;
    }
    QPushButton:hover {
        color: #FFA500;
    }
    QPushButton:pressed {
        background: qradialgradient(
            cx:0.5, cy:0.5, radius:0.5,
            fx:0.5, fy:0.3,
            stop:0 #1A0F08,
            stop:0.5 #2C1810,
            stop:1 #3E2723
        );
    }
"""

MOLE_STYLE = """
    QPushButton {
        background: qradialgradient(
            cx:0.5, cy:0.5, radius:0.5,
            fx:0.5, fy:0.3,
            stop:0 #FFFACD,
            stop:0.45 #D2691E,
            stop:0.75 #8B4513,
            stop:1 #3E2723
        );
        color: #2C1810;
        font-size: 34px;
        font-weight: bold;
        border: none;
    }
"""

HIT_STYLE = """
    QPushButton {
        background: qradialgradient(
            cx:0.5, cy:0.5, radius:0.5,
            fx:0.5, fy:0.3,
            stop:0 #228B22,
            stop:0.5 #32CD32,
            stop:1 #2E8B57
        );
        color: white;
        font-size: 36px;
        font-weight: bold;
        border: none;
    }
"""

MISS_STYLE = """
    QPushButton {
        background: qradialgradient(
            cx:0.5, cy:0.5, radius:0.5,
            fx:0.5, fy:0.3,
            stop:0 #8B0000,
            stop:0.5 #B22222,
            stop:1 #3E2723
        );
        color: white;
        font-size: 36px;
        font-weight: bold;
        border: none;
    }
"""


class RoundButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.mole_pixmap = QtGui.QPixmap()
        self.mole_label = text

    def resizeEvent(self, event):
        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        super().resizeEvent(event)

    def set_mole(self, pixmap, label):
        self.mole_pixmap = pixmap
        self.mole_label = label
        self.setText("")
        self.update()

    def clear_mole(self, label):
        self.mole_pixmap = QtGui.QPixmap()
        self.mole_label = label
        self.setText(label)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.mole_pixmap.isNull():
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        mole_size = int(min(self.width(), self.height()) * 0.78)
        mole_x = (self.width() - mole_size) // 2
        mole_y = (self.height() - mole_size) // 2 + 5
        scaled_mole = self.mole_pixmap.scaled(
            QSize(mole_size, mole_size),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        mole_x = (self.width() - scaled_mole.width()) // 2
        mole_y = (self.height() - scaled_mole.height()) // 2 + 5
        painter.drawPixmap(mole_x, mole_y, scaled_mole)

        badge_size = 34
        badge_rect = QRectF(12, 10, badge_size, badge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(44, 24, 16, 225))
        painter.drawEllipse(badge_rect)

        painter.setPen(QtGui.QColor("#FFFACD"))
        font = QtGui.QFont("Arial", 16)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, self.mole_label)


class Game_Main(QMainWindow):
    def __init__(self, difficulty_name=config.default_difficulty):
        super().__init__()

        self.difficulty_name = difficulty_name
        self.difficulty = config.get_difficulty(difficulty_name)

        self.setWindowTitle(
            f"{config.game_name} | Spiel | {self.difficulty_name}"
        )
        self.setFixedSize(QSize(1000, 800))
        self.bg_image = QtGui.QPixmap("./assets/images/background.png")
        self.mole_image = QtGui.QPixmap("./assets/images/mole.png")
        self.hardware = get_hardware()

        self.score = 0
        self.time_left = int(self.difficulty["Time"])
        self.max_active_moles = int(self.difficulty["MPT"])
        self.mole_visible_ms = int(float(self.difficulty["MST"]) * 1000)
        self.miss_penalty = int(self.difficulty.get("MissPenalty", -5))
        self.game_over = False
        self.countdown_active = True
        self.countdown_left = int(config.start_countdown_seconds)
        self.active_moles = set()
        self.mole_tokens = {}

        self.keypad_map = {
            "1": (0, 0), "2": (0, 1), "3": (0, 2), "A": (0, 3),
            "4": (1, 0), "5": (1, 1), "6": (1, 2), "B": (1, 3),
            "7": (2, 0), "8": (2, 1), "9": (2, 2), "C": (2, 3),
            "*": (3, 0), "0": (3, 1), "#": (3, 2), "D": (3, 3),
        }

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        info_layout = QHBoxLayout()

        self.difficulty_label = QLabel(f"Modus: {self.difficulty_name}")
        self.difficulty_label.setStyleSheet(self.info_label_style(font_size=22))

        self.countdown_label = QLabel(f"Start in: {self.countdown_left}")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("""
            QLabel {
                color: #FFFACD;
                font-size: 48px;
                font-weight: bold;
                background-color: rgba(139, 69, 19, 220);
                padding: 18px 34px;
                border-radius: 18px;
                border: 5px solid #D2691E;
            }
        """)

        info_layout.addWidget(self.difficulty_label)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(25)

        self.holes = []
        self.hole_labels = [
            ["1", "2", "3", "A"],
            ["4", "5", "6", "B"],
            ["7", "8", "9", "C"],
            ["*", "0", "#", "D"],
        ]

        for row in range(4):
            hole_row = []
            for col in range(4):
                hole = RoundButton(self.hole_labels[row][col])
                hole.setFixedSize(120, 120)
                hole.setStyleSheet(HOLE_STYLE)
                hole.hide()
                hole.clicked.connect(
                    lambda checked=False, r=row, c=col: self.hit_hole(r, c)
                )
                grid_layout.addWidget(hole, row, col)
                hole_row.append(hole)
            self.holes.append(hole_row)

        back_button = QPushButton("Zurück zum Menü")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #8B4513;
                color: #FFFACD;
                font-size: 18px;
                font-weight: bold;
                padding: 12px 25px;
                border: 4px solid #D2691E;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #A0522D;
                border-color: #F4A460;
            }
            QPushButton:pressed {
                background-color: #654321;
            }
        """)
        back_button.clicked.connect(self.go_back)

        main_layout.addLayout(info_layout)
        main_layout.addSpacing(30)
        main_layout.addWidget(self.countdown_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(20)
        main_layout.addLayout(grid_layout)
        main_layout.addSpacing(30)
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)
        central_widget.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_moles)
        
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)

        self.keypad_timer = QTimer()
        self.keypad_timer.timeout.connect(self.poll_keypad)

        self.update_start_hardware_feedback()

    def update_countdown(self):
        if self.game_over:
            return

        self.countdown_left -= 1

        if self.countdown_left > 0:
            self.countdown_label.setText(f"Start in: {self.countdown_left}")
            self.update_start_hardware_feedback()
            return

        self.start_gameplay()

    def start_gameplay(self):
        if self.game_over or not self.countdown_active:
            return

        self.countdown_timer.stop()
        self.countdown_active = False
        self.countdown_label.setText("Los!")
        QTimer.singleShot(500, self.countdown_label.hide)
        QTimer.singleShot(500, self.hardware.led_off)

        self.update_lcd()
        self.timer.start(1000)
        self.spawn_timer.start(250)
        self.keypad_timer.start(30)
        self.show_holes()
        self.spawn_moles()

    def update_start_hardware_feedback(self):
        self.hardware.lcd_show("Start in:", self.countdown_left)

        if self.countdown_left >= 3:
            self.hardware.set_rgb(r=True)
        elif self.countdown_left == 2:
            self.hardware.set_rgb(r=True, g=True)
        elif self.countdown_left == 1:
            self.hardware.set_rgb(g=True)

    def poll_keypad(self):
        key = self.hardware.poll_keypad()

        if key in self.keypad_map:
            row, col = self.keypad_map[key]
            self.hit_hole(row, col)

    def show_holes(self):
        for hole_row in self.holes:
            for hole in hole_row:
                hole.show()

    def info_label_style(self, font_size=28):
        return f"""
            QLabel {{
                color: #FFFACD;
                font-size: {font_size}px;
                font-weight: bold;
                background-color: rgba(139, 69, 19, 200);
                padding: 15px 30px;
                border-radius: 15px;
                border: 4px solid #D2691E;
            }}
        """

    def paintEvent(self, e, /):
        painter = QtGui.QPainter(self)
        scaled_bg = self.bg_image.scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(0, 0, scaled_bg)
        super().paintEvent(e)

    def keyPressEvent(self, event: QKeyEvent):
        if self.game_over or self.countdown_active:
            event.ignore()
            return

        key = event.text().upper()
        if key in self.keypad_map:
            row, col = self.keypad_map[key]
            self.hit_hole(row, col)

        super().keyPressEvent(event)

    def spawn_moles(self):
        if self.game_over or self.countdown_active:
            return

        available_holes = [
            (row, col)
            for row in range(4)
            for col in range(4)
            if (row, col) not in self.active_moles
        ]

        missing_moles = self.max_active_moles - len(self.active_moles)
        if missing_moles <= 0 or not available_holes:
            return

        for row, col in random.sample(
            available_holes,
            min(missing_moles, len(available_holes)),
        ):
            self.show_mole(row, col)

    def show_mole(self, row, col):
        position = (row, col)
        token = object()
        self.active_moles.add(position)
        self.mole_tokens[position] = token

        hole = self.holes[row][col]
        hole.set_mole(self.mole_image, self.hole_labels[row][col])
        hole.setStyleSheet(MOLE_STYLE)

        QTimer.singleShot(
            self.mole_visible_ms,
            lambda pos=position, expected_token=token: self.hide_mole(
                pos,
                expected_token,
            ),
        )

    def hide_mole(self, position, expected_token=None):
        if (
            expected_token is not None
            and self.mole_tokens.get(position) is not expected_token
        ):
            return

        row, col = position
        self.active_moles.discard(position)
        self.mole_tokens.pop(position, None)

        hole = self.holes[row][col]
        hole.clear_mole(self.hole_labels[row][col])
        hole.setStyleSheet(HOLE_STYLE)

    def hit_hole(self, row, col):
        if self.game_over or self.countdown_active:
            return

        position = (row, col)
        if position not in self.active_moles:
            self.add_points(self.miss_penalty)
            self.flash_led(r=True)
            self.flash_hole(row, col, MISS_STYLE)
            return

        self.hide_mole(position)
        self.add_points(10)
        self.flash_led(g=True)
        self.flash_hole(row, col, HIT_STYLE)

    def flash_led(self, r=False, g=False, b=False):
        self.hardware.set_rgb(r=r, g=g, b=b)
        QTimer.singleShot(150, self.hardware.led_off)

    def flash_hole(self, row, col, style):
        if self.game_over:
            return

        hole = self.holes[row][col]
        text = hole.text()
        is_active = (row, col) in self.active_moles

        if not is_active:
            hole.clear_mole(self.hole_labels[row][col])
        hole.setStyleSheet(style)
        QTimer.singleShot(
            150,
            lambda: self.restore_hole_after_flash(row, col, text, is_active),
        )

    def restore_hole_after_flash(self, row, col, text, was_active):
        if self.game_over:
            return

        position = (row, col)
        hole = self.holes[row][col]

        if was_active and position in self.active_moles:
            hole.set_mole(self.mole_image, self.hole_labels[row][col])
            hole.setStyleSheet(MOLE_STYLE)
            return

        if position not in self.active_moles:
            hole.clear_mole(self.hole_labels[row][col])
            hole.setStyleSheet(HOLE_STYLE)

    def update_time(self):
        self.time_left -= 1
        self.update_lcd()

        if self.time_left <= 0:
            self.end_game()

    def end_game(self):
        self.timer.stop()
        self.spawn_timer.stop()
        self.countdown_timer.stop()
        self.keypad_timer.stop()
        self.game_over = True

        for position in list(self.active_moles):
            self.hide_mole(position)

        self.difficulty_label.setText("Spiel vorbei")
        self.hardware.led_off()
        self.hardware.lcd_show("Spiel vorbei", f"Punkte: {self.score}")
        self.show_end_screen()

    def show_end_screen(self):
        from windows.end_screen import Game_EndScreen

        self.end_screen = Game_EndScreen(
            self.score,
            self.difficulty_name,
            finished_game_window=self,
        )
        self.end_screen.show()
        self.hide()

    def add_points(self, points: int):
        self.score += points
        self.update_lcd()

    def update_lcd(self):
        self.hardware.lcd_show(
            f"Zeit: {self.time_left}s",
            f"Punkte: {self.score}",
        )

    def go_back(self):
        from windows.main_menu import Game_MainMenu

        self.game_over = True
        self.timer.stop()
        self.spawn_timer.stop()
        self.countdown_timer.stop()
        self.keypad_timer.stop()
        self.hardware.led_off()
        self.hardware.lcd_show("Menue", self.difficulty_name)
        self.main_menu = Game_MainMenu()
        self.main_menu.show()
        self.close()
