"""Interactive register-field editor screen."""

from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..constants import APP_NAME
from ..models import WorkbookData
from ..workbook_io import export_workbook
from .common import BrandMark, RegisterRow


class EditorPage(QWidget):
    """Searchable, editable view of all register bytes in a workbook."""

    backRequested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.data: Optional[WorkbookData] = None
        self.rows: list[RegisterRow] = []

        page = QVBoxLayout(self)
        page.setContentsMargins(0, 0, 0, 0)
        page.setSpacing(0)
        page.addWidget(self._build_header())

        body = QWidget()
        body.setObjectName("editorBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 24, 28, 28)
        body_layout.setSpacing(16)

        title_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        editor_title = QLabel("Register map")
        editor_title.setObjectName("editorTitle")
        title_box.addWidget(editor_title)
        self.editor_subtitle = QLabel()
        self.editor_subtitle.setObjectName("rowSecondary")
        title_box.addWidget(self.editor_subtitle)
        title_row.addLayout(title_box)
        title_row.addStretch()

        self.search = QLineEdit()
        self.search.setObjectName("searchInput")
        self.search.setPlaceholderText("Search address, register, or field…")
        self.search.setClearButtonEnabled(True)
        self.search.setFixedWidth(330)
        self.search.textChanged.connect(self.apply_filters)
        title_row.addWidget(self.search)

        self.changed_only = QCheckBox("Edited only")
        self.changed_only.setObjectName("filterCheck")
        self.changed_only.toggled.connect(self.apply_filters)
        title_row.addWidget(self.changed_only)

        self.reset_button = QPushButton("Reset all")
        self.reset_button.setObjectName("secondaryButton")
        self.reset_button.setEnabled(False)
        self.reset_button.clicked.connect(self.reset_all)
        title_row.addWidget(self.reset_button)

        self.export_button = QPushButton("Export workbook")
        self.export_button.setObjectName("primaryButton")
        self.export_button.clicked.connect(self.export)
        title_row.addWidget(self.export_button)
        body_layout.addLayout(title_row)

        overview = QFrame()
        overview.setObjectName("overviewBar")
        overview_layout = QHBoxLayout(overview)
        overview_layout.setContentsMargins(18, 11, 18, 11)
        overview_layout.setSpacing(18)
        self.visible_count = QLabel()
        self.visible_count.setObjectName("overviewStrong")
        overview_layout.addWidget(self.visible_count)
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setObjectName("overviewDivider")
        overview_layout.addWidget(divider)
        helper = QLabel("Click a circle to toggle its bit. Field labels align to their exact bit range.")
        helper.setObjectName("overviewText")
        overview_layout.addWidget(helper)
        overview_layout.addStretch()
        self.modified_count = QLabel("0 EDITED")
        self.modified_count.setObjectName("modifiedCount")
        overview_layout.addWidget(self.modified_count)
        body_layout.addWidget(overview)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("registerScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.row_container = QWidget()
        self.row_container.setObjectName("rowContainer")
        self.row_layout = QVBoxLayout(self.row_container)
        self.row_layout.setContentsMargins(0, 0, 6, 0)
        self.row_layout.setSpacing(10)
        self.row_layout.addStretch()
        self.scroll.setWidget(self.row_container)
        body_layout.addWidget(self.scroll, 1)

        page.addWidget(body, 1)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("topBar")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 14, 28, 14)
        layout.setSpacing(12)

        back = QToolButton()
        back.setObjectName("backButton")
        back.setText("‹")
        back.setToolTip("Choose another workbook")
        back.setCursor(Qt.PointingHandCursor)
        back.clicked.connect(self.backRequested)
        layout.addWidget(back)
        layout.addWidget(BrandMark())
        brand = QLabel(APP_NAME)
        brand.setObjectName("brandName")
        layout.addWidget(brand)
        layout.addStretch()
        self.header_file = QLabel()
        self.header_file.setObjectName("headerFile")
        layout.addWidget(self.header_file)
        return header

    def load_data(self, data: WorkbookData) -> None:
        self.data = data
        self.search.clear()
        self.changed_only.setChecked(False)
        while self.row_layout.count() > 1:
            item = self.row_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.rows = []
        for register in data.registers:
            row = RegisterRow(register)
            row.changed.connect(self.on_row_changed)
            self.rows.append(row)
            self.row_layout.insertWidget(self.row_layout.count() - 1, row)

        self.header_file.setText(f"{data.source_path.name}   ·   {data.sheet_name}")
        self.editor_subtitle.setText(
            f"{len(data.registers)} addressable bytes  ·  "
            f"{data.registers[0].hex_addr}–{data.registers[-1].hex_addr}"
        )
        self.scroll.verticalScrollBar().setValue(0)
        self.update_counts()

    def on_row_changed(self, row: RegisterRow) -> None:
        self.update_counts()
        if self.changed_only.isChecked() and not row.register.is_modified:
            row.hide()

    def update_counts(self) -> None:
        modified = sum(row.register.is_modified for row in self.rows)
        visible = sum(not row.isHidden() for row in self.rows)
        self.visible_count.setText(f"{visible} OF {len(self.rows)} BYTES")
        self.modified_count.setText(f"{modified} EDITED")
        self.modified_count.setProperty("active", bool(modified))
        self.modified_count.style().unpolish(self.modified_count)
        self.modified_count.style().polish(self.modified_count)
        self.reset_button.setEnabled(bool(modified))

    def apply_filters(self) -> None:
        query = self.search.text().strip().lower()
        edited_only = self.changed_only.isChecked()
        for row in self.rows:
            visible = row.matches(query) and (not edited_only or row.register.is_modified)
            row.setVisible(visible)
        self.update_counts()

    def reset_all(self) -> None:
        if not any(row.register.is_modified for row in self.rows):
            return
        answer = QMessageBox.question(
            self,
            "Reset edited bits?",
            "Return every edited byte to the default value from the workbook?",
            QMessageBox.Reset | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        if answer == QMessageBox.Reset:
            for row in self.rows:
                if row.register.is_modified:
                    row.reset()
            self.apply_filters()

    def export(self) -> None:
        if self.data is None:
            return
        default_name = f"{self.data.source_path.stem}_edited.xlsx"
        destination, _ = QFileDialog.getSaveFileName(
            self,
            "Export edited register map",
            str(self.data.source_path.with_name(default_name)),
            "Excel workbooks (*.xlsx)",
        )
        if not destination:
            return
        if not destination.lower().endswith(".xlsx"):
            destination += ".xlsx"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            export_workbook(self.data, Path(destination))
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", f"The workbook could not be exported.\n\n{exc}")
        else:
            QMessageBox.information(
                self,
                "Workbook exported",
                f"Saved {Path(destination).name}\n\nEdited field values and "
                "EDITED_HEX_VALUE were written to the copy.",
            )
        finally:
            QApplication.restoreOverrideCursor()
