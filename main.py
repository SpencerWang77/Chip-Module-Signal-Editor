"""Chip Module Signal Editor — PyQt5 application entry point."""

import sys

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chip Module Signal Editor")
        self.resize(1000, 700)

        placeholder = QLabel("Chip Module Signal Editor", self)
        placeholder.setStyleSheet("font-size: 20px;")
        self.setCentralWidget(placeholder)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
