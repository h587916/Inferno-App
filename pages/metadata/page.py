import os
import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, 
                               QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout, QListWidget,
                               QGroupBox, QAbstractItemView, QHeaderView, QAbstractScrollArea, QToolTip)
from PySide6.QtCore import Qt
from pages.metadata.metadata import build_metadata
import json


# Folder where uploads and metadata are stored
UPLOAD_FOLDER = 'files/uploads/'
METADATA_FOLDER = 'files/metadata/'

# Ensure the directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

with open('pages/metadata/tooltips.json', 'r') as f:
    tooltips = json.load(f)

header_tooltips = tooltips['header_tooltips']
combobox_item_tooltips = tooltips['combobox_item_tooltips']


class MetadataPage(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout for the Metadata page
        layout = QVBoxLayout()

        ### DISPLAY UPLOADED FILES ###

        # List widget to show uploaded files
        self.file_list_group = QGroupBox("Uploaded Files")
        file_list_layout = QVBoxLayout(self.file_list_group)

        file_list_layout.setContentsMargins(10, 30, 10, 10)

        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.file_selected)
        self.file_list.setFixedHeight(100)
        self.file_list.setFixedWidth(300)
        self.file_list.setFocusPolicy(Qt.NoFocus)
        file_list_layout.addWidget(self.file_list)

        layout.addWidget(self.file_list_group)

        # Add a button to upload new CSV
        self.upload_button = QPushButton("Upload New CSV File")
        self.upload_button.clicked.connect(self.upload_csv)
        layout.addWidget(self.upload_button)

        # Add a button to generate metadata file for the selected file
        self.generate_button = QPushButton("Generate Metadata File")
        self.generate_button.clicked.connect(self.process_file)
        layout.addWidget(self.generate_button)

        # Add a button to delete the selected file
        self.delete_file_button = QPushButton("Delete Uploaded File")
        self.delete_file_button.clicked.connect(lambda: self.delete_file(self.file_list.currentItem()))
        layout.addWidget(self.delete_file_button)

        # Load the list of previously uploaded files
        self.load_uploaded_files()


        ### DISPLAY METADATA FILES ###

        # List widget to show generated metadata files
        self.metadata_list_group = QGroupBox("Metadata Files")
        metadata_list_layout = QVBoxLayout(self.metadata_list_group)

        metadata_list_layout.setContentsMargins(10, 30, 10, 10)

        self.metadata_list = QListWidget()
        self.metadata_list.itemClicked.connect(self.metadata_selected)  # Connect to handle metadata selection
        self.metadata_list.setFixedHeight(100)
        self.metadata_list.setFixedWidth(300)
        self.metadata_list.setFocusPolicy(Qt.NoFocus)
        metadata_list_layout.addWidget(self.metadata_list)
 
        layout.addWidget(self.metadata_list_group)

        # Add a button to modify the existing metadata file
        self.modify_button = QPushButton("Modify Metadata File")
        self.modify_button.clicked.connect(self.modify_metadata)
        layout.addWidget(self.modify_button)

        # Add a button to delete the selected metadata file
        self.delete_metadata_button = QPushButton("Delete Metadata File")
        self.delete_metadata_button.clicked.connect(lambda: self.delete_metadata(self.metadata_list.currentItem()))
        layout.addWidget(self.delete_metadata_button)

        # Load the list of generated metadata files
        self.load_metadata_files()

        ### MODIFY METADATA FILE - TABLE WIDGET ###

        # Create a table widget to display the CSV data and metadata
        self.table_widget = QTableWidget()
        self.table_widget.setVisible(False)  # Initially hidden

        # Add the table widget to the layout
        layout.addWidget(self.table_widget)

        # Add a button to save the metadata file
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_metadata_file)
        layout.addWidget(self.save_button)
        self.save_button.setVisible(False)  # Initially hidden

        # Add a button to go back to the initial state
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)
        self.back_button.setVisible(False)  # Initially hidden

        # Set the layout for the page
        self.setLayout(layout)

        # Apply the stylesheet
        with open('pages/metadata/styles.qss', 'r') as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)


    ### HELPER FUNCTIONS ###

    def load_uploaded_files(self):
        """Load the list of previously uploaded files from the uploads folder."""
        self.file_list.clear()
        uploaded_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]
        if uploaded_files:
            self.file_list.addItems(uploaded_files)
        else:
            self.file_list.addItem("No files uploaded yet.")


    def load_metadata_files(self):
        """Load the list of metadata files from the metadata folder."""
        self.metadata_list.clear()
        metadata_files = [f for f in os.listdir(METADATA_FOLDER) if f.endswith('.csv')]
        if metadata_files:
            self.metadata_list.addItems(metadata_files)
        else:
            self.metadata_list.addItem("No metadata files generated yet.")


    def delete_file(self, item):
        """Delete the selected file from the list and the uploads folder."""
        file_name = item.text()
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        os.remove(file_path)
        self.load_uploaded_files()


    def delete_metadata(self, item):
        """Delete the selected metadata file from the list and the metadata folder."""
        metadata_file_name = item.text()
        metadata_file_path = os.path.join(METADATA_FOLDER, metadata_file_name)
        os.remove(metadata_file_path)
        self.load_metadata_files()


    def file_selected(self, item):
        """Handle selecting a file from the previously uploaded list."""
        file_name = item.text()
        if file_name == "No files uploaded yet.":
            return
        self.selected_file_path = os.path.join(UPLOAD_FOLDER, file_name)

    
    def metadata_selected(self, item):
        """Handle selecting a metadata file from the generated metadata list."""
        metadata_file_name = item.text()
        if metadata_file_name == "No metadata files generated yet.":
            return
        self.selected_metadata_path = os.path.join(METADATA_FOLDER, metadata_file_name)

    
    def save_metadata_file(self):
        """Save the modified metadata file to the metadata folder."""
        # Determine the correct file path based on whether it's a new or existing file
        if hasattr(self, 'selected_metadata_path'):
            # If modifying an existing metadata file
            metadata_file_path = self.selected_metadata_path
        elif hasattr(self, 'selected_file_path'):
            # If generating a new metadata file
            metadata_file_path = os.path.join(METADATA_FOLDER, f"metadata_{os.path.basename(self.selected_file_path)}")
        else:
            # Handle the case where neither is selected
            QMessageBox.warning(self, "Error", "No file selected to save.")
            return
        
        metadata_df = pd.DataFrame(columns=[self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())])

        for i in range(self.table_widget.rowCount()):
            row = []
            for j in range(self.table_widget.columnCount()):
                if isinstance(self.table_widget.cellWidget(i, j), QComboBox):
                    row.append(self.table_widget.cellWidget(i, j).currentText())
                else:
                    row.append(self.table_widget.item(i, j).text())
            metadata_df.loc[i] = row

        metadata_df.to_csv(metadata_file_path, index=False)
        QMessageBox.information(self, "Metadata Saved", "Metadata file saved successfully.")


    def upload_csv(self):
        """Open file dialog to upload CSV and add it to the list without processing."""
        file_dialog = QFileDialog()
        csv_file, _ = file_dialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if csv_file:
            # Save the uploaded file to the upload directory
            file_name = os.path.basename(csv_file)
            file_path = os.path.join(UPLOAD_FOLDER, file_name)

            # Save the uploaded CSV file
            data = pd.read_csv(csv_file)
            data.to_csv(file_path, index=False)  # Save a copy in the uploads folder

            # Refresh the file list after uploading
            self.load_uploaded_files()


    def process_file(self):
        """Call the inferno R function to generate metadata and display the file."""
        if hasattr(self, 'selected_file_path'):
            try:
                # Generate the metadata file
                self.metadata_file_path = build_metadata(self.selected_file_path, f"files/metadata/metadata_{os.path.basename(self.selected_file_path)}")
                
                # Display the metadata in the table
                self.display_metadata(self.metadata_file_path)

                QMessageBox.information(self, "Metadata Generated", "Metadata file generated successfully. Review the file carefully and make any necessary changes.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate metadata: {str(e)}")
        else:
            QMessageBox.warning(self, "No File Selected", "Please select a file to generate metadata.")


    def modify_metadata(self):
        """Modify the metadata file and display it in the table widget."""
        if hasattr(self, 'selected_metadata_path'):
            try:
                self.display_metadata(self.selected_metadata_path)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load metadata: {str(e)}")
        else:
            QMessageBox.warning(self, "No Metadata File Selected", "Please select a metadata file to modify.")


    def display_metadata(self, metadata_file_path):
        """Display the metadata in the table widget."""
        # Hide the file list and irrelevaant buttons
        self.file_list_group.setVisible(False)
        self.metadata_list_group.setVisible(False)
        self.upload_button.setVisible(False)
        self.generate_button.setVisible(False)
        self.modify_button.setVisible(False)
        self.delete_file_button.setVisible(False)
        self.delete_metadata_button.setVisible(False)

        # Show the table widget and relevant buttons
        self.save_button.setVisible(True)
        self.back_button.setVisible(True)
        self.table_widget.setVisible(True)
        
        # Read the generated metadata file into a pandas DataFrame
        metadata_df = pd.read_csv(metadata_file_path)
        self.table_widget.setRowCount(len(metadata_df))
        self.table_widget.setColumnCount(len(metadata_df.columns))
        self.table_widget.setHorizontalHeaderLabels(metadata_df.columns)

        # Set the column widths and row heights
        self.table_widget.verticalHeader().setDefaultSectionSize(40)
        self.table_widget.setColumnWidth(metadata_df.columns.get_loc("type"), 130)
        self.table_widget.setColumnWidth(metadata_df.columns.get_loc("name"), 130)

        # Set tooltips for the headers
        for i, column_name in enumerate(metadata_df.columns):
            header_item = self.table_widget.horizontalHeaderItem(i)
            if column_name in header_tooltips:
                header_item.setToolTip(header_tooltips[column_name])
        
        # Fill the table with data from the DataFrame and add tooltips or dropdowns for specific columns
        for i, row in metadata_df.iterrows():
            for j, value in enumerate(row):
                column_name = metadata_df.columns[j]

                # Replace 'nan' values with an empty string
                if pd.isna(value):
                    value = ""

                if column_name == "type":
                    combo = QComboBox()
                    combo.addItems(["nominal", "ordinal", "continuous"])

                    # Set the tooltip for each item in the ComboBox
                    combo.setItemData(0, combobox_item_tooltips["nominal"], Qt.ToolTipRole)
                    combo.setItemData(1, combobox_item_tooltips["ordinal"], Qt.ToolTipRole)
                    combo.setItemData(2, combobox_item_tooltips["continuous"], Qt.ToolTipRole)

                    # Set the current value in the dropdown
                    combo.setCurrentText(str(value))
                    self.table_widget.setCellWidget(i, j, combo)

                elif column_name in ["minincluded", "maxincluded"]:
                    combo = QComboBox()
                    combo.addItems(["True", "False", ""])

                    # Set the current value in the dropdown
                    combo.setCurrentText(str(value))
                    self.table_widget.setCellWidget(i, j, combo)

                else:
                    item = QTableWidgetItem(str(value))
                    self.table_widget.setItem(i, j, item)


    def go_back(self):
        """Return to the initial state after processing a file."""
        self.file_list_group.setVisible(True)
        self.metadata_list_group.setVisible(True)
        self.upload_button.setVisible(True)
        self.generate_button.setVisible(True)
        self.modify_button.setVisible(True)
        self.delete_file_button.setVisible(True)
        self.delete_metadata_button.setVisible(True)
        self.save_button.setVisible(False)
        self.table_widget.setVisible(False)
        self.table_widget.clear()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        self.load_uploaded_files()
        self.file_list.setCurrentRow(-1)
        self.back_button.setVisible(False)
