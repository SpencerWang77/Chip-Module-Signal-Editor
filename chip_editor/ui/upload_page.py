"""Workbook upload and validation screen."""

from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..constants import APP_NAME
from ..models import WorkbookData
from ..workbook_io import WorkbookFormatError, parse_register_workbook
from .common import BrandMark, DropZone


class UploadPage(QWidget):
    """First-step page for selecting and validating an Excel workbook."""

    workbookReady = pyqtSignal(object)

    def __init__(self, project_dir: Path) -> None:
        super().__init__()
        self.project_dir = project_dir
        self.loaded_data: Optional[WorkbookData] = None

        page = QVBoxLayout(self)
        page.setContentsMargins(0, 0, 0, 0)
        page.setSpacing(0)
        page.addWidget(self._build_header())

        body = QWidget()
        body.setObjectName("pageBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(70, 48, 70, 54)
        body_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        content = QWidget()
        content.setMaximumWidth(820)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        eyebrow = QLabel("NEW REGISTER MAP")
        eyebrow.setObjectName("eyebrow")
        content_layout.addWidget(eyebrow)

        title = QLabel("Bring your chip map into focus.")
        title.setObjectName("pageTitle")
        content_layout.addWidget(title)

        intro = QLabel(
            "Upload the engineering workbook you already use. Chip Module Editor reads the "
            "eight-column REG_FIELD layout and turns every byte into an editable visual register."
        )
        intro.setObjectName("pageIntro")
        intro.setWordWrap(True)
        intro.setMaximumWidth(700)
        content_layout.addWidget(intro)

        self.drop_zone = DropZone()
        self.drop_zone.browseRequested.connect(self.choose_file)
        self.drop_zone.fileDropped.connect(self.load_file)
        content_layout.addWidget(self.drop_zone)

        self.error_label = QLabel()
        self.error_label.setObjectName("errorBanner")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        content_layout.addWidget(self.error_label)

        self.file_card = self._build_file_card()
        self.file_card.hide()
        content_layout.addWidget(self.file_card)

        requirements = QFrame()
        requirements.setObjectName("requirementsCard")
        req_layout = QHBoxLayout(requirements)
        req_layout.setContentsMargins(18, 15, 18, 15)
        req_layout.setSpacing(14)
        check = QLabel("✓")
        check.setObjectName("checkBadge")
        check.setAlignment(Qt.AlignCenter)
        check.setFixedSize(28, 28)
        req_layout.addWidget(check)
        req_text = QLabel(
            "Expected format  ·  Sheet “3.register”  ·  HEX_BYTE_ADDR  ·  REG_NAME  ·  "
            "REG_FIELD spanning bits 7 → 0"
        )
        req_text.setObjectName("requirementText")
        req_text.setWordWrap(True)
        req_layout.addWidget(req_text, 1)
        content_layout.addWidget(requirements)

        sample_path = self.project_dir / "top_signal.xlsx"
        if sample_path.exists():
            sample_row = QHBoxLayout()
            sample_row.addStretch()
            sample_hint = QLabel("Want to preview the supplied format?")
            sample_hint.setObjectName("mutedText")
            sample_row.addWidget(sample_hint)
            sample = QPushButton("Use top_signal.xlsx")
            sample.setObjectName("textButton")
            sample.setCursor(Qt.PointingHandCursor)
            sample.clicked.connect(lambda: self.load_file(str(sample_path)))
            sample_row.addWidget(sample)
            content_layout.addLayout(sample_row)

        body_layout.addWidget(content)
        page.addWidget(body, 1)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("topBar")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(34, 17, 34, 17)
        layout.setSpacing(12)
        layout.addWidget(BrandMark())
        brand = QLabel(APP_NAME)
        brand.setObjectName("brandName")
        layout.addWidget(brand)
        edition = QLabel("REGISTER STUDIO")
        edition.setObjectName("editionPill")
        layout.addWidget(edition)
        layout.addStretch()
        step = QLabel("01  IMPORT   /   02  EDIT")
        step.setObjectName("stepLabel")
        layout.addWidget(step)
        return header

    def _build_file_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("fileCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 17, 20, 17)
        layout.setSpacing(16)

        badge = QLabel("✓")
        badge.setObjectName("successBadge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(42, 42)
        layout.addWidget(badge)

        text_box = QVBoxLayout()
        text_box.setSpacing(3)
        self.file_name = QLabel()
        self.file_name.setObjectName("fileName")
        text_box.addWidget(self.file_name)
        self.file_meta = QLabel()
        self.file_meta.setObjectName("mutedText")
        text_box.addWidget(self.file_meta)
        layout.addLayout(text_box, 1)

        replace = QPushButton("Replace")
        replace.setObjectName("textButton")
        replace.clicked.connect(self.choose_file)
        layout.addWidget(replace)

        continue_button = QPushButton("Open register editor  →")
        continue_button.setObjectName("primaryButton")
        continue_button.setCursor(Qt.PointingHandCursor)
        continue_button.clicked.connect(self.submit)
        layout.addWidget(continue_button)
        return card

    def choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a register workbook",
            str(self.project_dir),
            "Excel workbooks (*.xlsx)",
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str) -> None:
        self.error_label.hide()
        self.file_card.hide()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            data = parse_register_workbook(Path(path))
        except WorkbookFormatError as exc:
            self.loaded_data = None
            self.error_label.setText(f"Couldn’t import this workbook.  {exc}")
            self.error_label.show()
            return
        finally:
            QApplication.restoreOverrideCursor()

        self.loaded_data = data
        first_addr = data.registers[0].hex_addr
        last_addr = data.registers[-1].hex_addr
        self.file_name.setText(data.source_path.name)
        self.file_meta.setText(
            f"{data.sheet_name}  ·  {len(data.registers)} bytes  ·  "
            f"{first_addr}–{last_addr}  ·  format verified"
        )
        self.file_card.show()

    def submit(self) -> None:
        if self.loaded_data is not None:
            self.workbookReady.emit(self.loaded_data)
