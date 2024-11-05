import os
import json
import shutil
import importlib.resources
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QMessageBox, QComboBox, QListWidget, 
                                QInputDialog, QSizePolicy, QDialog, QFormLayout, QLineEdit, QSpacerItem, QFileDialog, QHBoxLayout, QLabel, QGridLayout)
from r_integration.inferno_functions import run_learn


# Define the base directory paths (consistent with file_manager.py)
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, '.inferno_app')

UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
METADATA_FOLDER = os.path.join(APP_DIR, 'metadata')
LEARNT_FOLDER = os.path.join(APP_DIR, 'learnt')
USER_CONFIG_PATH = os.path.join(APP_DIR, 'config/learn_config.json')

class LearnPage(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        layout = QGridLayout()
        button_width = 100

        # Title label
        title_label = QLabel("Monte Carlo Simulation")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignHCenter)
        title_label.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        layout.addWidget(title_label, 0, 0, 1, 2)

        vertical_spacer = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(vertical_spacer, 1, 0, 1, 2)

        # --- Group box for left side (run simulation) ---
        self.simulation_group = QGroupBox("Simulation")
        self.simulation_group.setAlignment(Qt.AlignHCenter)

        simulation_layout = QVBoxLayout()
        simulation_layout.setContentsMargins(50, 50, 50, 0)  # left, top, right, bottom
        simulation_layout.setAlignment(Qt.AlignHCenter)
        self.simulation_group.setLayout(simulation_layout)
        
        fixed_label_width = 120
        file_layout = QHBoxLayout()
        csv_label = QLabel("Select a CSV File:")
        csv_label.setFixedWidth(fixed_label_width)
        self.csv_combobox = QComboBox()
        self.csv_combobox.currentIndexChanged.connect(self.check_selection)
        file_layout.addWidget(csv_label)
        file_layout.addWidget(self.csv_combobox)
        simulation_layout.addLayout(file_layout)

        meta_layout = QHBoxLayout()
        metadata_label = QLabel("Select a Metadata File:")
        metadata_label.setFixedWidth(fixed_label_width)
        self.metadata_combobox = QComboBox()
        self.metadata_combobox.currentIndexChanged.connect(self.check_selection)
        meta_layout.addWidget(metadata_label)
        meta_layout.addWidget(self.metadata_combobox)
        simulation_layout.addLayout(meta_layout)

        vertical_spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        simulation_layout.addItem(vertical_spacer)

        self.run_button = QPushButton("Simulate")
        self.run_button.clicked.connect(self.run_learn_function)
        self.run_button.setFixedWidth(button_width)

        self.configure_button = QPushButton("Configure")
        self.configure_button.setFixedWidth(button_width)
        self.configure_button.clicked.connect(self.configure_run_learn)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignHCenter)
        button_layout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom

        horizontal_spacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        button_layout.addWidget(self.run_button)
        button_layout.addItem(horizontal_spacer)
        button_layout.addWidget(self.configure_button)

        simulation_layout.addLayout(button_layout)
        simulation_layout.addStretch()

        # --- Group box for right side (results folder list) ---
        self.results_list_group = QGroupBox("Results Folders")
        self.results_list_group.setAlignment(Qt.AlignHCenter)

        results_list_layout = QVBoxLayout()
        results_list_layout.setContentsMargins(50, 50, 50, 50)  # left, top, right, bottom
        results_list_layout.setAlignment(Qt.AlignHCenter)
        self.results_list_group.setLayout(results_list_layout)

        list_layout = QVBoxLayout()
        self.results_list = QListWidget()
        self.results_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        list_layout.addWidget(self.results_list)

        results_list_layout.addLayout(list_layout)
        results_list_layout.addItem(vertical_spacer)


        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.rename_result)
        self.rename_button.setFixedWidth(button_width)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_result)
        self.delete_button.setFixedWidth(button_width)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_result)
        self.upload_button.setFixedWidth(button_width)

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_result)
        self.download_button.setFixedWidth(button_width)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 10)  # left, top, right, bottom
        button_layout.setAlignment(Qt.AlignHCenter)

        button_layout.addWidget(self.rename_button)
        button_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        button_layout.addWidget(self.delete_button)
        button_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        button_layout.addWidget(self.upload_button)
        button_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        button_layout.addWidget(self.download_button)

        results_list_layout.addLayout(button_layout)

        # General Setup
        layout.addWidget(self.simulation_group, 2, 0)
        layout.addWidget(self.results_list_group, 2, 1)

        self.setLayout(layout)

        # Apply the stylesheet
        with importlib.resources.open_text('pages.learn', 'styles.qss') as f:
            style = f.read()
            self.setStyleSheet(style)

        self.file_manager.files_updated.connect(self.load_files)
        self.file_manager.learnt_folders_updated.connect(self.load_result_folders)
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

    def upload_result(self):
        """Upload a learnt folder."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select a learnt folder to upload")
        if folder_path:
            folder_name = os.path.basename(folder_path)
            new_path = os.path.join(LEARNT_FOLDER, folder_name)
            if not os.path.exists(new_path):
                shutil.copytree(folder_path, new_path)
                self.file_manager.refresh()
                QMessageBox.information(self, "Success", f"Folder '{folder_name}' uploaded.")
            else:
                QMessageBox.warning(self, "Error", "A folder with that name already exists.")

    def download_result(self):
        """Download the selected result folder."""
        selected_item = self.results_list.currentItem()
        if selected_item:
            folder_name = selected_item.text()
            folder_path = os.path.join(LEARNT_FOLDER, folder_name)
            download_path = QFileDialog.getExistingDirectory(self, "Select the downloaded destination")
            if download_path:
                new_path = os.path.join(download_path, folder_name)
                if not os.path.exists(new_path):
                    shutil.copytree(folder_path, new_path)
                    QMessageBox.information(self, "Success", f"Folder '{folder_name}' downloaded.")
                else:
                    QMessageBox.warning(self, "Error", "A folder with that name already exists in the download location.")
        else:
            QMessageBox.warning(self, "Error", "No folder selected.")

    def check_selection(self):
        """Enable the run button if both CSV and metadata files are selected."""
        csv_selected = self.csv_combobox.currentText() != "No CSV files available"
        metadata_selected = self.metadata_combobox.currentText() != "No metadata files available"
        self.run_button.setEnabled(csv_selected and metadata_selected)

    def load_configuration(self):
        """Load configuration from JSON"""
        if os.path.exists(USER_CONFIG_PATH):
            # Load user configuration
            with open(USER_CONFIG_PATH, 'r') as f:
                config = json.load(f)
        else:
            # Use default values defined in code
            config = {
                'nsamples': 3600,
                'nchains': 60,
                'maxhours': 'inf',
                'seed': 16,
                'parallel': 12
            }
        self.nsamples = config.get('nsamples', 3600)
        self.nchains = config.get('nchains', 60)
        maxhours = config.get('maxhours', 'inf')
        if maxhours == 'inf':
            self.maxhours = float('inf')
        else:
            self.maxhours = float(maxhours)
        self.seed = config.get('seed', 16)
        self.parallel = config.get('parallel', 12)

    def configure_run_learn(self):
        """Open a dialog to configure run_learn parameters."""
        self.load_configuration()

        dialog = QDialog(self)
        dialog.setFixedWidth(270)
        dialog.setFixedHeight(170)
        dialog.setWindowTitle("Configure Learn Function Parameters")

        layout = QFormLayout()

        self.nsamples_input = QLineEdit(str(self.nsamples))
        self.nchains_input = QLineEdit(str(self.nchains))
        if self.maxhours == float('inf'):
            maxhours_str = 'inf'
        else:
            maxhours_str = str(self.maxhours)
        self.maxhours_input = QLineEdit(maxhours_str)
        self.seed_input = QLineEdit(str(self.seed))
        self.parallel_input = QLineEdit(str(self.parallel))

        layout.addRow("nsamples:", self.nsamples_input)
        layout.addRow("nchains:", self.nchains_input)
        layout.addRow("maxhours:", self.maxhours_input)
        layout.addRow("seed:", self.seed_input)
        layout.addRow("parallel:", self.parallel_input)

        doc_link = QLabel("<a href='https://pglpm.github.io/inferno/reference/learn.html'>Parameter Documentation</a>")
        doc_link.setOpenExternalLinks(True)

        save_button = QPushButton("Save")
        save_button.setFixedWidth(50)
        save_button.setFixedHeight(30)
        save_button.setStyleSheet("font-size: 10px;")
        save_button.clicked.connect(lambda: self.save_configuration(dialog))

        button_layout = QHBoxLayout()
        button_layout.addWidget(doc_link)
        button_layout.addStretch()  # Add a stretchable space before the button
        button_layout.addWidget(save_button)

        layout.addRow(button_layout)
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
        self.seed = int(self.seed_input.text())
        self.parallel = int(self.parallel_input.text())
        # Save the new configuration to config.json
        config = {
            'nsamples': self.nsamples,
            'nchains': self.nchains,
            'maxhours': 'inf' if self.maxhours == float('inf') else self.maxhours,
            'seed': self.seed,
            'parallel': self.parallel
        }
        with open(USER_CONFIG_PATH, 'w') as f:
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
        result = run_learn(metadatafile=metadata_file_path, datafile=csv_file_path, outputdir=outputdir, parallel=self.parallel, nsamples=self.nsamples, nchains=self.nchains, maxhours=self.maxhours, seed=self.seed)

        # Close the running message box after completion
        running_message.done(0)

        # Provide feedback with a message box based on the result
        if result:
            QMessageBox.information(self, "Success", f"Monte Carlo simulation runned successfully!\nThe results are saved in the '{datafile_name}' folder.")
            self.file_manager.refresh()
        else:
            QMessageBox.critical(self, "Error", "An error occurred while running the simulation")