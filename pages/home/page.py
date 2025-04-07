import os
import sys
import re
import importlib.resources
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, QFrame, QGridLayout, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath('.')

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- Main Title ---
        title_label = QLabel("Welcome to the Inferno App!")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignHCenter)
        main_layout.addWidget(title_label)

        # --- Scroll Area for Content ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(20, 20, 20, 20)

        # ----- About Inferno Section -----
        # Title for the About section (outside any colored box)
        about_title_label = QLabel("About Inferno")
        about_title_label.setObjectName("subtitle")
        scroll_layout.addWidget(about_title_label)

        # Create a horizontal layout for About content
        about_section_layout = QHBoxLayout()
        about_section_layout.setSpacing(20)

        # Left: a colored box (frame) containing the about text only
        about_text_frame = QFrame()
        about_text_frame.setObjectName("aboutTextFrame")
        about_text_frame.setFrameShape(QFrame.StyledPanel)
        about_text_frame.setLineWidth(1)
        about_text_layout = QVBoxLayout(about_text_frame)
        about_text_layout.setContentsMargins(20, 20, 20, 10) # left, top, right, bottom
        about_text = self.read_text_file('about.txt')
        about_text_label = QLabel(about_text)
        about_text_label.setWordWrap(True)
        about_text_label.setOpenExternalLinks(True)
        about_text_label.setTextFormat(Qt.RichText)
        about_text_layout.addWidget(about_text_label)
        about_text_layout.addStretch()
        about_section_layout.addWidget(about_text_frame, stretch=1)

        # Right: the image (outside any colored box)
        image_label = QLabel()
        image_path = os.path.join(base_path, 'resources', 'inferno_image.png')
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        about_section_layout.addWidget(image_label, stretch=1)

        scroll_layout.addLayout(about_section_layout)

        # Add a vertical spacer to separate the sections
        scroll_layout.addSpacing(40)

        # ----- App Features Section -----
        # Title for the App Features section (outside colored boxes)
        features_title_label = QLabel("App Features")
        features_title_label.setObjectName("subtitle")
        scroll_layout.addWidget(features_title_label)

        # Create a grid layout for the 4 feature boxes (2 columns × 2 rows)
        features_grid = QGridLayout()
        features_grid.setSpacing(20)
        features_grid.setContentsMargins(0, 0, 0, 0)

        features_text = self.read_text_file('features.txt')
        pattern = r"(?P<title>Metadata|Learn|Plotting|Mutualinfo):\s*(?P<content>.*?)(?=(?:Metadata|Learn|Plotting|Mutualinfo):|$)"
        matches = re.findall(pattern, features_text, flags=re.S)
        feature_contents = {title.strip(): content.strip() for title, content in matches}

        for i, feature in enumerate(["Metadata", "Learn", "Plotting", "Mutualinfo"]):
            feature_box = QFrame()
            feature_box.setObjectName("featureBox")
            feature_box.setFrameShape(QFrame.StyledPanel)
            feature_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            box_layout = QVBoxLayout(feature_box)
            box_layout.setContentsMargins(20, 20, 20, 10) # left, top, right, bottom
            box_layout.setSpacing(5)
            box_layout.setAlignment(Qt.AlignTop)

            # Add the feature title (inside the colored box)
            feature_title_label = QLabel(feature)
            feature_title_label.setObjectName("featureTitle")
            box_layout.addWidget(feature_title_label)

            # Add the corresponding feature information text
            feature_info_label = QLabel(feature_contents.get(feature, ""))
            feature_info_label.setWordWrap(True)
            feature_info_label.setOpenExternalLinks(True)
            feature_info_label.setTextFormat(Qt.RichText)
            box_layout.addWidget(feature_info_label)

            row = i // 2
            col = i % 2
            features_grid.addWidget(feature_box, row, col)

        scroll_layout.addLayout(features_grid)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # Apply the stylesheet
        with importlib.resources.open_text('pages.shared', 'styles.qss') as f:
            common_style = f.read()

        with importlib.resources.open_text('pages.home', 'styles.qss') as f:
            page_style = f.read()
        
        self.setStyleSheet(common_style + page_style)

    def read_text_file(self, resource):
        """Read the content of a text file and return it as a string."""
        try:
            return importlib.resources.read_text('pages.home.content', resource, encoding='utf-8')
        except FileNotFoundError:
            return ""
