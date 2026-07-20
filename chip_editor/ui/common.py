"""Reusable Qt widgets for the upload and register editor screens."""

from __future__ import annotations

from typing import Iterable, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QAbstractButton,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..constants import BIT_COLUMN_COUNT
from ..models import RegisterByte, RegisterField


class BrandMark(QWidget):
    """Compact circuit-node logo drawn natively with Qt."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(34, 34)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#112C36"))
        painter.drawRoundedRect(1, 1, 32, 32, 10, 10)
        painter.setBrush(QColor("#6DE0BD"))
        nodes = ((10, 10, 3), (22, 10, 3), (10, 22, 3), (22, 22, 3), (16, 16, 4))
        for x, y, radius in nodes:
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)


class DropZone(QFrame):
    """Drag-and-drop area that accepts Excel workbooks."""

    fileDropped = pyqtSignal(str)
    browseRequested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(244)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(9)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("XLSX")
        icon.setObjectName("fileIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(62, 72)
        layout.addWidget(icon, 0, Qt.AlignHCenter)

        title = QLabel("Drop your register workbook here")
        title.setObjectName("dropTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        helper = QLabel("or choose a .xlsx file from your computer")
        helper.setObjectName("mutedText")
        helper.setAlignment(Qt.AlignCenter)
        layout.addWidget(helper)

        browse = QPushButton("Choose workbook")
        browse.setObjectName("secondaryButton")
        browse.setCursor(Qt.PointingHandCursor)
        browse.clicked.connect(self.browseRequested)
        layout.addWidget(browse, 0, Qt.AlignHCenter)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.browseRequested.emit()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls() and any(
            url.toLocalFile().lower().endswith(".xlsx") for url in event.mimeData().urls()
        ):
            event.acceptProposedAction()
            self._set_dragging(True)

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        self._set_dragging(False)

    def dropEvent(self, event) -> None:  # noqa: N802
        self._set_dragging(False)
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        valid = next((path for path in paths if path.lower().endswith(".xlsx")), None)
        if valid:
            self.fileDropped.emit(valid)
            event.acceptProposedAction()

    def _set_dragging(self, dragging: bool) -> None:
        self.setProperty("dragging", dragging)
        self.style().unpolish(self)
        self.style().polish(self)


class BitButton(QAbstractButton):
    """A circle that visually represents a single zero/one bit."""

    def __init__(self, bit_number: int, checked: bool, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.bit_number = bit_number
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(36, 36)
        self.setAccessibleName(f"Bit {bit_number}")
        self._update_tooltip(checked)
        self.toggled.connect(self._update_tooltip)

    def _update_tooltip(self, checked: bool) -> None:
        self.setToolTip(f"Bit {self.bit_number}: {'1' if checked else '0'} — click to toggle")
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(4, 4, -4, -4)

        if self.isChecked():
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#20B88A" if not self.underMouse() else "#16A27A"))
            painter.drawEllipse(rect)
            painter.setPen(QPen(QColor("#FFFFFF"), 2))
            painter.drawLine(
                rect.center().x() - 5,
                rect.center().y(),
                rect.center().x() - 1,
                rect.center().y() + 4,
            )
            painter.drawLine(
                rect.center().x() - 1,
                rect.center().y() + 4,
                rect.center().x() + 6,
                rect.center().y() - 5,
            )
        else:
            border = QColor("#8CA1A8" if not self.underMouse() else "#20B88A")
            painter.setPen(QPen(border, 2))
            painter.setBrush(QColor("#FFFFFF"))
            painter.drawEllipse(rect)


FIELD_COLORS = (
    ("#E4F7F0", "#14785E"),
    ("#E8F1FD", "#315E98"),
    ("#F4EDFF", "#7450A8"),
    ("#FFF1DF", "#97632B"),
    ("#E6F6F8", "#267481"),
)


class FieldLabel(QLabel):
    """A colored field chip aligned below the bits it occupies."""

    def __init__(self, register_field: RegisterField, color_index: int) -> None:
        super().__init__(register_field.name)
        background, foreground = FIELD_COLORS[color_index % len(FIELD_COLORS)]
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setFixedHeight(27)
        self.setToolTip(
            f"{register_field.name}\nBits {register_field.start_bit}–{register_field.end_bit}\n"
            f"Default 0x{register_field.default_value:X}"
        )
        self.setStyleSheet(
            f"background: {background}; color: {foreground}; border-radius: 6px; "
            "padding: 0 6px; font-size: 10px; font-weight: 600;"
        )


class BitGrid(QWidget):
    """Eight bit circles and an aligned field map."""

    bitChanged = pyqtSignal(int, bool)

    def __init__(self, register: RegisterByte) -> None:
        super().__init__()
        self.buttons: list[BitButton] = []
        self.field_labels: list[tuple[RegisterField, FieldLabel]] = []
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(4)
        for column in range(BIT_COLUMN_COUNT):
            grid.setColumnStretch(column, 1)
            grid.setColumnMinimumWidth(column, 42)

        for display_index, bit_number in enumerate(range(7, -1, -1)):
            number = QLabel(str(bit_number))
            number.setObjectName("bitNumber")
            number.setAlignment(Qt.AlignCenter)
            grid.addWidget(number, 0, display_index)
            button = BitButton(bit_number, bool(register.bits[display_index]))
            button.toggled.connect(
                lambda checked, index=display_index: self.bitChanged.emit(index, checked)
            )
            self.buttons.append(button)
            grid.addWidget(button, 1, display_index, Qt.AlignHCenter)

        field_by_start = {7 - item.start_bit: item for item in register.fields}
        position = 0
        color_index = 0
        while position < BIT_COLUMN_COUNT:
            register_field = field_by_start.get(position)
            if register_field:
                width = register_field.width
                field_label = FieldLabel(register_field, color_index)
                self.field_labels.append((register_field, field_label))
                grid.addWidget(field_label, 2, position, 1, width)
                color_index += 1
                position += width
            else:
                next_start = min(
                    (key for key in field_by_start if key > position),
                    default=BIT_COLUMN_COUNT,
                )
                width = next_start - position
                reserved = QLabel("reserved" if width > 1 else "·")
                reserved.setObjectName("reservedField")
                reserved.setAlignment(Qt.AlignCenter)
                reserved.setMinimumWidth(0)
                reserved.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
                reserved.setFixedHeight(27)
                grid.addWidget(reserved, 2, position, 1, width)
                position += width

    def set_bits(self, bits: Iterable[int]) -> None:
        for button, value in zip(self.buttons, bits):
            button.blockSignals(True)
            button.setChecked(bool(value))
            button.blockSignals(False)
            button.update()


class RegisterRow(QFrame):
    """One address row containing identity, bit controls, fields, and values."""

    changed = pyqtSignal(object)

    def __init__(self, register: RegisterByte) -> None:
        super().__init__()
        self.register = register
        self.setObjectName("registerRow")
        self.setProperty("modified", False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(24)

        identity = QWidget()
        identity.setFixedWidth(206)
        identity_layout = QVBoxLayout(identity)
        identity_layout.setContentsMargins(0, 0, 0, 0)
        identity_layout.setSpacing(4)

        address = QLabel(register.hex_addr)
        address.setObjectName("addressBadge")
        identity_layout.addWidget(address, 0, Qt.AlignLeft)
        name = QLabel(register.reg_name)
        name.setObjectName("registerName")
        name.setToolTip(register.reg_name)
        identity_layout.addWidget(name)
        group = QLabel(register.reg32_name or "Ungrouped byte")
        group.setObjectName("rowSecondary")
        group.setToolTip(register.reg32_name)
        identity_layout.addWidget(group)
        identity_layout.addStretch()
        layout.addWidget(identity)

        self.bit_grid = BitGrid(register)
        self.bit_grid.bitChanged.connect(self._bit_changed)
        layout.addWidget(self.bit_grid, 1)

        summary = QWidget()
        summary.setFixedWidth(230)
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(5)
        field_count = len(register.fields)
        summary_title = QLabel(f"{field_count} FIELD{'S' if field_count != 1 else ''}")
        summary_title.setObjectName("summaryTitle")
        summary_layout.addWidget(summary_title)
        field_lines = [f"{item.range_label}  {item.name}" for item in register.fields]
        visible_lines = field_lines[:3]
        if len(field_lines) > 3:
            visible_lines.append(f"+ {len(field_lines) - 3} more fields")
        details = QLabel("\n".join(visible_lines) if visible_lines else "No named fields · reserved byte")
        details.setObjectName("fieldSummary")
        details.setToolTip("\n".join(field_lines))
        details.setWordWrap(False)
        summary_layout.addWidget(details)
        summary_layout.addStretch()
        layout.addWidget(summary)

        values = QWidget()
        values.setFixedWidth(92)
        values_layout = QVBoxLayout(values)
        values_layout.setContentsMargins(0, 0, 0, 0)
        values_layout.setSpacing(4)
        current_label = QLabel("VALUE")
        current_label.setObjectName("summaryTitle")
        values_layout.addWidget(current_label, 0, Qt.AlignRight)
        self.value_label = QLabel(f"0x{register.value:02X}")
        self.value_label.setObjectName("currentValue")
        values_layout.addWidget(self.value_label, 0, Qt.AlignRight)
        default_label = QLabel(f"default  0x{register.default_value:02X}")
        default_label.setObjectName("rowSecondary")
        values_layout.addWidget(default_label, 0, Qt.AlignRight)
        self.changed_pill = QLabel("EDITED")
        self.changed_pill.setObjectName("changedPill")
        self.changed_pill.hide()
        values_layout.addWidget(self.changed_pill, 0, Qt.AlignRight)
        values_layout.addStretch()
        layout.addWidget(values)

    def _bit_changed(self, display_index: int, checked: bool) -> None:
        self.register.bits[display_index] = int(checked)
        self.refresh()
        self.changed.emit(self)

    def refresh(self) -> None:
        self.value_label.setText(f"0x{self.register.value:02X}")
        self.changed_pill.setVisible(self.register.is_modified)
        self.setProperty("modified", self.register.is_modified)
        self.style().unpolish(self)
        self.style().polish(self)

    def reset(self) -> None:
        self.register.bits = list(self.register.original_bits)
        self.bit_grid.set_bits(self.register.bits)
        self.refresh()
        self.changed.emit(self)

    def matches(self, query: str) -> bool:
        if not query:
            return True
        haystack = " ".join(
            [
                self.register.hex_addr,
                self.register.dec_addr,
                self.register.reg_name,
                self.register.reg32_name,
                *(item.name for item in self.register.fields),
            ]
        ).lower()
        return query in haystack
