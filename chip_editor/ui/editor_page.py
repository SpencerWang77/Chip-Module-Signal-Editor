"""Module gallery and interactive four-byte register editor."""

from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
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
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..constants import APP_NAME
from ..models import (
    RegisterByte,
    RegisterField,
    RegisterModule,
    WorkbookData,
    build_register_modules,
)
from ..workbook_io import export_workbook
from .change_log import ChangeLogPanel
from .common import BrandMark, RegisterRow
from .field_details import FieldDetailsPanel
from .module_gallery import ModuleGallery


class EditorPage(QWidget):
    """Module-first register editor with a persistent session change log."""

    backRequested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.data: Optional[WorkbookData] = None
        self.modules: list[RegisterModule] = []
        self.rows: list[RegisterRow] = []
        self.row_by_register_id: dict[int, RegisterRow] = {}
        self.current_module: Optional[RegisterModule] = None

        page = QVBoxLayout(self)
        page.setContentsMargins(0, 0, 0, 0)
        page.setSpacing(0)
        page.addWidget(self._build_header())

        body = QWidget()
        body.setObjectName("editorBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 22, 24, 24)
        body_layout.setSpacing(14)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        self.modules_button = QPushButton("←  All modules")
        self.modules_button.setObjectName("secondaryButton")
        self.modules_button.clicked.connect(self.show_modules)
        self.modules_button.hide()
        title_row.addWidget(self.modules_button)

        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.editor_title = QLabel("Module map")
        self.editor_title.setObjectName("editorTitle")
        title_box.addWidget(self.editor_title)
        self.editor_subtitle = QLabel()
        self.editor_subtitle.setObjectName("rowSecondary")
        title_box.addWidget(self.editor_subtitle)
        title_row.addLayout(title_box)
        title_row.addStretch()

        self.search = QLineEdit()
        self.search.setObjectName("searchInput")
        self.search.setPlaceholderText("Search modules, registers, or fields…")
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
        self.overview_helper = QLabel()
        self.overview_helper.setObjectName("overviewText")
        overview_layout.addWidget(self.overview_helper)
        overview_layout.addStretch()
        self.modified_count = QLabel("0 EDITED")
        self.modified_count.setObjectName("modifiedCount")
        overview_layout.addWidget(self.modified_count)
        body_layout.addWidget(overview)

        workspace = QHBoxLayout()
        workspace.setSpacing(14)
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("editorContentStack")

        self.module_gallery = ModuleGallery()
        self.module_gallery.moduleSelected.connect(self.open_module)
        self.content_stack.addWidget(self.module_gallery)

        self.detail_scroll = QScrollArea()
        self.detail_scroll.setObjectName("registerScroll")
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setFrameShape(QFrame.NoFrame)
        self.detail_container = QWidget()
        self.detail_container.setObjectName("rowContainer")
        self.detail_layout = QVBoxLayout(self.detail_container)
        self.detail_layout.setContentsMargins(0, 0, 6, 0)
        self.detail_layout.setSpacing(10)
        self.field_details = FieldDetailsPanel()
        self.field_details.renameRequested.connect(self.rename_selected_field)
        self.detail_layout.addWidget(self.field_details)
        self.detail_layout.addStretch()
        self.detail_scroll.setWidget(self.detail_container)
        self.content_stack.addWidget(self.detail_scroll)

        workspace.addWidget(self.content_stack, 1)
        self.change_log = ChangeLogPanel()
        workspace.addWidget(self.change_log)
        body_layout.addLayout(workspace, 1)
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
        self.change_log.clear()

        self._remove_detail_rows()
        for row in self.rows:
            row.deleteLater()
        self.rows = []
        self.row_by_register_id = {}
        self.modules = build_register_modules(data.registers)

        for module in self.modules:
            for register in module.registers:
                row = RegisterRow(register, module.name)
                row.changed.connect(self.on_row_changed)
                row.activity.connect(self.change_log.add_entry)
                row.fieldSelected.connect(self.show_field_details)
                self.rows.append(row)
                self.row_by_register_id[id(register)] = row

        self.module_gallery.load_modules(self.modules)
        self.header_file.setText(f"{data.source_path.name}   ·   {data.sheet_name}")
        self.show_modules()

    def show_modules(self) -> None:
        self.current_module = None
        self.field_details.clear_selection()
        self.content_stack.setCurrentWidget(self.module_gallery)
        self.modules_button.hide()
        self.search.show()
        self.changed_only.show()
        self.editor_title.setText("Module map")
        mapped_bytes = sum(len(module.registers) for module in self.modules)
        self.editor_subtitle.setText(
            f"{len(self.modules)} named modules  ·  {mapped_bytes} mapped bytes"
        )
        self.overview_helper.setText(
            "Select a module card to open its four-byte register editor."
        )
        self.apply_filters()

    def open_module(self, module: RegisterModule) -> None:
        self.current_module = module
        self._remove_detail_rows()
        details_index = self.detail_layout.indexOf(self.field_details)
        for register in module.registers:
            row = self.row_by_register_id[id(register)]
            self.detail_layout.insertWidget(details_index, row)
            details_index += 1
            row.show()
        self.field_details.clear_selection()
        self.field_details.show()

        self.content_stack.setCurrentWidget(self.detail_scroll)
        self.modules_button.show()
        self.search.hide()
        self.changed_only.hide()
        self.editor_title.setText(module.name)
        self.editor_subtitle.setText(
            f"Four-byte module  ·  {module.start_address}–{module.end_address}"
        )
        self.overview_helper.setText(
            "Toggle bits, then select a field label to read its description or rename it."
        )
        self.detail_scroll.verticalScrollBar().setValue(0)
        self.update_counts()

    def _remove_detail_rows(self) -> None:
        for row in self.rows:
            if self.detail_layout.indexOf(row) >= 0:
                self.detail_layout.removeWidget(row)
                row.setParent(None)

    def on_row_changed(self, row: RegisterRow) -> None:
        self.module_gallery.refresh_cards()
        if (
            self.field_details.register is row.register
            and self.field_details.register_field is not None
        ):
            self.field_details.refresh_from_model()
        self.update_counts()
        if self.current_module is None and self.changed_only.isChecked():
            self.apply_filters()

    def update_counts(self) -> None:
        modified = sum(row.register.is_modified for row in self.rows)
        if self.current_module is not None:
            self.visible_count.setText(f"{len(self.current_module.registers)} BYTES")
        self.modified_count.setText(f"{modified} EDITED")
        self.modified_count.setProperty("active", bool(modified))
        self.modified_count.style().unpolish(self.modified_count)
        self.modified_count.style().polish(self.modified_count)
        self.reset_button.setEnabled(bool(modified))

    def apply_filters(self) -> None:
        if self.current_module is not None:
            return
        query = self.search.text().strip().lower()
        visible = self.module_gallery.apply_filter(query, self.changed_only.isChecked())
        self.visible_count.setText(f"{visible} OF {len(self.modules)} MODULES")
        self.update_counts()

    def reset_all(self) -> None:
        if not any(row.register.is_modified for row in self.rows):
            return
        answer = QMessageBox.question(
            self,
            "Reset all edits?",
            "Return every edited bit and field name to the workbook defaults?",
            QMessageBox.Reset | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        if answer == QMessageBox.Reset:
            for row in self.rows:
                if row.register.is_modified:
                    row.reset()
            self.module_gallery.refresh_cards()
            if self.current_module is None:
                self.apply_filters()
            else:
                self.update_counts()
            self.field_details.refresh_from_model()

    def show_field_details(
        self,
        register: RegisterByte,
        register_field: RegisterField,
    ) -> None:
        self.field_details.display(register, register_field)
        QTimer.singleShot(
            0,
            lambda: self.detail_scroll.ensureWidgetVisible(
                self.field_details,
                0,
                12,
            ),
        )

    def rename_selected_field(
        self,
        register: RegisterByte,
        register_field: RegisterField,
        new_name: str,
    ) -> None:
        row = self.row_by_register_id.get(id(register))
        if row is None:
            return
        row.rename_field(register_field, new_name)
        self.field_details.display(register, register_field)

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
            QMessageBox.critical(
                self,
                "Export failed",
                f"The workbook could not be exported.\n\n{exc}",
            )
        else:
            QMessageBox.information(
                self,
                "Workbook exported",
                f"Saved {Path(destination).name}\n\nEdited field names, field values, and "
                "EDITED_HEX_VALUE were written to the copy.",
            )
        finally:
            QApplication.restoreOverrideCursor()
