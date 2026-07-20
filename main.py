"""Application entry point for Chip Module Editor for ESWIN."""

import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from chip_editor.constants import APP_NAME
from chip_editor.theme import STYLE_SHEET
from chip_editor.window import MainWindow


def main() -> None:
    """Configure Qt and launch the desktop application."""

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    base_font = QFont("Avenir Next")
    base_font.setPointSize(10)
    app.setFont(base_font)
    app.setStyleSheet(STYLE_SHEET)

    window = MainWindow(Path(__file__).resolve().parent)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
