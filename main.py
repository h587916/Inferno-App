from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget, QHBoxLayout
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
import sys

# Import the individual pages from their respective files
from pages.home_page import HomePage
from pages.metadata_page import MetadataPage
from pages.learn_page import LearnPage
from pages.plotting_page import PlottingPage
from pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ### INITIAL SETUP WITH WINDOW ###

        # Set main window properties
        self.setWindowTitle("Inferno App")
        self.setGeometry(200, 200, 1200, 800)

        # Main layout that will hold the sidebar and the content area
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # No margins around the main layout


        ### SIDEBAR WITH BUTTONS AND ICONS ###

        # Create a sidebar layout
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setSpacing(25)  # Space between sidebar buttons

        # Create buttons for the sidebar menu with .svg icons
        self.home_button = QPushButton(" Home")
        self.metadata_button = QPushButton(" Metadata")
        self.learn_button = QPushButton(" Learn")
        self.plotting_button = QPushButton(" Plotting")
        self.settings_button = QPushButton(" Settings")

        # Set .svg icons for buttons (replace with actual file paths)
        self.home_button.setIcon(QIcon('icons/home.svg'))
        self.metadata_button.setIcon(QIcon('icons/metadata.svg'))
        self.learn_button.setIcon(QIcon('icons/learn.svg'))
        self.plotting_button.setIcon(QIcon('icons/plotting.svg'))
        self.settings_button.setIcon(QIcon('icons/settings.svg'))

        # Set icon sizes
        icon_size = QSize(24, 24)
        self.home_button.setIconSize(icon_size)
        self.metadata_button.setIconSize(icon_size)
        self.learn_button.setIconSize(icon_size)
        self.plotting_button.setIconSize(icon_size)
        self.settings_button.setIconSize(icon_size)

        # Add the buttons to the sidebar layout
        self.sidebar_layout.addWidget(self.home_button)
        self.sidebar_layout.addWidget(self.metadata_button)
        self.sidebar_layout.addWidget(self.learn_button)
        self.sidebar_layout.addWidget(self.plotting_button)
        self.sidebar_layout.addWidget(self.settings_button)
        self.sidebar_layout.addStretch()  # Push the items to the top

        # Create a sidebar widget and set its layout
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("side_menu")
        self.sidebar_widget.setLayout(self.sidebar_layout)
        self.sidebar_widget.setFixedWidth(200)  # Default expanded width


        ### MANAGE DIFFERENT PAGES ON BUTTON CLICKS ###

        # Create a stacked widget to display different pages based on button clicks
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stacked_widget")

        # Create and add pages to the stacked widget
        self.home_page = HomePage()
        self.metadata_page = MetadataPage()
        self.learn_page = LearnPage()
        self.plotting_page = PlottingPage()
        self.settings_page = SettingsPage()

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.metadata_page)
        self.stacked_widget.addWidget(self.learn_page)
        self.stacked_widget.addWidget(self.plotting_page)
        self.stacked_widget.addWidget(self.settings_page)

        # Connect sidebar buttons to change the displayed page
        self.home_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.home_page))
        self.metadata_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.metadata_page))
        self.learn_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.learn_page))
        self.plotting_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.plotting_page))
        self.settings_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_page))


        ### 

        # Add the sidebar and main content area to the main layout
        self.main_layout.addWidget(self.sidebar_widget)
        self.main_layout.addWidget(self.stacked_widget)

        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        central_widget.setObjectName("centralwidget")
        self.setCentralWidget(central_widget)


        ### STYLESHEET ###

        # Apply the updated stylesheet for the new color scheme
        self.setStyleSheet("""
        *{
            border: none;
            background-color: transparent;
            color: #000;
        }
        #centralwidget{
            background-color: #0288d1;  /* Set the background to white */
        }
        #stacked_widget{
            background-color: #ffffff;  /* Make sure the stacked widget also has a white background */
        }
        #side_menu{
            background-color: #0288d1;  /* Solid blue sidebar with no gaps */
            border-radius: 0px;
        }
        QPushButton{
            padding: 10px;
            background-color: #0288d1;
            border-radius: 5px;
            font-size: 16px;
            color: #ffffff;
        }
        QPushButton:hover{
            background-color: #0277bd;
        }
        QPushButton:pressed{
            background-color: #01579b;
        }
        QPushButton::icon {
            color: red;
        }
        """)

        # Initial state of sidebar (expanded)
        self.sidebar_expanded = True


    ### HELPER FUNCTIONS ###

    def toggle_sidebar(self):
        """Toggle between the expanded and minimized states of the sidebar."""
        if self.sidebar_expanded:
            # Minimize the sidebar: hide text, only show icons
            self.sidebar_widget.setFixedWidth(50)
            self.home_button.setText("")
            self.metadata_button.setText("")
            self.learn_button.setText("")
            self.plotting_button.setText("")
            self.settings_button.setText("")
        else:
            # Expand the sidebar: show text and icons
            self.sidebar_widget.setFixedWidth(200)
            self.home_button.setText(" Home")
            self.metadata_button.setText(" Metadata")
            self.learn_button.setText(" Learn")
            self.plotting_button.setText(" Plotting")
            self.settings_button.setText(" Settings")
        
        self.sidebar_expanded = not self.sidebar_expanded


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
