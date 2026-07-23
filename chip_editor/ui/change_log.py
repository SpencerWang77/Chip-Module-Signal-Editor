"""Compact activity log for register edits."""

from datetime import datetime

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)


class ChangeLogPanel(QFrame):
    """Right-side chronological list of bit and field-name changes."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("changeLogPanel")
        self.setFixedWidth(276)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title = QLabel("CHANGE LOG")
        title.setObjectName("logTitle")
        title_box.addWidget(title)
        self.count_label = QLabel("0 changes this session")
        self.count_label.setObjectName("logCount")
        title_box.addWidget(self.count_label)
        header.addLayout(title_box)
        header.addStretch()

        clear_button = QPushButton("Clear")
        clear_button.setObjectName("logClearButton")
        clear_button.clicked.connect(self.clear)
        header.addWidget(clear_button)
        layout.addLayout(header)

        self.empty_label = QLabel(
            "Your bit toggles and field-name edits will appear here."
        )
        self.empty_label.setObjectName("logEmpty")
        self.empty_label.setWordWrap(True)
        self.empty_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.empty_label)

        self.entries = QListWidget()
        self.entries.setObjectName("logEntries")
        self.entries.setWordWrap(True)
        self.entries.setSpacing(5)
        self.entries.hide()
        layout.addWidget(self.entries, 1)

    @property
    def count(self) -> int:
        return self.entries.count()

    def add_entry(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        item = QListWidgetItem(f"{timestamp}\n{message}")
        item.setToolTip(message)
        item.setSizeHint(QSize(0, 70))
        self.entries.insertItem(0, item)
        self.empty_label.hide()
        self.entries.show()
        self._update_count()

    def clear(self) -> None:
        self.entries.clear()
        self.entries.hide()
        self.empty_label.show()
        self._update_count()

    def _update_count(self) -> None:
        count = self.count
        noun = "change" if count == 1 else "changes"
        self.count_label.setText(f"{count} {noun} this session")
