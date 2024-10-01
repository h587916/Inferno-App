import os
import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, 
                               QComboBox, QListWidget, QTextEdit, QAbstractItemView)
from r_integration.inferno_functions import run_mutualinfo

LEARNT_FOLDER = 'files/learnt/'
UPLOAD_FOLDER = 'files/uploads/'

class PlottingPage(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout for the Plotting page
        layout = QVBoxLayout()

        # Dataset selection
        self.dataset_label = QLabel("Select a Dataset:")
        layout.addWidget(self.dataset_label)

        self.dataset_combobox = QComboBox()
        layout.addWidget(self.dataset_combobox)
        self.load_datasets()

        # Learnt folder selection
        self.learnt_label = QLabel("Select a Learnt Folder:")
        layout.addWidget(self.learnt_label)

        self.learnt_combobox = QComboBox()
        layout.addWidget(self.learnt_combobox)
        self.load_learnt_folders()

        # Variable selection for Y1 (dependent variable)
        self.Y1_label = QLabel("Select Y1 (Target Variable):")
        layout.addWidget(self.Y1_label)

        self.Y1_combobox = QComboBox()
        layout.addWidget(self.Y1_combobox)

        # Variable selection for Y2 (independent variables) with multi-selection
        self.Y2_label = QLabel("Select Y2 (Conditioning Variables):")
        layout.addWidget(self.Y2_label)

        self.Y2_listwidget = QListWidget()
        self.Y2_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.Y2_listwidget)

        # Button to load variables from the dataset
        self.load_variables_button = QPushButton("Load Variables")
        layout.addWidget(self.load_variables_button)
        self.load_variables_button.clicked.connect(self.load_data_variables)

        # Button to run mutual information
        self.run_button = QPushButton("Run Mutual Information")
        layout.addWidget(self.run_button)
        self.run_button.clicked.connect(self.run_mutual_information)

        # Area to display results
        self.results_label = QLabel("Results:")
        layout.addWidget(self.results_label)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)

        # Set the layout for the page
        self.setLayout(layout)

    def load_datasets(self):
        """Load available datasets from the uploads directory into the ComboBox."""
        datasets = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]
        if datasets:
            self.dataset_combobox.addItems(datasets)
        else:
            self.dataset_combobox.addItem("No datasets available")

    def load_learnt_folders(self):
        """Load available learnt folders from the learnt directory into the ComboBox."""
        learnt_folders = [f for f in os.listdir(LEARNT_FOLDER) if os.path.isdir(os.path.join(LEARNT_FOLDER, f))]
        if learnt_folders:
            self.learnt_combobox.addItems(learnt_folders)
        else:
            self.learnt_combobox.addItem("No learnt folders available")

    def load_data_variables(self):
        """Load available variates from the selected dataset for Y1 and Y2 selection."""
        selected_dataset = self.dataset_combobox.currentText()
        if selected_dataset == "No datasets available":
            QMessageBox.warning(self, "Error", "Please select a valid dataset.")
            return

        try:
            dataset_path = os.path.join(UPLOAD_FOLDER, selected_dataset)
            data = pd.read_csv(dataset_path)

            # Clear previous items in combobox and list widget
            self.Y1_combobox.clear()
            self.Y2_listwidget.clear()

            # Populate the combo box and list widget with column names
            self.Y1_combobox.addItems(data.columns)
            self.Y2_listwidget.addItems(data.columns)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dataset variables: {str(e)}")

    def run_mutual_information(self):
        print("hei")
        """Run mutual information calculation between selected Y1 and Y2."""
        Y1_variate = self.Y1_combobox.currentText()
        Y2_variates = [item.text() for item in self.Y2_listwidget.selectedItems()]
        learnt_folder = self.learnt_combobox.currentText()

        if Y1_variate and Y2_variates and learnt_folder != "No learnt folders available":
            try:
                # Call the run_mutualinfo function
                Y1names = [Y1_variate]
                Y2names = Y2_variates
                learnt_dir = os.path.join(LEARNT_FOLDER, learnt_folder)

                # Run mutual information function
                result = run_mutualinfo(Y1names=Y1names, learnt_dir=learnt_dir, Y2names=Y2names)
                print(result)

                # Check if result is valid
                if result is not None:
                    # Display result in the text area (assuming it's a DataFrame)
                    result_text = result.to_string()  # Convert DataFrame to string for display
                    self.results_display.setText(result_text)
                    QMessageBox.information(self, "Success", "Mutual information calculated successfully.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to calculate mutual information. Please check the logs.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to calculate mutual information: {str(e)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please select Y1, at least one Y2 variable, and a learnt folder.")
