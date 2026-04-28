from PySide6 import QtGui
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from config import config


class Game_EndScreen(QMainWindow):
    def __init__(self, score, difficulty_name, finished_game_window=None):
        super().__init__()

        self.score = score
        self.difficulty_name = difficulty_name
        self.finished_game_window = finished_game_window
        self.next_window = None

        self.setWindowTitle(config.game_name + " | Ergebnis")
        self.setFixedSize(QSize(1000, 800))
        self.bg_image = QtGui.QPixmap("./assets/images/mainmenu.jpg")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(80, 70, 80, 70)
        layout.setSpacing(24)

        if self.score < 0:
            title = QLabel("Du warst ziemlich schlecht!")
        else:
            title = QLabel("Spiel vorbei")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #FFFACD;
                font-size: 46px;
                font-weight: bold;
                background-color: rgba(139, 69, 19, 210);
                padding: 18px 28px;
                border-radius: 15px;
                border: 4px solid #D2691E;
            }
        """)

        score_label = QLabel(f"Endpunktzahl: {self.score}")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet("""
            QLabel {
                color: #2C1810;
                font-size: 34px;
                font-weight: bold;
                background-color: rgba(255, 250, 205, 235);
                padding: 18px 28px;
                border-radius: 15px;
                border: 4px solid #D2691E;
            }
        """)

        difficulty_label = QLabel(f"Schwierigkeit: {self.difficulty_name}")
        difficulty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        difficulty_label.setStyleSheet("""
            QLabel {
                color: #FFFACD;
                font-size: 22px;
                font-weight: bold;
                background-color: rgba(139, 69, 19, 190);
                padding: 12px 20px;
                border-radius: 12px;
                border: 3px solid #D2691E;
            }
        """)

        button_style = """
            QPushButton {
                background-color: #8B4513;
                color: #FFFACD;
                font-size: 20px;
                font-weight: bold;
                padding: 14px 28px;
                border: 4px solid #D2691E;
                border-radius: 12px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #A0522D;
                border-color: #F4A460;
            }
            QPushButton:pressed {
                background-color: #654321;
            }
        """

        restart_button = QPushButton("Nochmal spielen")
        menu_button = QPushButton("Zurück zum Menü")
        quit_button = QPushButton("Spiel beenden")

        restart_button.setStyleSheet(button_style)
        menu_button.setStyleSheet(button_style)
        quit_button.setStyleSheet(button_style)

        restart_button.clicked.connect(self.restart_game)
        menu_button.clicked.connect(self.go_to_menu)
        quit_button.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addWidget(score_label)
        layout.addWidget(difficulty_label)
        layout.addStretch()
        layout.addWidget(restart_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(quit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        central_widget.setLayout(layout)

    def paintEvent(self, e, /):
        painter = QtGui.QPainter(self)
        scaled_bg = self.bg_image.scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(0, 0, scaled_bg)
        super().paintEvent(e)

    def restart_game(self):
        from windows.game import Game_Main

        self.close_finished_game()
        self.next_window = Game_Main(self.difficulty_name)
        self.next_window.show()
        self.close()

    def go_to_menu(self):
        from windows.main_menu import Game_MainMenu

        self.close_finished_game()
        self.next_window = Game_MainMenu()
        self.next_window.show()
        self.close()

    def close_finished_game(self):
        if self.finished_game_window is not None:
            self.finished_game_window.close()
            self.finished_game_window = None

    def closeEvent(self, event):
        self.close_finished_game()
        super().closeEvent(event)
