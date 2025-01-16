import importlib.resources
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class MutualInfoPage(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager

        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Work In Progress ...")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        self.setLayout(main_layout)

        # Apply the stylesheet
        with importlib.resources.open_text('pages.mutualinfo', 'styles.qss') as f:
            style = f.read()
            self.setStyleSheet(style)
