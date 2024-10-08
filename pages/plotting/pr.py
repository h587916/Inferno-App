import os
import pandas as pd
from PySide6.QtWidgets import QLineEdit
from r_integration.inferno_functions import run_Pr

UPLOAD_FOLDER = 'files/uploads/'
LEARNT_FOLDER = 'files/learnt/'


def load_pr_variables(Y_combobox, X_listwidget, X_value_form, learnt_combobox):
    return


def run_pr_function(Y_combobox, X_listwidget, X_value_form, learnt_combobox, results_display):
    """Run the Pr function with selected Y and X variates."""
    Y_variate = Y_combobox.currentText()
    selected_X_items = X_listwidget.selectedItems()

    if not Y_variate or not selected_X_items:
        results_display.setText("Please select both Y and X variates.")
        return

    try:
        # Prepare Y DataFrame
        Y_df = pd.DataFrame({Y_variate: []})

        # Prepare X DataFrame with user-specified values
        X_df = pd.DataFrame()
        for item in selected_X_items:
            X_variate = item.text()
            X_value = getattr(X_value_form, f"{X_variate}_input").text()  # Retrieve the value inputted by the user
            X_df[X_variate] = [X_value]

        # Run Pr function
        learnt_folder = learnt_combobox.currentText()
        learnt_dir = os.path.join(LEARNT_FOLDER, learnt_folder)
        result = run_Pr(Y=Y_df, learnt_dir=learnt_dir, X=X_df)

        # Display results
        if result is not None:
            results_display.setText(f"Pr function result:\n{result}")
        else:
            results_display.setText("Error running Pr function.")

    except Exception as e:
        results_display.setText(f"An error occurred: {str(e)}")
