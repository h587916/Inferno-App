from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget, QHBoxLayout, QLabel
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
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

        # Set window title to an empty string to remove "Python"
        self.setWindowTitle(" ")

        # Set window icon to a blank icon (effectively removing the icon)
        self.setWindowIcon(QIcon("icons/inferno_symbol.png"))  # QIcon() creates an empty icon

        # Set window to be maximized (full-windowed)
        #self.showMaximized()

        # Remove the window title and icon, but keep the minimize, maximize/restore, and close buttons
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

        # Main layout that will hold the sidebar and the content area
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # No margins around the main layout


       ### SIDEBAR WITH ICON AND TEXT ###

        # Create a sidebar layout
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setSpacing(25)  # Space between sidebar buttons

        # Add a horizontal layout for the app icon and text at the top of the sidebar
        sidebar_header_layout = QHBoxLayout()
        sidebar_header_layout.setSpacing(10)
        sidebar_header_layout.setContentsMargins(0, 10, 0, 0)

        # Add the app icon (inferno_symbol.png)
        inferno_icon = QLabel()
        pixmap = QPixmap('icons/inferno_symbol.png')
        inferno_icon.setPixmap(pixmap)
        inferno_icon.setFixedSize(52, 52)  # Set icon size (adjust as needed)
        inferno_icon.setScaledContents(True)  # Ensure the image scales to fit the QLabel size
        sidebar_header_layout.addWidget(inferno_icon)

        # Add the "Inferno App" text next to the icon
        inferno_text = QLabel("Inferno App")
        inferno_text.setObjectName("sidebar_title")
        sidebar_header_layout.addWidget(inferno_text)

        # Add spacing at the end to align the content left
        sidebar_header_layout.addStretch()

        # Add the header (icon + text) to the sidebar layout
        self.sidebar_layout.addLayout(sidebar_header_layout)


        ### REST OF THE SIDEBAR ###

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
        #sidebar_title{
            color: white; 
            font-size: 20px;
            font-weight: bold;          
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
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
