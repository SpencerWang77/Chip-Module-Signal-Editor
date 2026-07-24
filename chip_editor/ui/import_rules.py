"""Hover-expandable workbook contract shown on the upload page."""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class RulesInfoButton(QToolButton):
    """Keyboard-accessible information icon that reports pointer entry."""

    hoverEntered = pyqtSignal()

    def enterEvent(self, event) -> None:  # noqa: N802
        self.hoverEntered.emit()
        super().enterEvent(event)


class ImportRulesCard(QFrame):
    """Compact workbook summary that expands after hovering over its info icon."""

    expandedChanged = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.expanded = False
        self.setObjectName("requirementsCard")
        self.setMouseTracking(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        summary = QHBoxLayout()
        summary.setSpacing(13)

        self.info_button = RulesInfoButton()
        self.info_button.setObjectName("rulesInfoButton")
        self.info_button.setText("i")
        self.info_button.setToolTip("Hover or click to view workbook rules")
        self.info_button.setCursor(Qt.PointingHandCursor)
        self.info_button.setFocusPolicy(Qt.StrongFocus)
        self.info_button.setFixedSize(30, 30)
        self.info_button.hoverEntered.connect(lambda: self.set_expanded(True))
        self.info_button.clicked.connect(lambda: self.set_expanded(not self.expanded))
        summary.addWidget(self.info_button)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title = QLabel("Workbook import & export rules")
        title.setObjectName("rulesTitle")
        title_box.addWidget(title)
        subtitle = QLabel(
            "A readable “register” sheet is required; “AD_AA” descriptions are optional."
        )
        subtitle.setObjectName("requirementText")
        subtitle.setWordWrap(True)
        title_box.addWidget(subtitle)
        summary.addLayout(title_box, 1)

        hover_hint = QLabel("HOVER  ⌄")
        hover_hint.setObjectName("rulesHoverHint")
        summary.addWidget(hover_hint)
        layout.addLayout(summary)

        self.details = QWidget()
        self.details.setObjectName("rulesDetails")
        details_layout = QHBoxLayout(self.details)
        details_layout.setContentsMargins(0, 12, 0, 0)
        details_layout.setSpacing(12)
        details_layout.addWidget(
            self._rule_column(
                "1  REQUIRED REGISTER TAB",
                "The .xlsx workbook needs a sheet whose name contains “register”. "
                "That sheet must provide HEX_BYTE_ADDR, REG_NAME, and an eight-column "
                "REG_FIELD ordered from bit 7 to bit 0.",
            ),
            1,
        )
        details_layout.addWidget(
            self._rule_column(
                "2  OPTIONAL DESCRIPTIONS",
                "A sheet whose name contains “AD_AA” is optional. When present, "
                "SIGNAL_NAME and DESCRIPTION are read and matched to register fields; "
                "HEX_BYTE_ADDR improves matching.",
            ),
            1,
        )
        details_layout.addWidget(
            self._rule_column(
                "3  SAFE EXPORT",
                "Export creates a new workbook copy, updates the selected register "
                "sheet with edited names and values, and carries every other worksheet "
                "and its content into the exported file.",
            ),
            1,
        )
        self.details.hide()
        layout.addWidget(self.details)

    @staticmethod
    def _rule_column(title: str, text: str) -> QFrame:
        column = QFrame()
        column.setObjectName("ruleColumn")
        layout = QVBoxLayout(column)
        layout.setContentsMargins(12, 11, 12, 12)
        layout.setSpacing(6)
        caption = QLabel(title)
        caption.setObjectName("ruleCaption")
        caption.setWordWrap(True)
        layout.addWidget(caption)
        description = QLabel(text)
        description.setObjectName("ruleText")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(description, 1)
        return column

    def set_expanded(self, expanded: bool) -> None:
        if self.expanded == expanded:
            return
        self.expanded = expanded
        self.details.setVisible(expanded)
        hint = self.findChild(QLabel, "rulesHoverHint")
        if hint is not None:
            hint.setText("OPEN  ⌃" if expanded else "HOVER  ⌄")
        self.expandedChanged.emit(expanded)
        self.updateGeometry()

    def leaveEvent(self, event) -> None:  # noqa: N802
        self.set_expanded(False)
        super().leaveEvent(event)
