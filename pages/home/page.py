import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Welcome to the Inferno App")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title_label)
        
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(50, 50, 50, 0) # left, top, right, bottom

        # About Inferno
        about_layout = QVBoxLayout()
        about_layout.setContentsMargins(0, 0, 50, 0) # left, top, right, bottom
        about_title = QLabel("About Inferno")
        about_title.setObjectName("subtitle")
        about_layout.addWidget(about_title)
        about_text = self.read_text_file('pages/home/content/about.txt')
        links_label = QLabel(about_text)
        links_label.setOpenExternalLinks(True)
        links_label.setTextFormat(Qt.RichText)
        about_layout.addWidget(links_label)
        about_layout.addStretch()
        content_layout.addLayout(about_layout)

        # Inferno Features
        features_layout = QVBoxLayout()
        features_layout.setContentsMargins(50, 0, 0, 0) # left, top, right, bottom
        features_title = QLabel("Features")
        features_title.setObjectName("subtitle")
        features_layout.addWidget(features_title)
        features_text = self.read_text_file('pages/home/content/features.txt')
        features_label = QLabel(features_text)
        features_layout.addWidget(features_label)
        features_layout.addStretch()
        content_layout.addLayout(features_layout)

        # Inferno Guide
        guide_layout = QVBoxLayout()
        guide_layout.setContentsMargins(50, 100, 50, 20) # left, top, right, bottom
        guide_title = QLabel("Quick Start Guide")
        guide_title.setObjectName("subtitle")
        guide_layout.addWidget(guide_title)
        guide_text = self.read_text_file('pages/home/content/guide.txt')
        guide_label = QLabel(guide_text)
        guide_layout.addWidget(guide_label)

        # Add the content layout to the main layout
        guide_layout.addStretch()
        layout.addLayout(content_layout)
        layout.addLayout(guide_layout)

        self.setLayout(layout)

        # Apply the stylesheet
        with open('pages/home/styles.qss', 'r') as f:
            style = f.read()
            self.setStyleSheet(style)


    def read_text_file(self, file_path):
        """Read the content of a text file and return it as a string."""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        return ""