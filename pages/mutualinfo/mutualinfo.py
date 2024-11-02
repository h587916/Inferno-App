import os
import pandas as pd
from r_integration.inferno_functions import run_mutualinfo
from PySide6.QtWidgets import QMessageBox

# Define the base directory paths (consistent with file_manager.py)
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, '.inferno_app')

UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
LEARNT_FOLDER = os.path.join(APP_DIR, 'learnt')


def load_mutual_variables(dataset_combobox, predictand_combobox, predictor_listwidget, additional_predictor_listwidget):
    """Load available variates from the selected dataset for predictand, predictor, and additional predictor selection."""
    selected_dataset = dataset_combobox.currentText()
    
    if selected_dataset == "No datasets available":
        QMessageBox.warning(None, "Error", "Please select a valid dataset.")
        return
    
    dataset_path = os.path.join(UPLOAD_FOLDER, selected_dataset)

    try:
        # Open and close the file safely to avoid permission errors
        with open(dataset_path, 'r') as f:
            data = pd.read_csv(f)

        # Clear previous items in combobox and list widget
        predictand_combobox.clear()
        predictor_listwidget.clear()
        additional_predictor_listwidget.clear()

        # Populate the combobox and list widgets with column names
        predictand_combobox.addItems(data.columns)
        predictor_listwidget.addItems(data.columns)
        additional_predictor_listwidget.addItems(data.columns)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load dataset variables: {str(e)}")


def run_mutual_information(predictand_combobox, predictor_listwidget, additional_predictor_listwidget, learnt_combobox, results_display, dataset_combobox):
    """Run mutual information calculation between predictors and predictand."""
    predictand = predictand_combobox.currentText()
    predictors = [item.text() for item in predictor_listwidget.selectedItems()]
    additional_predictors = [item.text() for item in additional_predictor_listwidget.selectedItems()]
    learnt_folder = learnt_combobox.currentText()
    selected_dataset = dataset_combobox.currentText()

    if predictand and predictors and learnt_folder != "No learnt folders available":
        try:
            # Show a message box to indicate the mutual information function is running
            running_message = QMessageBox(None)
            running_message.setWindowTitle("Running")
            running_message.setText("Calculating mutual information... \nThis will take a few moments.")
            running_message.setStandardButtons(QMessageBox.NoButton)
            running_message.show()

            # Prepare the predictand DataFrame
            learnt_dir = os.path.join(LEARNT_FOLDER, learnt_folder)
            predictand_df = pd.DataFrame() 
            dataset_path = os.path.join(UPLOAD_FOLDER, selected_dataset)
            data = pd.read_csv(dataset_path)
            predictand_df[predictand] = data[predictand]

            # Run mutual information function
            result = run_mutualinfo(predictor=predictors, learnt_dir=learnt_dir, additional_predictor=additional_predictors, predictand=predictand_df)

            # Close the running message box
            running_message.done(0)

            # Check if result is valid
            if result is not None:
                # Display results in the text area
                formatted_result = format_mutualinfo_result(result)
                results_display.setText(formatted_result)
                QMessageBox.information(None, "Success", "Mutual information calculated successfully.")
            else:
                QMessageBox.warning(None, "Error", "Failed to calculate mutual information. Please check the logs.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to calculate mutual information: {str(e)}")
    else:
        QMessageBox.warning(None, "Input Error", "Please select a predictand, at least one predictor, and a learnt folder.")


def format_mutualinfo_result(result):
    """Format the mutualinfo result into a readable string."""
    try:
        # Extract the relevant sections from the result
        mi = result.rx2('MI')  # Mutual Information
        cond_en12 = result.rx2('CondEn12')  # Conditional Entropy H(Y1 | Y2)
        cond_en21 = result.rx2('CondEn21')  # Conditional Entropy H(Y2 | Y1)
        en1 = result.rx2('En1')  # Entropy H(Y1)
        en2 = result.rx2('En2')  # Entropy H(Y2)

        # Prepare the result text
        result_text = "Mutual Information Results:\n"
        result_text += "\nMutual Information (MI):\n"
        result_text += format_floatvector(mi)

        result_text += "\n\nConditional Entropy H(Y1 | Y2):\n"
        result_text += format_floatvector(cond_en12)

        result_text += "\n\nConditional Entropy H(Y2 | Y1):\n"
        result_text += format_floatvector(cond_en21)

        result_text += "\n\nEntropy H(Y1):\n"
        result_text += format_floatvector(en1)

        result_text += "\n\nEntropy H(Y2):\n"
        result_text += format_floatvector(en2)

        return result_text

    except Exception as e:
        return f"Error formatting mutual information result: {str(e)}"


def format_floatvector(vector):
    """Helper function to format FloatVector objects."""
    formatted_str = ""
    try:
        for idx, val in enumerate(vector):
            formatted_str += f"Value: {val:.6f}\n"  # You can change the format based on your preference
        return formatted_str
    except Exception as e:
        return f"Error formatting vector: {str(e)}"

