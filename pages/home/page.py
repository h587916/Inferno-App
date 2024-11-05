import os
import sys
import importlib.resources
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        # Determine the base path
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            # Running in a normal Python environment
            base_path = os.path.abspath('.')

        layout = QVBoxLayout()

        # Title label
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 20) # left, top, right, bottom
        title_label = QLabel("Welcome to the Inferno App!")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignHCenter)
        title_layout.addWidget(title_label)
        layout.addLayout(title_layout)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(50, 0, 50, 0) # left, top, right, bottom

        # About Inferno
        about_layout = QVBoxLayout()
        about_layout.setContentsMargins(0, 0, 50, 0) # left, top, right, bottom
        about_title = QLabel("About Inferno")
        about_title.setObjectName("subtitle")
        about_layout.addWidget(about_title)
        about_text = self.read_text_file('about.txt')
        links_label = QLabel(about_text)
        links_label.setWordWrap(True)
        links_label.setOpenExternalLinks(True)
        links_label.setTextFormat(Qt.RichText)
        about_layout.addWidget(links_label)
        about_layout.addSpacing(20)

        image_label = QLabel()
        image_path = os.path.join(base_path, 'icons', 'inferno_image.png')
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignHCenter)
        about_layout.addWidget(image_label)

        about_layout.addStretch()
        content_layout.addLayout(about_layout)

        # Inferno Features
        features_layout = QVBoxLayout()
        features_layout.setContentsMargins(50, 0, 0, 0) # left, top, right, bottom
        features_title = QLabel("App Features")
        features_title.setObjectName("subtitle")
        features_layout.addWidget(features_title)

        features_text = self.read_text_file('features.txt')
        features_label = QLabel(features_text)
        features_label.setWordWrap(True)
        features_label.setOpenExternalLinks(True)
        features_label.setTextFormat(Qt.RichText)
        features_layout.addWidget(features_label)
        features_layout.addStretch()
        content_layout.addLayout(features_layout)

        # Add the content layout to the main layout
        scroll_layout.addLayout(content_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

        # Apply the stylesheet
        with importlib.resources.open_text('pages.home', 'styles.qss') as f:
            style = f.read()
            self.setStyleSheet(style)

    def read_text_file(self, resource):
        """Read the content of a text file and return it as a string."""
        try:
            return importlib.resources.read_text('pages.home.content', resource, encoding='utf-8')
        except FileNotFoundError:
            return ""