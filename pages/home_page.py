from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        # Create a main layout for centering
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 20, 0, 0)  # Move content up by adjusting the top margin

        # Create a layout for the actual content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)  # Reduce space between elements
        content_layout.setAlignment(Qt.AlignTop)

        # Add a welcome label
        welcome_label = QLabel("<h1>Welcome to the Inferno App</h1>")
        welcome_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(welcome_label)

        # Add clickable links to the GitHub repo and documentation
        links_label = QLabel(
            'You can find more information about Inferno here:<br>'
            '<a href="https://github.com/pglpm/inferno">GitHub Repository</a><br>'
            '<a href="https://pglpm.github.io/inferno/index.html">Inferno Documentation</a>'
        )
        links_label.setOpenExternalLinks(True)  # Allow the links to be clicked and opened in a browser
        content_layout.addWidget(links_label)

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
