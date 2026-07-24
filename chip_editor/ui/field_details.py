"""Focused description and rename panel for one selected register field."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..models import RegisterByte, RegisterField


class FieldDetailsPanel(QFrame):
    """Show AD_AA documentation and an editor for the selected field name."""

    renameRequested = pyqtSignal(object, object, str)
    descriptionChangeRequested = pyqtSignal(object, object, str)

    def __init__(self) -> None:
        super().__init__()
        self.register: Optional[RegisterByte] = None
        self.register_field: Optional[RegisterField] = None
        self.setObjectName("fieldDetailsPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 19, 22, 21)
        layout.setSpacing(15)

        heading = QHBoxLayout()
        heading.setSpacing(10)
        heading_box = QVBoxLayout()
        heading_box.setSpacing(2)
        eyebrow = QLabel("SELECTED REGISTER FIELD")
        eyebrow.setObjectName("fieldDetailsEyebrow")
        heading_box.addWidget(eyebrow)
        title = QLabel("Description & identity")
        title.setObjectName("fieldDetailsTitle")
        heading_box.addWidget(title)
        heading.addLayout(heading_box)
        heading.addStretch()
        self.match_badge = QLabel("SELECT A FIELD")
        self.match_badge.setObjectName("descriptionMatchBadge")
        heading.addWidget(self.match_badge, 0, Qt.AlignTop)
        layout.addLayout(heading)

        content = QHBoxLayout()
        content.setSpacing(24)

        identity = QWidget()
        identity.setFixedWidth(330)
        identity_layout = QVBoxLayout(identity)
        identity_layout.setContentsMargins(0, 0, 0, 0)
        identity_layout.setSpacing(8)

        name_caption = QLabel("REGISTER FIELD NAME")
        name_caption.setObjectName("fieldDetailsCaption")
        identity_layout.addWidget(name_caption)
        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        self.name_edit = QLineEdit()
        self.name_edit.setObjectName("fieldDetailsNameInput")
        self.name_edit.setPlaceholderText("Select a field above")
        self.name_edit.setClearButtonEnabled(True)
        self.name_edit.setEnabled(False)
        self.name_edit.returnPressed.connect(self._request_rename)
        self.name_edit.editingFinished.connect(self._request_rename)
        name_row.addWidget(self.name_edit, 1)
        self.apply_button = QPushButton("Apply")
        self.apply_button.setObjectName("fieldDetailsApply")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self._request_rename)
        name_row.addWidget(self.apply_button)
        identity_layout.addLayout(name_row)

        self.metadata = QLabel("Address and bit range appear after selection.")
        self.metadata.setObjectName("fieldDetailsMetadata")
        self.metadata.setWordWrap(True)
        identity_layout.addWidget(self.metadata)

        self.source = QLabel(
            "Click a colored field label below the bit circles to inspect it."
        )
        self.source.setObjectName("fieldDetailsSource")
        self.source.setWordWrap(True)
        identity_layout.addWidget(self.source)
        identity_layout.addStretch()
        content.addWidget(identity)

        divider = QFrame()
        divider.setObjectName("fieldDetailsDivider")
        divider.setFrameShape(QFrame.VLine)
        content.addWidget(divider)

        description_box = QVBoxLayout()
        description_box.setSpacing(7)
        description_header = QHBoxLayout()
        description_caption = QLabel("DESCRIPTION")
        description_caption.setObjectName("fieldDetailsCaption")
        description_header.addWidget(description_caption)
        description_header.addStretch()
        self.apply_description_button = QPushButton("Apply description")
        self.apply_description_button.setObjectName("descriptionApply")
        self.apply_description_button.setEnabled(False)
        self.apply_description_button.clicked.connect(
            self._request_description_change
        )
        description_header.addWidget(self.apply_description_button)
        description_box.addLayout(description_header)
        self.description = QPlainTextEdit()
        self.description.setPlainText(
            "Select a register field to show its description from the optional AD_AA worksheet."
        )
        self.description.setObjectName("fieldDescriptionText")
        self.description.setEnabled(False)
        self.description.setMinimumHeight(170)
        description_box.addWidget(self.description, 1)
        content.addLayout(description_box, 1)
        layout.addLayout(content)

    def clear_selection(self) -> None:
        self.register = None
        self.register_field = None
        self.name_edit.blockSignals(True)
        self.name_edit.clear()
        self.name_edit.blockSignals(False)
        self.name_edit.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.apply_description_button.setEnabled(False)
        self.metadata.setText("Address and bit range appear after selection.")
        self.source.setText(
            "Click a colored field label below the bit circles to inspect it."
        )
        self.description.setPlainText(
            "Select a register field to show its description from the optional AD_AA worksheet."
        )
        self.description.setEnabled(False)
        self._set_match_state(False, selected=False)

    def display(self, register: RegisterByte, register_field: RegisterField) -> None:
        self.register = register
        self.register_field = register_field
        self.name_edit.setEnabled(True)
        self.apply_button.setEnabled(True)
        self.refresh_from_model()

    def refresh_from_model(self) -> None:
        if self.register is None or self.register_field is None:
            return
        register_field = self.register_field
        self.name_edit.blockSignals(True)
        self.name_edit.setText(register_field.name)
        self.name_edit.blockSignals(False)
        self.metadata.setText(
            f"{self.register.hex_addr}   ·   {register_field.range_label}   ·   "
            f"{register_field.width} bit{'s' if register_field.width != 1 else ''}"
        )
        if register_field.has_description:
            self.source.setText(
                f"Matched to {register_field.description_source_name} by suffix"
                f"   ·   {register_field.description_source_sheet} row "
                f"{register_field.description_source_row}"
            )
            self.description.setEnabled(True)
            self.apply_description_button.setEnabled(True)
            self.description.setPlainText(register_field.description)
        elif register_field.description_source_sheet:
            self.source.setText(
                "No safe suffix match was found for this field in "
                f"{register_field.description_source_sheet}."
            )
            self.description.setEnabled(False)
            self.apply_description_button.setEnabled(False)
            self.description.setPlainText(
                "No description is available for this register field."
            )
        else:
            self.source.setText(
                "This workbook has no worksheet whose name contains “AD_AA”."
            )
            self.description.setEnabled(False)
            self.apply_description_button.setEnabled(False)
            self.description.setPlainText(
                "No description is available for this register field."
            )
        self._set_match_state(register_field.has_description, selected=True)

    def is_showing(self, register_field: RegisterField) -> bool:
        return self.register_field is register_field

    def _request_rename(self) -> None:
        if self.register is None or self.register_field is None:
            return
        new_name = self.name_edit.text().strip()
        if not new_name:
            self.refresh_from_model()
            return
        if new_name != self.register_field.name:
            self.renameRequested.emit(self.register, self.register_field, new_name)

    def _request_description_change(self) -> None:
        if (
            self.register is None
            or self.register_field is None
            or not self.register_field.has_description
        ):
            return
        new_description = self.description.toPlainText().strip()
        if new_description != self.register_field.description:
            self.descriptionChangeRequested.emit(
                self.register,
                self.register_field,
                new_description,
            )

    def _set_match_state(self, matched: bool, selected: bool) -> None:
        if not selected:
            text = "SELECT A FIELD"
        elif matched:
            text = "DESCRIPTION MATCHED"
        else:
            text = "NO DESCRIPTION"
        self.match_badge.setText(text)
        self.match_badge.setProperty("matched", bool(selected and matched))
        self.match_badge.setProperty("selected", selected)
        self.match_badge.style().unpolish(self.match_badge)
        self.match_badge.style().polish(self.match_badge)
