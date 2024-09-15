import os
import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, 
                               QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout)
from PySide6.QtCore import Qt
from r_integration.metadata import build_metadata

# Folder where uploads and metadata are stored
UPLOAD_FOLDER = 'files/uploads/'
METADATA_FOLDER = 'files/metadata/'

# Ensure the directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

class MetadataPage(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout for the Metadata page
        layout = QVBoxLayout()

        # Add a button to upload CSV
        self.upload_button = QPushButton("Upload CSV File")
        self.upload_button.clicked.connect(self.upload_csv)

        # Create a table widget to display the CSV data and metadata
        self.table_widget = QTableWidget()
        self.table_widget.setVisible(False)

        # Add undo and redo buttons
        self.undo_button = QPushButton("Undo")
        self.redo_button = QPushButton("Redo")
        self.undo_button.setVisible(False)
        self.redo_button.setVisible(False)

        self.undo_button.clicked.connect(self.undo_action)
        self.redo_button.clicked.connect(self.redo_action)

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Add widgets to the layout
        layout.addWidget(self.upload_button)
        layout.addWidget(self.table_widget)

        # Add undo/redo buttons in a horizontal layout
        undo_redo_layout = QHBoxLayout()
        undo_redo_layout.addWidget(self.undo_button)
        undo_redo_layout.addWidget(self.redo_button)
        layout.addLayout(undo_redo_layout)

        # Set the layout for the page
        self.setLayout(layout)

         # Apply the stylesheet to ensure white background for QComboBox and QMessageBox
        self.setStyleSheet("""
        QComboBox {
            background-color: white;
            color: black;
        }
        QMessageBox {
            background-color: white;
        }
        QTableWidget {
            background-color: white;
        }
        QTableWidget QHeaderView::section {
            background-color: white;  
            color: black;
        }
        QPushButton {
            background-color: #0288d1; 
            color: white; 
            border-radius: 5px;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #0277bd;  
        }
        QPushButton:pressed {
            background-color: #01579b; 
        }
        """)

    def upload_csv(self):
        """Open file dialog to upload CSV and generate metadata."""
        file_dialog = QFileDialog()
        csv_file, _ = file_dialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if csv_file:
            # Save the uploaded file to the upload directory
            file_name = os.path.basename(csv_file)
            file_path = os.path.join(UPLOAD_FOLDER, file_name)

            # Save the uploaded CSV file
            data = pd.read_csv(csv_file)
            data.to_csv(file_path, index=False)  # Save a copy in the uploads folder

            # Call the inferno R function to generate metadata
            try:
                metadata_file_path = build_metadata(file_path, f"files/metadata/metadata_{file_name}")
                self.display_metadata(metadata_file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate metadata: {str(e)}")

    def display_metadata(self, metadata_file_path):
        """Display the metadata in the table widget."""
        # Read the generated metadata file into a pandas DataFrame
        metadata_df = pd.read_csv(metadata_file_path)

        # Set up the table widget to display the metadata
        self.table_widget.setVisible(True)
        self.undo_button.setVisible(True)
        self.redo_button.setVisible(True)

        self.table_widget.setRowCount(len(metadata_df))
        self.table_widget.setColumnCount(len(metadata_df.columns))
        self.table_widget.setHorizontalHeaderLabels(metadata_df.columns)

        # Tooltips for specific columns
        tooltips = {
            "type": "Type of data (nominal, ordinal, continuous)",
            "datastep": "Width of gaps",
            "domainmin": "Minimum domain value",
            "domainmax": "Maximum domain value",
            "minincluded": "Is the minimum included?",
            "maxincluded": "Is the maximum included?",
            "plotmin": "Minimum value for plotting",
            "plotmax": "Maximum value for plotting"
        }

        # Fill the table with data from the DataFrame and add tooltips or dropdowns for specific columns
        for i, row in metadata_df.iterrows():
            for j, value in enumerate(row):
                column_name = metadata_df.columns[j]
                if column_name in ["type", "minincluded", "maxincluded"]:
                    combo = QComboBox()
                    if column_name == "type":
                        combo.addItems(["nominal", "ordinal", "continuous"])
                    elif column_name in ["minincluded", "maxincluded"]:
                        combo.addItems(["True", "False", ""])

                    # Set the current value in the dropdown
                    combo.setCurrentText(str(value))
                    combo.currentIndexChanged.connect(self.save_state)  # Save state when dropdown changes
                    self.table_widget.setCellWidget(i, j, combo)
                else:
                    item = QTableWidgetItem(str(value))
                    if column_name in tooltips:
                        item.setToolTip(tooltips[column_name])
                    self.table_widget.setItem(i, j, item)

        QMessageBox.information(self, "Metadata Template Generated", "Plis review the generated template carefully to make sure it does not contain errors")
        self.save_state()  # Save initial state

    def save_state(self):
        """Save the current state of the table for undo/redo functionality."""
        table_data = []
        for i in range(self.table_widget.rowCount()):
            row_data = []
            for j in range(self.table_widget.columnCount()):
                if isinstance(self.table_widget.cellWidget(i, j), QComboBox):
                    row_data.append(self.table_widget.cellWidget(i, j).currentText())
                else:
                    row_data.append(self.table_widget.item(i, j).text())
            table_data.append(row_data)

        # Save the current state to the undo stack
        self.undo_stack.append(table_data)
        self.redo_stack.clear()  # Clear the redo stack whenever a new state is saved

    def restore_state(self, state):
        """Restore a given state to the table."""
        for i, row_data in enumerate(state):
            for j, value in enumerate(row_data):
                if isinstance(self.table_widget.cellWidget(i, j), QComboBox):
                    self.table_widget.cellWidget(i, j).setCurrentText(value)
                else:
                    self.table_widget.item(i, j).setText(value)

    def undo_action(self):
        """Undo the last action."""
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())  # Save the current state to the redo stack
            previous_state = self.undo_stack[-1]  # Restore the last state
            self.restore_state(previous_state)

    def redo_action(self):
        """Redo the last undone action."""
        if self.redo_stack:
            next_state = self.redo_stack.pop()  # Restore the state from the redo stack
            self.undo_stack.append(next_state)  # Save the current state to the undo stack
            self.restore_state(next_state)
