import os
import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                               QComboBox, QGridLayout, QListWidget, QGroupBox, QStackedWidget, QMessageBox, QFileDialog,
                               QLabel, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from r_integration.inferno_functions import build_metadata
import json

# Load tooltips for the headers and combo boxes
with open('pages/metadata/tooltips.json', 'r') as f:
    tooltips = json.load(f)

header_tooltips = tooltips['header_tooltips']
combobox_item_tooltips = tooltips['combobox_item_tooltips']

UPLOAD_FOLDER = 'files/uploads/'
METADATA_FOLDER = 'files/metadata/'


class MetadataPage(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.selected_file_path = None
        self.selected_metadata_path = None

        # Set up the layout for the Metadata page
        layout = QVBoxLayout()

        # Create a horizontal layout for the top navigation buttons (File Management, Metadata Editing)
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Create panels for the Metadata page
        self.create_file_management_panel()
        self.create_metadata_editing_panel()

        # Set the layout for the page
        self.setLayout(layout)

        # Set default panel to file management panel
        self.stacked_widget.setCurrentWidget(self.file_management_panel)

        # Apply the stylesheet
        with open('pages/metadata/styles.qss', 'r') as f:
            style = f.read()
            self.setStyleSheet(style)

        # Connent to the FileManager signals tp update file lists
        self.file_manager.files_updated.connect(self.load_files)

        # Refresh the file lists when the page is initialized
        self.file_manager.refresh()

      
    def create_file_management_panel(self):
        """Create the panel for managing uploaded files and metadata generation."""
        self.file_management_panel = QWidget()
        layout = QGridLayout(self.file_management_panel)

        # Title label
        self.panel_title = QLabel("File Management & Metadata Generation")
        font = self.panel_title.font()
        font.setPointSize(20)
        font.setBold(True)
        self.panel_title.setFont(font)
        self.panel_title.setAlignment(Qt.AlignHCenter)
        self.panel_title.setContentsMargins(0, 20, 0, 0)
        layout.addWidget(self.panel_title, 0, 0, 1, 2)  # Spanning 2 columns

        # Add vertical spacer between title and group boxes
        vertical_spacer = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(vertical_spacer, 1, 0, 1, 2)

        # File list group box
        self.file_list_group = QGroupBox("Uploaded Files")
        self.file_list_group.setAlignment(Qt.AlignCenter)
        file_list_layout = QVBoxLayout()
        self.file_list_group.setLayout(file_list_layout)
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(lambda item: self.file_selected(item, UPLOAD_FOLDER))
        file_list_layout.addWidget(self.file_list)
        file_list_layout.setContentsMargins(20, 40, 10, 10) # top, left, bottom, right

        # Metadata list group box
        self.metadata_list_group = QGroupBox("Metadata Files")
        self.metadata_list_group.setAlignment(Qt.AlignCenter)
        metadata_list_layout = QVBoxLayout()
        self.metadata_list_group.setLayout(metadata_list_layout)
        self.metadata_list = QListWidget()
        self.metadata_list.itemClicked.connect(lambda item: self.file_selected(item, METADATA_FOLDER))
        metadata_list_layout.addWidget(self.metadata_list)
        metadata_list_layout.setContentsMargins(10, 40, 20, 10) # top, left, bottom, right

        # Buttons
        width = 250

        self.upload_button = QPushButton("Upload New CSV File")
        self.upload_button.setFixedWidth(width)
        self.upload_button.clicked.connect(self.upload_file)

        self.modify_button = QPushButton("Modify Metadata File")
        self.modify_button.setFixedWidth(width)
        self.modify_button.clicked.connect(self.modify_metadata)

        self.generate_button = QPushButton("Generate Metadata File")
        self.generate_button.setFixedWidth(width)
        self.generate_button.clicked.connect(self.process_file)

        self.delete_metadata_button = QPushButton("Delete Metadata File")
        self.delete_metadata_button.setFixedWidth(width)
        self.delete_metadata_button.clicked.connect(lambda: self.delete_file(self.metadata_list.currentItem(), METADATA_FOLDER))

        self.delete_file_button = QPushButton("Delete Uploaded File")
        self.delete_file_button.setFixedWidth(width)
        self.delete_file_button.clicked.connect(lambda: self.delete_file(self.file_list.currentItem(), UPLOAD_FOLDER))

        # Create a grid layout for the buttons
        buttons_layout = QGridLayout()
        buttons_layout.setHorizontalSpacing(0)
        buttons_layout.setVerticalSpacing(10)

        # First row
        buttons_layout.addWidget(self.upload_button, 0, 0, alignment=Qt.AlignHCenter)
        buttons_layout.addWidget(self.modify_button, 0, 1, alignment=Qt.AlignHCenter)

        # Second row
        buttons_layout.addWidget(self.generate_button, 1, 0, alignment=Qt.AlignHCenter)
        buttons_layout.addWidget(self.delete_metadata_button, 1, 1, alignment=Qt.AlignHCenter)

        # Third row
        buttons_layout.addWidget(self.delete_file_button, 2, 0, alignment=Qt.AlignHCenter)
        # Optional: Add a placeholder to maintain alignment
        buttons_layout.addItem(QSpacerItem(0, 0), 2, 1)

        # Adjusted positions for group boxes and buttons layout
        layout.addWidget(self.file_list_group, 2, 0)
        layout.addWidget(self.metadata_list_group, 2, 1)
        layout.addLayout(buttons_layout, 3, 0, 1, 2)  # Spanning 2 columns

        # Add vertical spacer at the bottom
        bottom_spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(bottom_spacer, 4, 0, 1, 2)  # Spanning 2 columns

        # Set row stretches
        layout.setRowStretch(0, 0)  # Title does not stretch
        layout.setRowStretch(1, 0)  # Spacer between title and group boxes does not stretch
        layout.setRowStretch(2, 1)  # Group boxes stretch
        layout.setRowStretch(3, 0)  # Buttons do not stretch
        layout.setRowStretch(4, 0)  # Bottom spacer does not stretch

        self.setLayout(layout)


        # Add the file management panel to the stacked widget
        self.stacked_widget.addWidget(self.file_management_panel)
        self.stacked_widget.setCurrentWidget(self.file_management_panel)


    def create_metadata_editing_panel(self):
        """Create the panel for modifying the metadata file."""
        self.metadata_editing_panel = QWidget()
        layout = QVBoxLayout(self.metadata_editing_panel)

        # Create the table widget to display the metadata
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Button to save the metadata file
        self.save_button = QPushButton("Save Metadata")
        self.save_button.clicked.connect(self.save_metadata_file)
        layout.addWidget(self.save_button)

        # Button to go back to the file management panel
        self.back_button = QPushButton("Back to File Management")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        # Add the metadata editing panel to the stacked widget
        self.stacked_widget.addWidget(self.metadata_editing_panel)

    ### HELPER FUNCTIONS ###
    
    def load_files(self):
        """Load the list of uploaded files from the FileManager."""
        self.file_list.clear()
        if self.file_manager.uploaded_files:
            self.file_list.addItems(self.file_manager.uploaded_files)
        else:
            self.file_list.addItem("No files uploaded yet.")

        """Load the list of metadata files from the FileManager."""
        self.metadata_list.clear()
        if self.file_manager.metadata_files:
            self.metadata_list.addItems(self.file_manager.metadata_files)
        else:
            self.metadata_list.addItem("No metadata files generated yet.")

    def upload_file(self):
        """Open file dialog to upload CSV and refresh the file list."""
        file_dialog = QFileDialog()
        csv_file, _ = file_dialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if csv_file:
            self.file_manager.add_file(csv_file, UPLOAD_FOLDER)

    def delete_file(self, item, folder):
        """Delete the selected uploaded file using the FileManager."""
        try:
            file_name = item.text()
            reply = QMessageBox.question(self, "Delete File", f"Are you sure you want to delete {file_name}?")
            if reply == QMessageBox.Yes:
                self.file_manager.delete_file(file_name, folder)
        except AttributeError:
             QMessageBox.warning(self, "No File Selected", "Please select a file to delete.")

    def file_selected(self, item, folder):
        """Handle selecting a file from the uploaded files list."""
        file_name = item.text()
        
        if folder == UPLOAD_FOLDER:
            self.selected_file_path = os.path.join(folder, file_name)

        if folder == METADATA_FOLDER:
            self.selected_metadata_path = os.path.join(folder, file_name)

    def process_file(self):
        """Generate metadata for the selected uploaded file."""
        if self.selected_file_path:
            try:
                # Generate metadata using the inferno function
                self.metadata_file_path = build_metadata(self.selected_file_path, f"files/metadata/metadata_{os.path.basename(self.selected_file_path)}")
                self.display_metadata(self.metadata_file_path)
                self.stacked_widget.setCurrentWidget(self.metadata_editing_panel)
                QMessageBox.information(self, "Success", "Metadata generated successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate metadata: {str(e)}")
        else:
            QMessageBox.warning(self, "No File Selected", "Please select a file to generate metadata.")

    def modify_metadata(self):
        """Display the metadata editing panel to modify an existing metadata file."""
        if self.selected_metadata_path:
            self.display_metadata(self.selected_metadata_path)
            self.stacked_widget.setCurrentWidget(self.metadata_editing_panel)
        else:
            QMessageBox.warning(self, "No Metadata Selected", "Please select a metadata file to modify.")

    def display_metadata(self, metadata_file_path):
        """Display metadata in the table widget with tooltips."""
        metadata_df = pd.read_csv(metadata_file_path)
        
        # Set row and column count based on DataFrame
        self.table_widget.setRowCount(len(metadata_df))
        self.table_widget.setColumnCount(len(metadata_df.columns))
        self.table_widget.setHorizontalHeaderLabels(metadata_df.columns)

        # Set tooltips for headers
        for i, column_name in enumerate(metadata_df.columns):
            header_item = self.table_widget.horizontalHeaderItem(i)
            if column_name in header_tooltips:  # Use header_tooltips from the JSON file
                header_item.setToolTip(header_tooltips[column_name])

        # Fill the table with data from the DataFrame and set tooltips for the cells
        for i, row in metadata_df.iterrows():
            for j, value in enumerate(row):
                column_name = metadata_df.columns[j]

                # If the column is "type", use a combo box
                if column_name == "type":
                    combo = QComboBox()
                    combo.addItems(["nominal", "ordinal", "continuous"])
                    combo.setCurrentText(str(value))

                    # Set tooltips for the combo box items
                    combo.setItemData(0, combobox_item_tooltips["nominal"], Qt.ToolTipRole)
                    combo.setItemData(1, combobox_item_tooltips["ordinal"], Qt.ToolTipRole)
                    combo.setItemData(2, combobox_item_tooltips["continuous"], Qt.ToolTipRole)

                    self.table_widget.setCellWidget(i, j, combo)
                else:
                    # Set regular text items for other columns
                    item = QTableWidgetItem(str(value))
                    self.table_widget.setItem(i, j, item)


    def save_metadata_file(self):
        """Save the modified metadata file."""
        if hasattr(self, 'selected_metadata_path'):
            metadata_file_path = self.selected_metadata_path
        elif hasattr(self, 'selected_file_path'):
            metadata_file_path = os.path.join('files/metadata', f"metadata_{os.path.basename(self.selected_file_path)}")
        else:
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

    def go_back(self):
        """Return to the file management panel."""
        self.stacked_widget.setCurrentWidget(self.file_management_panel)