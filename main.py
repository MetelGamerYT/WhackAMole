import sys

from PySide6.QtWidgets import QApplication

from hardware_controller import cleanup_hardware
from windows.main_menu import Game_MainMenu


def main():
    app = QApplication(sys.argv)
    window = Game_MainMenu()
    window.show()

    try:
        return app.exec()
    finally:
        cleanup_hardware()


if __name__ == "__main__":
    sys.exit(main())
