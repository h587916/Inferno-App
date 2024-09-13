import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from r_integration.learn import run_learn

class LearnPage(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout for the Learn page
        layout = QVBoxLayout()

        # Add a label to provide feedback to the user
        self.feedback_label = QLabel("Click the button below to run the learn() function.")
        layout.addWidget(self.feedback_label)

        # Add a button to run the learn function
        run_button = QPushButton("Run learn() function")
        run_button.clicked.connect(self.run_learn_function)  # Connect the button to the run_learn_function method
        layout.addWidget(run_button)

        # Set the layout for the page
        self.setLayout(layout)

    def run_learn_function(self):
        metadatafile, _ = QFileDialog.getOpenFileName(self, "Select Metadata File", "", "CSV Files (*.csv)")
        if not metadatafile:
            self.feedback_label.setText("No metadata file selected.")
            return

        # Prompt the user to select the data file
        datafile, _ = QFileDialog.getOpenFileName(self, "Select Data File", "", "CSV Files (*.csv)")
        if not datafile:
            self.feedback_label.setText("No data file selected.")
            return

        # Show a message box to confirm the files before running
        confirmation = QMessageBox.question(self, "Confirm", f"Run learn() with:\nMetadata: {metadatafile}\nData: {datafile}",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.No:
            return

        # Extract the base name of the data file (without extension)
        datafile_name = os.path.splitext(os.path.basename(datafile))[0]

        # Generate the output directory under 'files/learnt/'
        outputdir = f"files/learnt/{datafile_name}"

        # Update feedback label before running
        self.feedback_label.setText("Running the learn() function...")

        # Run the learn() function with the selected files
        result = run_learn(metadatafile=metadatafile, datafile=datafile, outputdir=outputdir, seed=16, parallel=12)

        # Provide feedback to the user based on the result
        if result:
            self.feedback_label.setText("Learn function completed successfully.")
        else:
            self.feedback_label.setText("An error occurred while running the learn function.")