import os
import json
import shutil
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QMessageBox, QComboBox, QListWidget, QInputDialog, QSizePolicy, QDialog, QFormLayout, QLineEdit
from r_integration.inferno_functions import run_learn


UPLOAD_FOLDER = 'files/uploads/'
METADATA_FOLDER = 'files/metadata/'
LEARNT_FOLDER = 'files/learnt/'

class LearnPage(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Monte Carlo Simulation")
        font = title_label.font()
        font.setPointSize(20)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignHCenter)
        title_label.setContentsMargins(0, 10, 0, 20)  # left, top, right, bottom
        layout.addWidget(title_label)

        # --- Group box for left side ---
        self.left_group = QGroupBox()
        self.left_group.setAlignment(Qt.AlignHCenter)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(40, 20, 40, 400)  # left, top, right, bottom
        self.left_group.setLayout(left_layout)
        fixed_label_width = 120

        file_layout = QHBoxLayout()
        csv_label = QLabel("Select a CSV File:")
        self.csv_combobox = QComboBox()
        self.csv_combobox.currentIndexChanged.connect(self.check_selection)
        csv_label.setFixedWidth(fixed_label_width)
        file_layout.addWidget(csv_label)
        file_layout.addWidget(self.csv_combobox)
        left_layout.addLayout(file_layout)

        meta_layout = QHBoxLayout()
        metadata_label = QLabel("Select a Metadata File:")
        self.metadata_combobox = QComboBox()
        self.metadata_combobox.currentIndexChanged.connect(self.check_selection)
        metadata_label.setFixedWidth(fixed_label_width)
        meta_layout.addWidget(metadata_label)
        meta_layout.addWidget(self.metadata_combobox)
        left_layout.addLayout(meta_layout)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(40, 0, 40, 0)  # left, top, right, bottom

        self.run_button = QPushButton("Run Simulation")
        self.run_button.clicked.connect(self.run_learn_function)
        self.run_button.setFixedWidth(150)
        button_layout.addWidget(self.run_button)

        self.configure_button = QPushButton("Configure")
        self.configure_button.setFixedWidth(150)
        self.configure_button.clicked.connect(self.configure_run_learn)
        button_layout.addWidget(self.configure_button)

        left_layout.addLayout(button_layout)

        # --- Group box for right side ---
        self.right_group = QGroupBox("Results Folders")
        self.right_group.setAlignment(Qt.AlignHCenter)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 20, 0, 180)  # left, top, right, bottom
        self.right_group.setLayout(right_layout)

        list_layout = QHBoxLayout()
        self.results_list = QListWidget()
        self.results_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.results_list.setMaximumWidth(400)
        self.results_list.setMaximumHeight(300)
        list_layout.addWidget(self.results_list)
        right_layout.addLayout(list_layout)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(70, 0, 70, 0)  # left, top, right, bottom

        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.rename_result)
        self.rename_button.setFixedWidth(150)
        button_layout.addWidget(self.rename_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_result)
        self.delete_button.setFixedWidth(150)
        button_layout.addWidget(self.delete_button)

        right_layout.addLayout(button_layout)

        # Add group boxes to the main layout
        group_layout = QHBoxLayout()
        group_layout.addWidget(self.left_group)
        group_layout.addWidget(self.right_group)
        layout.addLayout(group_layout)

        # Set the layout for the page
        self.setLayout(layout)

        # Load and apply styles from the QSS file
        with open('pages/learn/styles.qss', 'r') as f:
            style = f.read()
            self.setStyleSheet(style)

        # Connect to file manager signals
        self.file_manager.files_updated.connect(self.load_files)
        self.file_manager.learnt_folders_updated.connect(self.load_result_folders)

        # Load files
        self.file_manager.refresh()


    ### HELPER FUNCTIONS ###

    def load_files(self):
        """Load CSV and metadata files from FileManager."""
        self.csv_combobox.clear()
        self.metadata_combobox.clear()

        # Populate CSV combobox
        if self.file_manager.uploaded_files:
            self.csv_combobox.addItems(self.file_manager.uploaded_files)
        else:
            self.csv_combobox.addItem("No CSV files available")
            self.csv_combobox.setItemData(1, Qt.NoItemFlags)
        self.csv_combobox.setCurrentIndex(-1)

        # Populate Metadata combobox
        if self.file_manager.metadata_files:
            self.metadata_combobox.addItems(self.file_manager.metadata_files)
        else:
            self.metadata_combobox.addItem("No metadata files available")
            self.metadata_combobox.setItemData(1, Qt.NoItemFlags)
        self.metadata_combobox.setCurrentIndex(-1)

    def load_result_folders(self):
        """Load the result folders from the learnt folder using FileManager."""
        self.results_list.clear()

        if self.file_manager.learnt_folders:
            self.results_list.addItems(self.file_manager.learnt_folders)
        else:
            self.results_list.addItem("No result folders available")
    
    def rename_result(self):
        """Rename the selected result folder."""
        selected_item = self.results_list.currentItem()
        if selected_item:
            old_name = selected_item.text()
            new_name, ok = QInputDialog.getText(self, "Rename Folder", "Enter new name:", text=old_name)
            if ok and new_name:
                old_path = os.path.join(LEARNT_FOLDER, old_name)
                new_path = os.path.join(LEARNT_FOLDER, new_name)
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)
                    self.file_manager.refresh()
                    QMessageBox.information(self, "Success", f"Folder renamed to {new_name}.")
                else:
                    QMessageBox.warning(self, "Error", "A folder with that name already exists.")
        else:
            QMessageBox.warning(self, "Error", "No folder selected.")

    def delete_result(self):
        """Delete the selected result folder."""
        selected_item = self.results_list.currentItem()
        if selected_item:
            folder_name = selected_item.text()
            confirm = QMessageBox.question(self, "Delete Folder", f"Are you sure you want to delete the folder '{folder_name}'?", 
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                folder_path = os.path.join(LEARNT_FOLDER, folder_name)
                shutil.rmtree(folder_path)
                self.file_manager.refresh()
                QMessageBox.information(self, "Success", f"Folder '{folder_name}' deleted.")
        else:
            QMessageBox.warning(self, "Error", "No folder selected.")

    def check_selection(self):
        """Enable the run button if both CSV and metadata files are selected."""
        csv_selected = self.csv_combobox.currentText() != "No CSV files available"
        metadata_selected = self.metadata_combobox.currentText() != "No metadata files available"
        self.run_button.setEnabled(csv_selected and metadata_selected)

    def load_configuration(self):
        """Load configuration from config.json or create it with default values."""
        with open('pages/learn/config.json', 'r') as f:
            config = json.load(f)
            self.nsamples = config.get('nsamples', 3600)
            self.nchains = config.get('nchains', 60)
            maxhours = config.get('maxhours', 'inf')
            if maxhours == 'inf':
                self.maxhours = float('inf')
            else:
                self.maxhours = float(maxhours)
            self.parallel = config.get('parallel', 4)

    def configure_run_learn(self):
        """Open a dialog to configure run_learn parameters."""
        self.load_configuration()

        dialog = QDialog(self)
        dialog.setMinimumWidth(300)
        dialog.setWindowTitle("Configure Learn Function Parameters")

        layout = QFormLayout()

        self.nsamples_input = QLineEdit(str(self.nsamples))
        self.nchains_input = QLineEdit(str(self.nchains))
        if self.maxhours == float('inf'):
            maxhours_str = 'inf'
        else:
            maxhours_str = str(self.maxhours)
        self.maxhours_input = QLineEdit(maxhours_str)
        self.parallel_input = QLineEdit(str(self.parallel))

        layout.addRow("nsamples:", self.nsamples_input)
        layout.addRow("nchains:", self.nchains_input)
        layout.addRow("maxhours:", self.maxhours_input)
        layout.addRow("parallel:", self.parallel_input)

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_configuration(dialog))

        layout.addWidget(save_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def save_configuration(self, dialog):
        """Save the configured values."""
        self.nsamples = int(self.nsamples_input.text())
        self.nchains = int(self.nchains_input.text())
        maxhours_text = self.maxhours_input.text()
        if maxhours_text == 'inf':
            self.maxhours = float('inf')
        else:
            self.maxhours = float(maxhours_text)
        self.parallel = int(self.parallel_input.text())
        # Save the new configuration to config.json
        config = {
            'nsamples': self.nsamples,
            'nchains': self.nchains,
            'maxhours': 'inf' if self.maxhours == float('inf') else self.maxhours,
            'parallel': self.parallel
        }
        with open('pages/learn/config.json', 'w') as f:
            json.dump(config, f)
        dialog.accept()

    def run_learn_function(self):
        """Run the learn function with the selected CSV and Metadata files."""
        csv_file = self.csv_combobox.currentText()
        metadata_file = self.metadata_combobox.currentText()

        if not csv_file or not metadata_file or csv_file == "No CSV files available" or metadata_file == "No metadata files available":
            QMessageBox.warning(self, "Error", "Please select both a CSV file and a Metadata file.")
            return

        # Confirmation message box before running
        confirmation = QMessageBox.question(self, "Confirm", f"Run Monte Carlo simulation with:\nMetadata: {metadata_file}\nData: {csv_file}", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.No:
            return

        # Extract the base name of the CSV file (without extension)
        datafile_name = os.path.splitext(csv_file)[0]

        # Generate the output directory under LEARNT_FOLDER
        outputdir = os.path.join(LEARNT_FOLDER, datafile_name)

        # Show a message box to indicate the learn function is running
        running_message = QMessageBox(self)
        running_message.setWindowTitle("Running")
        running_message.setText("Running the Monte Carlo simulation... \nThis will take a few minutes, so you might want\n to go grab a cup of coffee while waiting.")
        running_message.setStandardButtons(QMessageBox.NoButton)
        running_message.show()

        # Full paths for the selected files
        csv_file_path = os.path.join(UPLOAD_FOLDER, csv_file)
        metadata_file_path = os.path.join(METADATA_FOLDER, metadata_file)

        # Run the learn() function with the selected files
        result = run_learn(metadatafile=metadata_file_path, datafile=csv_file_path, outputdir=outputdir, parallel=12)

        # Close the running message box after completion
        running_message.done(0)

        # Provide feedback with a message box based on the result
        if result:
            QMessageBox.information(self, "Success", f"Monte Carlo simulation runned successfully!\nThe results are saved in the '{datafile_name}' folder.")
            self.file_manager.refresh()
        else:
            QMessageBox.critical(self, "Error", "An error occurred while running the simulation")