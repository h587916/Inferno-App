from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        # Create a main layout for centering
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 20, 0, 0)  # Move content up by adjusting the top margin

        # Create a layout for the actual content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)  # Reduce space between elements
        content_layout.setAlignment(Qt.AlignTop)

        # Add a welcome label
        welcome_label = QLabel("<h1>Settings</h1>")
        welcome_label.setAlignment(Qt.AlignCenter)  # Center align the welcome text
        content_layout.addWidget(welcome_label)

        # Set a fixed size for the content layout
        content_container = QWidget()
        content_container.setLayout(content_layout)
        content_container.setFixedWidth(600)  # Set the width of the content (adjust as needed)

        # Add the content container to the main layout and center it
        main_layout.addStretch()
        main_layout.addWidget(content_container)
        main_layout.addStretch()

        # Set the main layout for the page
        self.setLayout(main_layout)
