from PySide6 import QtGui
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QVBoxLayout, QWidget

from config import config
from hardware_controller import get_hardware


class Game_MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(config.game_name + " | Hauptmenü")
        self.setFixedSize(QSize(1000, 800))
        self.bg_image = QtGui.QPixmap("./assets/images/mainmenu.jpg")
        self.hardware = get_hardware()
        self.difficulty_names = list(config.difficulty_names())
        self.selected_difficulty_index = 0
        self.difficulty_buttons = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.addStretch()

        self.button_style = """
            QPushButton {
                background-color: #8B4513;
                color: #FFFACD;
                font-size: 18px;
                font-weight: bold;
                font-family: Arial;
                padding: 15px 25px;
                border: 4px solid #D2691E;
                border-radius: 15px;
                min-width: 280px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #A0522D;
                border-color: #F4A460;
            }
            QPushButton:pressed {
                background-color: #654321;
                border-color: #8B4513;
            }
        """
        self.selected_button_style = """
            QPushButton {
                background-color: #D2691E;
                color: #2C1810;
                font-size: 18px;
                font-weight: bold;
                font-family: Arial;
                padding: 15px 25px;
                border: 5px solid #FFFACD;
                border-radius: 15px;
                min-width: 280px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #F4A460;
                border-color: #FFFACD;
            }
            QPushButton:pressed {
                background-color: #CD853F;
            }
        """

        for difficulty_name in self.difficulty_names:
            btn_difficulty = QPushButton(f"Start: {difficulty_name}")
            btn_difficulty.setStyleSheet(self.button_style)
            btn_difficulty.clicked.connect(
                lambda checked=False, name=difficulty_name: self.start_game(name)
            )
            self.difficulty_buttons.append(btn_difficulty)
            left_layout.addWidget(btn_difficulty)
            left_layout.addSpacing(15)

        btn_credits = QPushButton("Credits")
        btn_quit = QPushButton("Spiel beenden")

        btn_credits.setStyleSheet(self.button_style)
        btn_quit.setStyleSheet(self.button_style)

        btn_credits.clicked.connect(self.show_credits)
        btn_quit.clicked.connect(self.close)

        left_layout.addWidget(btn_credits)
        left_layout.addSpacing(15)
        left_layout.addWidget(btn_quit)
        left_layout.addStretch()

        main_layout.addLayout(left_layout)
        main_layout.addStretch()
        main_layout.setContentsMargins(30, 20, 20, 20)

        central_widget.setLayout(main_layout)
        self.update_selected_difficulty()

        self.encoder_timer = QTimer()
        self.encoder_timer.timeout.connect(self.poll_encoder)
        self.encoder_timer.start(50)

    def paintEvent(self, e, /):
        painter = QtGui.QPainter(self)
        scaled_bg = self.bg_image.scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(0, 0, scaled_bg)
        super().paintEvent(e)

    def select_difficulty(self):
        self.start_game(config.default_difficulty)

    def start_game(self, difficulty_name):
        from windows.game import Game_Main

        self.encoder_timer.stop()
        self.game_menu = Game_Main(difficulty_name)
        self.game_menu.show()
        self.close()

    def show_credits(self):
        from windows.credits import Game_Credits

        self.credits_window = Game_Credits()
        self.credits_window.show()
        self.close()

    def poll_encoder(self):
        event = self.hardware.poll_encoder()

        if event == "next":
            self.move_selected_difficulty(1)
        elif event == "previous":
            self.move_selected_difficulty(-1)
        elif event == "press":
            self.start_game(self.current_difficulty_name())

    def move_selected_difficulty(self, direction):
        self.selected_difficulty_index = (
            self.selected_difficulty_index + direction
        ) % len(self.difficulty_names)
        self.update_selected_difficulty()

    def current_difficulty_name(self):
        return self.difficulty_names[self.selected_difficulty_index]

    def update_selected_difficulty(self):
        for index, button in enumerate(self.difficulty_buttons):
            if index == self.selected_difficulty_index:
                button.setStyleSheet(self.selected_button_style)
            else:
                button.setStyleSheet(self.button_style)

        self.hardware.lcd_show("Schwierigkeit", self.current_difficulty_name())

    def closeEvent(self, event):
        self.encoder_timer.stop()
        super().closeEvent(event)
