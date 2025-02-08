import os
import pandas as pd
from functools import partial
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                               QComboBox, QGridLayout, QListWidget, QGroupBox, QStackedWidget, QMessageBox, QFileDialog,
                               QLabel, QSpacerItem, QSizePolicy, QHBoxLayout, QLineEdit, QInputDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from r_integration.inferno_functions import build_metadata
import json
import importlib.resources
from appdirs import user_data_dir


# Load tooltips for the headers and combo boxes
with importlib.resources.open_text('pages.metadata', 'tooltips.json') as f:
    tooltips = json.load(f)

header_tooltips = tooltips['header_tooltips']
combobox_item_tooltips = tooltips['combobox_item_tooltips']

# Define the base directory paths (consistent with file_manager.py)
APP_DIR = user_data_dir("Inferno App", "inferno")
UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
METADATA_FOLDER = os.path.join(APP_DIR, 'metadata')

class CustomTableWidget(QTableWidget):
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            if not (item.flags() & Qt.ItemIsEditable):
                return
            self.editItem(item)
            editor = self.indexWidget(self.currentIndex())
            if isinstance(editor, QLineEdit):
                editor.setCursorPosition(len(editor.text()))
                editor.textChanged.connect(lambda: self.update_cell_display(editor))

    def update_cell_display(self, editor):
        """Update the cell display with the current text in the editor."""
        current_index = self.currentIndex()
        self.model().setData(current_index, editor.text())

