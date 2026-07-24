"""Responsive square-card gallery for four-byte register modules."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..models import RegisterModule


class ModuleCard(QFrame):
    """A square, clickable summary of one four-byte register module."""

    selected = pyqtSignal(object)

    def __init__(self, module: RegisterModule) -> None:
        super().__init__()
        self.module = module
        self.setObjectName("moduleCard")
        self.setProperty("modified", False)
        self.setFixedSize(164, 164)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setToolTip(f"Open {module.name}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 15, 16, 14)
        layout.setSpacing(5)

        type_label = QLabel("4-BYTE MODULE")
        type_label.setObjectName("moduleType")
        layout.addWidget(type_label)

        self.name_label = QLabel(module.name.replace("_", "_\u200b"))
        self.name_label.setObjectName("moduleName")
        self.name_label.setWordWrap(True)
        self.name_label.setToolTip(module.name)
        layout.addWidget(self.name_label)
        layout.addStretch()

        self.address_label = QLabel(f"{module.start_address}  →  {module.end_address}")
        self.address_label.setObjectName("moduleAddress")
        layout.addWidget(self.address_label)

        self.edit_label = QLabel()
        self.edit_label.setObjectName("moduleEditCount")
        layout.addWidget(self.edit_label, 0, Qt.AlignLeft)
        self.refresh()

    def refresh(self) -> None:
        count = self.module.modified_count
        self.edit_label.setText(f"{count} EDITED" if count else "READY TO EDIT")
        self.setProperty("modified", bool(count))
        self.style().unpolish(self)
        self.style().polish(self)

    def matches(self, query: str) -> bool:
        if not query:
            return True
        searchable = " ".join(
            [
                self.module.name,
                self.module.start_address,
                self.module.end_address,
                *(register.reg_name for register in self.module.registers),
                *(
                    register_field.name
                    for register in self.module.registers
                    for register_field in register.fields
                ),
                *(
                    register_field.description
                    for register in self.module.registers
                    for register_field in register.fields
                ),
            ]
        ).lower()
        return query in searchable

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.module)
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.selected.emit(self.module)
            event.accept()
            return
        super().keyPressEvent(event)


class ModuleGallery(QWidget):
    """Scrollable responsive collection of module cards."""

    moduleSelected = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self.cards: list[ModuleCard] = []
        self.filtered_cards: list[ModuleCard] = []
        self._columns = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("moduleScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.container = QWidget()
        self.container.setObjectName("moduleContainer")
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(2, 2, 8, 2)
        self.grid.setHorizontalSpacing(14)
        self.grid.setVerticalSpacing(14)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def load_modules(self, modules: list[RegisterModule]) -> None:
        for card in self.cards:
            card.deleteLater()
        self.cards = []
        for module in modules:
            card = ModuleCard(module)
            card.selected.connect(self.moduleSelected)
            self.cards.append(card)
        self.filtered_cards = list(self.cards)
        self._columns = 0
        QTimer.singleShot(0, self._reflow)

    def apply_filter(self, query: str, edited_only: bool) -> int:
        self.filtered_cards = [
            card
            for card in self.cards
            if card.matches(query) and (not edited_only or card.module.is_modified)
        ]
        for card in self.cards:
            card.setVisible(card in self.filtered_cards)
        self._columns = 0
        self._reflow()
        return len(self.filtered_cards)

    def refresh_cards(self) -> None:
        for card in self.cards:
            card.refresh()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._reflow()

    def _reflow(self) -> None:
        available_width = max(164, self.scroll.viewport().width() - 20)
        columns = max(1, (available_width + 14) // (164 + 14))
        if columns == self._columns and self.grid.count() == len(self.filtered_cards):
            return
        self._columns = columns
        while self.grid.count():
            self.grid.takeAt(0)
        for index, card in enumerate(self.filtered_cards):
            self.grid.addWidget(card, index // columns, index % columns)
            card.show()
        self.grid.setRowStretch((len(self.filtered_cards) + columns - 1) // columns, 1)
