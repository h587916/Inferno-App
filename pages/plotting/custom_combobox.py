from PySide6.QtWidgets import QComboBox

class CustomComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()