class MetadataPage(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.selected_file_path = None
        self.selected_metadata_path = None

        layout = QVBoxLayout()

        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        self.create_file_management_panel()
        self.create_metadata_editing_panel()
        self.stacked_widget.setCurrentWidget(self.file_management_panel)

        self.setLayout(layout)

        with importlib.resources.open_text('pages.metadata', 'styles.qss') as f:
            style = f.read()
            self.setStyleSheet(style)

        self.file_manager.files_updated.connect(self.load_files)
        self.file_manager.refresh()

    def create_file_management_panel(self):
        """Create the panel for managing uploaded files and metadata generation."""
        self.file_management_panel = QWidget()
        layout = QGridLayout()

        # Title label
        self.panel_title = QLabel("File Management & Metadata Generation")
        self.panel_title.setObjectName("title")
        self.panel_title.setAlignment(Qt.AlignHCenter)
        self.panel_title.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        layout.addWidget(self.panel_title, 0, 0, 1, 2)  # Spanning 2 columns

        vertical_spacer = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(vertical_spacer, 1, 0, 1, 2)

        width = 100
        # File list group box and buttons
        self.file_list_group = QGroupBox("Uploaded CSV Files")
        self.file_list_group.setAlignment(Qt.AlignHCenter)
        file_list_layout = QVBoxLayout()
        self.file_list_group.setLayout(file_list_layout)

        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(lambda item: self.file_selected(item, UPLOAD_FOLDER))
        file_list_layout.addWidget(self.file_list)
        file_list_layout.setContentsMargins(20, 40, 10, 10) # left, top, right, bottom
        file_list_layout.setSpacing(20)

        file_button_layout = QHBoxLayout()
        file_button_layout.setAlignment(Qt.AlignHCenter)
        file_button_layout.setSpacing(20)

        self.upload_button = QPushButton("Upload")
        self.upload_button.setFixedWidth(width)
        self.upload_button.clicked.connect(self.upload_file)
        file_button_layout.addWidget(self.upload_button)

        self.generate_button = QPushButton("Generate")
        self.generate_button.setObjectName("generateButton")
        self.generate_button.setFixedWidth(width)
        self.generate_button.clicked.connect(self.process_file)
        file_button_layout.addWidget(self.generate_button)

        self.delete_file_button = QPushButton("Delete")
        self.delete_file_button.setObjectName("deleteButton")
        self.delete_file_button.setFixedWidth(width)
        self.delete_file_button.clicked.connect(lambda: self.delete_file(self.file_list.currentItem(), UPLOAD_FOLDER))
        file_button_layout.addWidget(self.delete_file_button)

        file_list_layout.addLayout(file_button_layout)

        # Metadata list group box and buttons
        self.metadata_list_group = QGroupBox("Generated Metadata Files")
        self.metadata_list_group.setAlignment(Qt.AlignHCenter)
        metadata_list_layout = QVBoxLayout()
        self.metadata_list_group.setLayout(metadata_list_layout)
        
        self.metadata_list = QListWidget()
        self.metadata_list.itemClicked.connect(lambda item: self.file_selected(item, METADATA_FOLDER))
        metadata_list_layout.addWidget(self.metadata_list)
        metadata_list_layout.setContentsMargins(10, 40, 20, 10) # left, top, right, bottom
        metadata_list_layout.setSpacing(20)

        meta_button_layout = QHBoxLayout()
        meta_button_layout.setAlignment(Qt.AlignHCenter)
        meta_button_layout.setSpacing(20)

        self.modify_button = QPushButton("Modify")
        self.modify_button.setFixedWidth(width)
        self.modify_button.clicked.connect(self.modify_metadata)
        meta_button_layout.addWidget(self.modify_button)

        self.rename_button = QPushButton("Rename")
        self.rename_button.setFixedWidth(width)
        self.rename_button.clicked.connect(self.rename_metadata)
        meta_button_layout.addWidget(self.rename_button)
        
        self.delete_metadata_button = QPushButton("Delete")
        self.delete_metadata_button.setObjectName("deleteButton")
        self.delete_metadata_button.setFixedWidth(width)
        self.delete_metadata_button.clicked.connect(lambda: self.delete_file(self.metadata_list.currentItem(), METADATA_FOLDER))
        meta_button_layout.addWidget(self.delete_metadata_button)

        metadata_list_layout.addLayout(meta_button_layout)

        # Adjusted positions for group boxes and buttons layout
        layout.addWidget(self.file_list_group, 2, 0)
        layout.addWidget(self.metadata_list_group, 2, 1)

        bottom_spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(bottom_spacer, 4, 0, 1, 2)

        self.file_management_panel.setLayout(layout)
        self.stacked_widget.addWidget(self.file_management_panel)

    def create_metadata_editing_panel(self):
        """Create the panel for modifying the metadata file."""
        self.metadata_editing_panel = QWidget()
        layout = QVBoxLayout()

        # Add title
        self.meta_title = QLabel()
        self.meta_title.setObjectName("title")
        self.meta_title.setAlignment(Qt.AlignHCenter)
        self.meta_title.setContentsMargins(0, 0, 0, 10) # left, top, right, bottom
        layout.addWidget(self.meta_title)

        # Create the table widget to display the metadata
        self.table_widget = CustomTableWidget()
        layout.addWidget(self.table_widget)

        # Create a horizontal layout for the buttons
        button_width = 100
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignHCenter)
        button_layout.setContentsMargins(0, 10, 0, 0) # left, top, right, bottom
        button_layout.setSpacing(20)

        # Button to save the metadata file
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.on_save_button_clicked)
        save_button.setFixedWidth(button_width)
        button_layout.addWidget(save_button)

        # Button to go back to the file management panel
        discard_button = QPushButton("Discard")
        discard_button.setObjectName("deleteButton")
        discard_button.clicked.connect(self.discard_changes)
        discard_button.setFixedWidth(button_width)
        button_layout.addWidget(discard_button)

        # +/- buttons for adding/removing columns
        add_column_button = QPushButton("+")
        add_column_button.setObjectName("addButton")
        add_column_button.setFixedSize(25, 25)
        add_column_button.setToolTip("Add 'V' column")
        add_column_button.clicked.connect(self.add_v_column)
        button_layout.addWidget(add_column_button)

        remove_column_button = QPushButton("-")
        remove_column_button.setObjectName("deleteButton")
        remove_column_button.setFixedSize(25, 25)
        remove_column_button.setToolTip("Remove 'V' column")
        remove_column_button.clicked.connect(self.remove_v_column)
        button_layout.addWidget(remove_column_button)

        layout.addLayout(button_layout)

        self.metadata_editing_panel.setLayout(layout)

        # Add the metadata editing panel to the stacked widget
        self.stacked_widget.addWidget(self.metadata_editing_panel)


    ####### File Management Panel Functions #######    

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
            reply = QMessageBox.question(self, "Delete File", f"Are you sure you want to delete '{file_name}'?")
            if reply == QMessageBox.Yes:
                self.file_manager.delete_file(file_name, folder)
        except AttributeError:
             QMessageBox.warning(self, "Error", "Please select a file to delete.")

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
            metadata_file_name = f"metadata_{os.path.basename(self.selected_file_path)}"
            metadata_file_path = os.path.join(METADATA_FOLDER, metadata_file_name)

            self.metadata_file_path = build_metadata(self.selected_file_path, metadata_file_path)
            self.file_manager.refresh()

            self.display_metadata(self.metadata_file_path)
            self.stacked_widget.setCurrentWidget(self.metadata_editing_panel)

            QMessageBox.information(self, "Success", "Metadata generated successfully.")
        else:
            QMessageBox.warning(self, "Error", "Please select a file to generate metadata.")

    def modify_metadata(self):
        """Display the metadata editing panel to modify an existing metadata file."""
        if self.selected_metadata_path:
            self.display_metadata(self.selected_metadata_path)
            self.stacked_widget.setCurrentWidget(self.metadata_editing_panel)
        else:
            QMessageBox.warning(self, "Error", "Please select a metadata file to modify.")

    def rename_metadata(self):
        """Rename the selected metadata file."""
        item = self.metadata_list.currentItem()
        if item:
            old_name = item.text()
            new_name, ok = QInputDialog.getText(self, "Rename File", "Enter new name:", text=old_name)
            if ok and new_name:
                if not new_name.endswith('.csv'):
                    QMessageBox.warning(self, "Error", "Metadata file names must end with '.csv'.")
                    return
                new_path = os.path.join(METADATA_FOLDER, new_name)
                if os.path.exists(new_path):
                    QMessageBox.warning(self, "Error", "A file with that name already exists.")
                    return
                else:
                    self.file_manager.rename_file(old_name, new_name, METADATA_FOLDER)
                    QMessageBox.information(self, "Success", "Metadata file renamed successfully.")
        else:
            QMessageBox.warning(self, "Error", "No file selected to rename.")

    ####### Metadata Editing Panel Functions #######

    def display_metadata(self, metadata_file_path):
        """Display metadata in the table widget with tooltips."""
        metadata_df = pd.read_csv(metadata_file_path)
        metadata_df = self.replace_empty_values(metadata_df)
        metadata_df = metadata_df.fillna('')
        
        self.table_widget.setRowCount(len(metadata_df))
        self.table_widget.setColumnCount(len(metadata_df.columns))
        self.table_widget.setHorizontalHeaderLabels(metadata_df.columns)

        header_font = QFont()
        header_font.setPointSize(16)

        header_tooltip_dict = {column_name: header_tooltips.get(column_name, '') for column_name in metadata_df.columns}

        for i, column_name in enumerate(metadata_df.columns):
            header_item = self.table_widget.horizontalHeaderItem(i)
            header_item.setFont(header_font)
            header_item.setToolTip(header_tooltip_dict[column_name])

        row_height = 40
        for row in range(self.table_widget.rowCount()):
            self.table_widget.setRowHeight(row, row_height)

        type_column = metadata_df.columns.get_loc("type")
        self.table_widget.setColumnWidth(type_column, 130)

        combobox_tooltip_dict = {
            "nominal": combobox_item_tooltips.get("nominal", ''),
            "ordinal": combobox_item_tooltips.get("ordinal", ''),
            "continuous": combobox_item_tooltips.get("continuous", '')
        }

        for i, row in metadata_df.iterrows():
            for j, value in enumerate(row):
                column_name = metadata_df.columns[j]

                if column_name == "type":
                    combo = QComboBox()
                    combo.addItems(["nominal", "ordinal", "continuous"])
                    combo.setCurrentText(str(value))
                    combo.currentIndexChanged.connect(partial(self.on_type_combobox_change, i, combo))

                    for index in range(combo.count()):
                        item_text = combo.itemText(index)
                        combo.setItemData(index, combobox_tooltip_dict[item_text], Qt.ToolTipRole)

                    self.table_widget.setCellWidget(i, j, combo)
                else:
                    item = QTableWidgetItem(str(value))
                    self.table_widget.setItem(i, j, item)
            
            initial_type = self.table_widget.cellWidget(i, type_column).currentText()
            self.update_editability(i, initial_type)

        self.meta_title.setText(f"Editing Metadata File: {os.path.basename(metadata_file_path)}")

    def replace_empty_values(self, metadata_df):
        """Replace empty values in the metadata DataFrame based on type."""
        for index, row in metadata_df.iterrows():
            row_type = row["type"]

            if row_type == "continuous":
                self.replace(row, metadata_df, index)

            elif row_type == "ordinal":
                v_columns = [col for col in metadata_df.columns if col.startswith("V")]
                v_values = [row[col] for col in v_columns if col in metadata_df.columns]

                if all(pd.isna(val) or val == "" for val in v_values):
                    self.replace(row, metadata_df, index)

        return metadata_df
    
    def replace(self, row, metadata_df, index):
        if pd.isna(row.get("domainmin", None)):
            metadata_df.at[index, "domainmin"] = float("-Inf")
        if pd.isna(row.get("domainmax", None)):
            metadata_df.at[index, "domainmax"] = float("+Inf")
        if pd.isna(row.get("datastep", None)):
            metadata_df.at[index, "datastep"] = 1.0
        if pd.isna(row.get("minincluded", None)):
            metadata_df.at[index, "minincluded"] = "False"
        if pd.isna(row.get("maxincluded", None)):
            metadata_df.at[index, "maxincluded"] = "False"

    def on_type_combobox_change(self, row_index, combo, index):
        selected_type = combo.currentText()
        self.reset_row(row_index, selected_type)
        self.update_editability(row_index, selected_type)

    def update_editability(self, row_index, selected_type):
        """Enable or disable cells based on the value of the 'type' column."""
        column_names = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]

        if selected_type == "nominal":
            editable_columns = [col for col in column_names if col.startswith("V")]
        elif selected_type == "continuous":
            editable_columns = ["datastep", "domainmin", "domainmax", "minincluded", "maxincluded"]
        else:  # "ordinal"
            editable_columns = column_names  # All columns editable

        for col_index, column_name in enumerate(column_names):
            item = self.table_widget.item(row_index, col_index)
            if item:
                if column_name in editable_columns:
                    item.setFlags(item.flags() | Qt.ItemIsEditable) # Enable editing
                else:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable) # Disable editing

    def reset_row(self, row_index, selected_type):
        """Reset irrelevant fields in the row based on the selected type."""
        column_names = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]

        if selected_type == "nominal":
            reset_columns = ["datastep", "domainmin", "domainmax", "minincluded", "maxincluded"]
        elif selected_type == "continuous":
            reset_columns = [col for col in column_names if col.startswith("V")]
        else:
            reset_columns = []  # No columns to reset for "ordinal"

        for col_index, column_name in enumerate(column_names):
            if column_name in reset_columns:
                item = self.table_widget.item(row_index, col_index)
                if item:
                    item.setText('')  # Clear the value

    def on_save_button_clicked(self):
        """Validate and save the metadata file if validation passes."""
        if self.validate_metadata():
            self.save_metadata_file()
    
    def validate_metadata(self):
        column_names = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
        type_column_index = column_names.index("type")

        v_columns = [i for i, col in enumerate(column_names) if col.startswith("V")]
        continuous_columns = ["datastep", "domainmin", "domainmax", "minincluded", "maxincluded"]
        continuous_indices = [column_names.index(col) for col in continuous_columns if col in column_names]

        acceptable_values = {'', 'true', 'false', 'True', 'False', 'TRUE', 'FALSE'}  # Acceptable value for 'minincluded' and 'maxincluded'

        for i in range(self.table_widget.rowCount()):
            type_value = self.table_widget.cellWidget(i, type_column_index).currentText()
            v_values = [self.table_widget.item(i, v_index).text().strip() for v_index in v_columns]
            continuous_values = [self.table_widget.item(i, cont_index).text().strip() for cont_index in continuous_indices]

            if type_value == "nominal":
                valid_v_count = sum(bool(self.table_widget.item(i, v_index).text().strip()) for v_index in v_columns)
                if valid_v_count < 2:
                    QMessageBox.warning(self, "Validation Error", f"Row {i+1}: 'Nominal' type requires at least 2 'V' columns with values.")
                    return False

            elif type_value == "continuous":
                if not all(continuous_values) or any(v_values):
                    QMessageBox.warning(self, "Validation Error", f"Row {i+1}: Variables with type 'Continuous' requires values in all fields except the 'V' columns.")
                    return False
                minincluded_index = column_names.index("minincluded")
                maxincluded_index = column_names.index("maxincluded")
                minincluded_value = self.table_widget.item(i, minincluded_index).text().strip()
                maxincluded_value = self.table_widget.item(i, maxincluded_index).text().strip()
                if minincluded_value not in acceptable_values or maxincluded_value not in acceptable_values:
                    QMessageBox.warning(self, "Validation Error", f"Row {i+1}: 'minincluded' and 'maxincluded' must be empty, 'False' or 'TRUE'.")
                    return False

            elif type_value == "ordinal":
                has_v_values = any(v_values)
                has_continuous_values = any(continuous_values)

                if has_v_values == has_continuous_values:  # Both True or both False
                    QMessageBox.warning(self, "Validation Error", f"Row {i+1}: Variables with type 'Ordinal' requires values in either the 'V' columns or the other fields, but not both.")
                    return False

        return True

    def save_metadata_file(self):
        """Save the modified metadata file."""
        if self.selected_metadata_path:
            metadata_file_path = self.selected_metadata_path
        elif self.selected_file_path:
            metadata_file_path = os.path.join(METADATA_FOLDER, f"metadata_{os.path.basename(self.selected_file_path)}")
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
        self.stacked_widget.setCurrentWidget(self.file_management_panel)

    def discard_changes(self):
        """Return to the file management panel."""
        reply = QMessageBox.question(self, "Discard Changes", "Are you sure you want to discard the changes?")
        if reply == QMessageBox.Yes:
            self.stacked_widget.setCurrentWidget(self.file_management_panel)

    def add_v_column(self):
        """Add a new 'V' column to the metadata table."""
        current_v_columns = [col for col in [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())] if col.startswith('V')]
        new_v_column_name = f"V{len(current_v_columns) + 1}"
        self.table_widget.insertColumn(self.table_widget.columnCount())
        column_index = self.table_widget.columnCount() - 1
        self.table_widget.setHorizontalHeaderItem(column_index, QTableWidgetItem(new_v_column_name))

        type_column_index = 1 # 'type' column index

        for row_index in range(self.table_widget.rowCount()):
            selected_type = self.table_widget.cellWidget(row_index, type_column_index).currentText()

            new_item = QTableWidgetItem('')
            self.table_widget.setItem(row_index, column_index, new_item)

            if selected_type == "nominal" or selected_type == "ordinal":
                new_item.setFlags(new_item.flags() | Qt.ItemIsEditable)
            else:
                new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
  
    def remove_v_column(self):
        """Remove the last 'V' column from the metadata table."""
        current_v_columns = [i for i, col in enumerate([self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]) if col.startswith('V')]
        if len(current_v_columns) > 2:
            self.table_widget.removeColumn(current_v_columns[-1])
     