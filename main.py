from PySide6.QtWidgets import QApplication
from game_window import GameWindow
import sys
from pathlib import Path


def main():
    app = QApplication(sys.argv)
    # Подключаем стиль (как CSS)
    qss_path = Path(__file__).with_name("styles.qss")
    with open(qss_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    w = GameWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

#проверка