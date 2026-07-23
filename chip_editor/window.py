"""Main window and page navigation."""

from pathlib import Path

from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from .constants import APP_NAME
from .models import WorkbookData
from .ui.editor_page import EditorPage
from .ui.upload_page import UploadPage


class MainWindow(QMainWindow):
    """Top-level application window containing the two-step workflow."""

    def __init__(self, project_dir: Path) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1440, 900)
        self.setMinimumSize(1280, 720)

        self.pages = QStackedWidget()
        self.upload_page = UploadPage(project_dir)
        self.editor_page = EditorPage()
        self.pages.addWidget(self.upload_page)
        self.pages.addWidget(self.editor_page)
        self.setCentralWidget(self.pages)

        self.upload_page.workbookReady.connect(self.open_editor)
        self.editor_page.backRequested.connect(
            lambda: self.pages.setCurrentWidget(self.upload_page)
        )

    def open_editor(self, data: WorkbookData) -> None:
        self.editor_page.load_data(data)
        self.pages.setCurrentWidget(self.editor_page)
