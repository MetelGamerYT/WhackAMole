from PySide6 import QtGui
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel

from config import config


class Game_Credits(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(config.game_name + " | Credits")
        self.setFixedSize(QSize(600, 400))
        self.bg_image = QtGui.QPixmap("./assets/images/mainmenu.jpg")

        # Zentrales Widget und Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Zurück-Button oben links
        back_button = QPushButton("← Zurück")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #8B4513;
                color: #FFFACD;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 15px;
                border: 3px solid #D2691E;
                border-radius: 10px;
                max-width: 120px;
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

        # Titel
        title = QLabel("Credits")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #FFFACD;
                font-size: 28px;
                font-weight: bold;
                background-color: rgba(139, 69, 19, 180);
                padding: 10px;
                border-radius: 10px;
                border: 3px solid #D2691E;
            }
        """)

        # Credits Text
        credits_text = QTextEdit()
        credits_text.setReadOnly(True)
        credits_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 250, 205, 230);
                color: #3E2723;
                font-size: 14px;
                padding: 15px;
                border: 3px solid #D2691E;
                border-radius: 10px;
            }
        """)

        # Hier fügst du deine Credits ein
        credits_content = """
<h3>Grafiken:</h3>
<ul>
    <li>Hintergrundbilder: https://img.freepik.com/vektoren-premium/landwirtschaft-die-auf-dem-feld-arbeitet-und-sonnige-tage-erntet-flache-vektorgrafik_939711-1178.jpg</li>
    <li>Maulwurf: https://www.housedigest.com/1451823/identify-mole-snake-pest-holes-lawn/</li>
</ul>

<h3>Entwicklung:</h3>
<ul>
    <li>Programmierung: Simon, Vincent, Pascal</li>
    <li>Framework: PySide6 | Python3</li>
</ul>

<h3>Besonderer Dank:</h3>
<ul>
    <li>Jörgi <3 und sein Maulwurfproblem</li>
</ul>

<h3>Betatester:</h3>
<ul>
    <li>Jannik | -390 | Mittel</li>
    <li>Eric | 490 | Einfach</li>
    <li>Hans | 480 | Einfach</li>
    <li>Timo | 1000 | Einfach</li>
    <li>Alexander | 640 | Einfach</li>
</ul>
        """
        credits_text.setHtml(credits_content)

        # Widgets zum Layout hinzufügen
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(title)
        main_layout.addSpacing(10)
        main_layout.addWidget(credits_text)

        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)

    def paintEvent(self, e, /):
        painter = QtGui.QPainter(self)
        scaled_bg = self.bg_image.scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled_bg)
        super().paintEvent(e)

    def go_back(self):
        from windows.main_menu import Game_MainMenu  # Import erst hier!
        self.main_menu = Game_MainMenu()
        self.main_menu.show()
        self.close()