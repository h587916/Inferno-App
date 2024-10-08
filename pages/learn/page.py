import os
import shutil
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QComboBox, QListWidget, QInputDialog
from r_integration.inferno_functions import run_learn


UPLOAD_FOLDER = 'files/uploads/'
METADATA_FOLDER = 'files/metadata/'
LEARNT_FOLDER = 'files/learnt/'

class LearnPage(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager

        # Set up the layout for the Learn page
        layout = QVBoxLayout()

        # Add ComboBox for selecting CSV file
        self.csv_label = QLabel("Select a CSV File:")
        layout.addWidget(self.csv_label)
        self.csv_combobox = QComboBox()
        layout.addWidget(self.csv_combobox)

        # Add ComboBox for selecting metadata file
        self.metadata_label = QLabel("Select a Metadata File:")
        layout.addWidget(self.metadata_label)
        self.metadata_combobox = QComboBox()
        layout.addWidget(self.metadata_combobox)

        # Add a button to run the learn function
        self.run_button = QPushButton("Run")
        self.run_button.setEnabled(False)  # Initially disabled
        self.run_button.clicked.connect(self.run_learn_function)  
        layout.addWidget(self.run_button)

        # Add a list for displaying the learn results
        self.results_label = QLabel("Results:")
        layout.addWidget(self.results_label)
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

        # Add a button to rename a result folder
        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.rename_result)
        layout.addWidget(self.rename_button)

        # Add a button to delete a result folder
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_result)
        layout.addWidget(self.delete_button)

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

        self.csv_combobox.currentIndexChanged.connect(self.check_selection)
        self.metadata_combobox.currentIndexChanged.connect(self.check_selection)


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
                    self.file_manager.load_files() 
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
                self.file_manager.load_files()
                QMessageBox.information(self, "Success", f"Folder '{folder_name}' deleted.")
        else:
            QMessageBox.warning(self, "Error", "No folder selected.")


    def check_selection(self):
        """Enable the run button if both CSV and metadata files are selected."""
        csv_selected = self.csv_combobox.currentText() != "No CSV files available"
        metadata_selected = self.metadata_combobox.currentText() != "No metadata files available"
        self.run_button.setEnabled(csv_selected and metadata_selected)


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

        # Generate the output directory under 'files/learnt/'
        outputdir = f"files/learnt/{datafile_name}"

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
            self.file_manager.load_files()
        else:
            QMessageBox.critical(self, "Error", "An error occurred while running the simulation")