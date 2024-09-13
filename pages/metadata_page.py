import os
import pandas as pd
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem
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

        # Add a button
        self.upload_button = QPushButton("Upload CSV File")
        self.upload_button.clicked.connect(self.upload_csv)

        # Create table widget to display the CSV data
        self.table_widget = QTableWidget()
        self.table_widget.setVisible(False)

        # Add widgets to the layout
        layout.addWidget(self.upload_button)
        layout.addWidget(self.table_widget)

        # Set the layout for the page
        self.setLayout(layout)

    def upload_csv(self):
        # Open file dialog to upload CSV file
        file_dialog = QFileDialog()
        csv_file, _ = file_dialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if csv_file:
            # Save the uploaded file to the upload directory
            file_name = os.path.basename(csv_file)
            file_path = os.path.join(UPLOAD_FOLDER, file_name)

            # Check if the directory exists before saving
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

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
        """Function to display the metadata in the table widget"""
        # Read the generated metadata file into a pandas DataFrame
        metadata_df = pd.read_csv(metadata_file_path)

        # Set up the table widget to display the metadata
        self.table_widget.setVisible(True)
        self.table_widget.setRowCount(len(metadata_df))
        self.table_widget.setColumnCount(len(metadata_df.columns))
        self.table_widget.setHorizontalHeaderLabels(metadata_df.columns)

        # Fill the table with data from the DataFrame
        for i, row in metadata_df.iterrows():
            for j, value in enumerate(row):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(value)))

        QMessageBox.information(self, "Metadata Generated", f"Metadata file created: {metadata_file_path}")
