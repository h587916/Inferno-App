from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Welcome to the Inferno App")
        title_label.setAlignment(Qt.AlignHCenter)
        font = title_label.font()
        font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Add a horizontal layout to hold the content
        content_layout = QHBoxLayout()

        # About Inferno
        about_layout = QVBoxLayout()
        links_label = QLabel(
            'You can find more information about Inferno here:<br>'
            '<a href="https://github.com/pglpm/inferno">GitHub Repository</a><br>'
            '<a href="https://pglpm.github.io/inferno/index.html">Inferno Documentation</a>'
        )
        links_label.setOpenExternalLinks(True)
        about_layout.addWidget(links_label)

        # Inferno Features
        features_layout = QVBoxLayout()
        features_label = QLabel(
            'Inferno is a Python package that provides a suite of tools for the analysis of single-cell RNA-seq data.<br>'
            'It is designed to be user-friendly, efficient, and scalable to large datasets.'
        )
        features_layout.addWidget(features_label)

        # Add the layouts to the content layout
        content_layout.addLayout(about_layout)
        content_layout.addLayout(features_layout)
        layout.addLayout(content_layout)

        self.setLayout(layout)
