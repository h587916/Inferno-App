import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget, QHBoxLayout, QLabel
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap

# Import the individual pages from their respective files
from pages.home.page import HomePage
from pages.metadata.page import MetadataPage
from pages.learn.page import LearnPage
from pages.plotting.page import PlottingPage
from pages.mutualinfo.page import MutualInfoPage
from pages.literature.page import LiteraturePage
from file_manager.file_manager import FileManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Determine the base path
        if getattr(sys, 'frozen', False):
            # If the application is frozen (packaged)
            base_path = sys._MEIPASS
        else:
            # If running in development
            base_path = os.path.abspath(".")

        ### CENTRALIZED FILE MANAGEMENT ###
        self.file_manager = FileManager()

        ### INITIAL SETUP WITH WINDOW ###
        self.setWindowTitle("Inferno App")
        ico_icon_path = os.path.join(base_path, 'icons', 'inferno_symbol.png')
        self.setWindowIcon(QIcon(ico_icon_path))
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.resize(1400, 700)

        # Main layout that will hold the sidebar and the content area
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        ### SIDEBAR WITH ICON AND TEXT ###
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setSpacing(25)

        # Sidebar header: icon and text
        sidebar_header_layout = QHBoxLayout()
        sidebar_header_layout.setSpacing(10)
        sidebar_header_layout.setContentsMargins(0, 10, 0, 0)

        inferno_icon = QLabel()
        pixmap = QPixmap(ico_icon_path)
        inferno_icon.setPixmap(pixmap)
        inferno_icon.setFixedSize(52, 52) 
        inferno_icon.setScaledContents(True) 
        sidebar_header_layout.addWidget(inferno_icon)

        inferno_text = QLabel("Inferno App")
        inferno_text.setObjectName("sidebar_title")
        sidebar_header_layout.addWidget(inferno_text)

        sidebar_header_layout.addStretch()
        self.sidebar_layout.addLayout(sidebar_header_layout)

        # Define a dictionary of pages and their corresponding buttons
        self.pages = {
            "Home": (HomePage(), QPushButton(" Home")),
            "Metadata": (MetadataPage(self.file_manager), QPushButton(" Metadata")),
            "Learn": (LearnPage(self.file_manager), QPushButton(" Learn")),
            "Plotting": (PlottingPage(self.file_manager), QPushButton(" Plotting")),
            "Mutualinfo": (MutualInfoPage(self.file_manager), QPushButton(" Mutualinfo")),
            "Literature": (LiteraturePage(), QPushButton(" Literature"))
        }

        # Create the stacked widget to hold all the pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stacked_widget")

        # Loop through the pages, add them to the stacked widget, and connect their buttons
        icon_size = QSize(24, 24)
        for page_name, (page_widget, button) in self.pages.items():
            # Add each page to the stacked widget
            self.stacked_widget.addWidget(page_widget)

            # Set the icon for the button (assuming the icon filenames match the page names)
            icon_path = os.path.join(base_path, 'icons', f'{page_name.lower()}.svg')
            button.setIcon(QIcon(icon_path))
            button.setIconSize(icon_size)

            # Connect button to switch to the corresponding page and update the active button style
            button.clicked.connect(self.make_switch_page_lambda(page_widget, button))

            # Add each button to the sidebarsssssssssss
            self.sidebar_layout.addWidget(button)

        self.sidebar_layout.addStretch()  # Push the items to the top

        # Create a sidebar widget and set its layout
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("side_menu")
        self.sidebar_widget.setLayout(self.sidebar_layout)
        self.sidebar_widget.setFixedWidth(200)  # Default expanded width


        ### MAIN LAYOUT SETUP ###
        self.main_layout.addWidget(self.sidebar_widget)
        self.main_layout.addWidget(self.stacked_widget)

        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        central_widget.setObjectName("centralwidget")
        self.setCentralWidget(central_widget)

        # Initially set the active page to the home page
        self.set_active_button(self.pages["Home"][1]) 
        self.stacked_widget.setCurrentWidget(self.pages["Home"][0])

        ### STYLESHEET ###
        self.setStyleSheet("""
        * {
            border: none;
            background-color: transparent;
            color: #000;
        }
        #centralwidget {
            background-color: #0288d1; 
        }
        #stacked_widget {
            background-color: #ffffff; 
        }
        #side_menu {
            background-color: #0288d1;
            border-radius: 0px;
        }
        #sidebar_title {
            color: white;
            font-size: 20px;
            font-weight: bold;          
        }
        QPushButton {
            padding: 10px;
            background-color: #0288d1;
            border-radius: 5px;
            font-size: 16px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #0288d1;
            border: 2px solid #ffffff;
        }
        QPushButton:pressed {
            background-color: #0288d1;
            border: 2px solid #ffffff;
        }
        QPushButton:checked {
            background-color: #0288d1;
            border: 2px solid #ffffff;
            color: #ffffff;
        }
        """)

    ### FUNCTION TO SWITCH PAGES AND SET ACTIVE BUTTON ###
    def switch_page(self, page_widget, button):
        """Switch to the given page and update the active button's style."""
        self.stacked_widget.setCurrentWidget(page_widget)
        self.set_active_button(button)

    def set_active_button(self, active_button):
        """Set the active button's style and reset other buttons."""
        # Reset all button styles to the default
        for page_name, (page_widget, button) in self.pages.items():
            button.setStyleSheet("background-color: #0288d1; color: white;")

        # Highlight the active button
        active_button.setStyleSheet("background-color: #0288d1; color: white; border: 2px solid #ffffff;")

    def make_switch_page_lambda(self, page_widget, button):
        """Create a lambda function to switch to the given page and update the active button."""
        return lambda: self.switch_page(page_widget, button)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
