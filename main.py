import sys
import os
import platform

system_platform = platform.system()
if system_platform == 'Darwin':
    if 'R_HOME' not in os.environ or not os.environ['R_HOME']:
        os.environ['R_HOME'] = 'Library/Frameworks/R.framework/Resources'
    os.environ['PATH'] += ':/usr/local/bin:/opt/homebrew/bin'

elif system_platform == 'Windows':
    if 'R_HOME' not in os.environ or not os.environ['R_HOME']:
        os.environ['R_HOME'] = 'C:\\Program Files\\R\\R-4.4.2'

elif system_platform == 'Linux':
    if 'R_HOME' not in os.environ or not os.environ['R_HOME']:
        os.environ['R_HOME'] = '/usr/lib/R'
    os.environ['PATH'] += ':/usr/bin:/usr/local/bin'


from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget, QHBoxLayout, QLabel, QStyle, QProxyStyle, QStyleOptionViewItem
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap, QPalette, QColor

# Import the individual pages from their respective files
from pages.home.page import HomePage
from pages.metadata.page import MetadataPage
from pages.learn.page import LearnPage
from pages.plotting.page import PlottingPage
from pages.mutualinfo.page import MutualInfoPage
from pages.literature.page import LiteraturePage
from file_manager.file_manager import FileManager


class CustomFusionStyle(QProxyStyle):
    def drawControl(self, element, option, painter, widget):
        if element == QStyle.CE_ItemViewItem:
            if isinstance(option, QStyleOptionViewItem):
                option.backgroundBrush = QColor("white")
                option.palette.setColor(QPalette.Text, QColor("black"))
                option.palette.setColor(QPalette.Base, QColor("white"))
        super().drawControl(element, option, painter, widget)

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint in {QStyle.SH_ComboBox_Popup, QStyle.SH_ComboBox_UseNativePopup}:
            return 0  # Disable native pop-ups on all platforms
        return super().styleHint(hint, option, widget, returnData)
    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        self.file_manager = FileManager()

        self.setWindowTitle("Inferno App")
        ico_icon_path = os.path.join(base_path, 'icons', 'inferno_symbol.png')
        self.setWindowIcon(QIcon(ico_icon_path))
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.resize(1400, 700)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setSpacing(25)
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

        self.pages = {
            "Home": (HomePage(), QPushButton(" Home")),
            "Metadata": (MetadataPage(self.file_manager), QPushButton(" Metadata")),
            "Learn": (LearnPage(self.file_manager), QPushButton(" Learn")),
            "Plotting": (PlottingPage(self.file_manager), QPushButton(" Plotting")),
            "Mutualinfo": (MutualInfoPage(self.file_manager), QPushButton(" Mutualinfo")),
            "Literature": (LiteraturePage(), QPushButton(" Literature"))
        }

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stacked_widget")

        icon_size = QSize(24, 24)
        for page_name, (page_widget, button) in self.pages.items():
            self.stacked_widget.addWidget(page_widget)

            icon_path = os.path.join(base_path, 'icons', f'{page_name.lower()}.svg')
            button.setIcon(QIcon(icon_path))
            button.setIconSize(icon_size)

            button.clicked.connect(self.make_switch_page_lambda(page_widget, button))

            self.sidebar_layout.addWidget(button)

        self.sidebar_layout.addStretch() 

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("side_menu")
        self.sidebar_widget.setLayout(self.sidebar_layout)
        self.sidebar_widget.setFixedWidth(200) 

        self.main_layout.addWidget(self.sidebar_widget)
        self.main_layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        central_widget.setObjectName("centralwidget")
        self.setCentralWidget(central_widget)

        self.set_active_button(self.pages["Home"][1]) 
        self.stacked_widget.setCurrentWidget(self.pages["Home"][0])

        # Apply the stylesheet
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

    ### HELPER FUNCTIONS ###
    def switch_page(self, page_widget, button):
        """Switch to the given page and update the active button's style."""
        self.stacked_widget.setCurrentWidget(page_widget)
        self.set_active_button(button)

    def set_active_button(self, active_button):
        """Set the active button's style and reset other buttons."""
        for page_name, (page_widget, button) in self.pages.items():
            button.setStyleSheet("background-color: #0288d1; color: white;")

        active_button.setStyleSheet("background-color: #0288d1; color: white; border: 2px solid #ffffff;")

    def make_switch_page_lambda(self, page_widget, button):
        """Create a lambda function to switch to the given page and update the active button."""
        return lambda: self.switch_page(page_widget, button)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    custom_style = CustomFusionStyle("Fusion")
    app.setStyle(custom_style)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("white"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())