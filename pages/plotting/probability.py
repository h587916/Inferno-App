import os
import pandas as pd
from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QAbstractItemView, QFormLayout, QTextEdit, QPushButton, QStackedWidget, QHBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import logging
from r_integration.inferno_functions import run_Pr

UPLOAD_FOLDER = 'files/uploads/'
LEARNT_FOLDER = 'files/learnt/'

# Define combinations for plotting output
plotting_combinations = [
    {
        'id': 1,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': list(range(-10, 11))}),  # Y range from -30 to 30
        'X': pd.DataFrame({'Sex': ['Female'], 'TreatmentGroup': ['NR']})
    },
    {
        'id': 2,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': list(range(-10, 11))}),  # Y range from -30 to 30
        'X': pd.DataFrame({'Sex': ['Male', 'Male'], 'TreatmentGroup': ['NR', 'Placebo']})  # Multiple categories
    },
    {
        'id': 3,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': list(range(-10, 11))}),  # Y range from -30 to 30
        'X': pd.DataFrame({'Sex': ['Female'] * len(list(range(25, 31))), 'Age': list(range(25, 31)), 'TreatmentGroup': ['NR'] * len(list(range(25, 31)))})  # Age range
    },
    {
        'id': 4,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': [0]}),  # Single value
        'X': pd.DataFrame({'Sex': ['Female'] * len(list(range(25, 31))), 'Age': list(range(25, 31)), 'TreatmentGroup': ['NR'] * len(list(range(25, 31)))})  # Age range
    },
]

# Define combinations for text output
value_combinations = [
    {
        'id': 5,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': [0]}),  # Single value
        'X': pd.DataFrame({'Sex': ['Female'], 'TreatmentGroup': ['NR']})
    },
    {
        'id': 6,
        'Y': pd.DataFrame({'diff.MDS.UPRS.III': [0]}),  # Single value
        'X': pd.DataFrame({'Sex': ['Male', 'Male'], 'TreatmentGroup': ['NR', 'Placebo']})  # Multiple categories
    }
]

def load_pr_variables(pr_dataset_combobox, Y_listwidget, X_listwidget):
    """Load available variables for the Pr function."""
    selected_dataset = pr_dataset_combobox.currentText()

    if selected_dataset == "No datasets available":
        QMessageBox.warning(None, "Error", "Please select a valid dataset.")
        return
    
    dataset_path = os.path.join(UPLOAD_FOLDER, selected_dataset)

    try:
        # Open and close the file safely to avoid permission errors
        with open(dataset_path, 'r') as f:
            data = pd.read_csv(f)

        # Clear previous items in list widgets
        Y_listwidget.clear()
        X_listwidget.clear()

        # Populate the list widgets with column names
        Y_listwidget.addItems(data.columns)
        X_listwidget.addItems(data.columns)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load dataset variables: {str(e)}")

def run_pr_function(results_display):
    print("### RUNNING ###")

    #all_combinations = plotting_combinations + value_combinations
    #combination = random.choice(all_combinations)
    
    #Y = combination['Y']
    #X = combination['X']

    Y = pd.DataFrame({'diff.MDS.UPRS.III': list(range(-30, 31))})
    X = pd.DataFrame({'Sex': ['Female'], 'TreatmentGroup': ['NR']})
    learnt_dir = 'files/learnt/toydata'

    try:
        probabilities_values, probabilities_quantiles = run_Pr(Y, learnt_dir, X)

        if should_plot(Y, X):
            # Plotting case
            results_display.setText(f"Plotting results...")
            plot_probabilities(Y, probabilities_values, probabilities_quantiles)
        else:
            # Text value case
            results_display.setText(f"Displaying numerical results: \nProbabilities: {probabilities_values}\nQuantiles: {probabilities_quantiles}")
    
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to run the Pr function: {str(e)}")

def should_plot(Y, X):
    # Check if any column in Y has multiple values and is numeric
    for column in Y.columns:
        if len(Y[column].unique()) > 1 and pd.api.types.is_numeric_dtype(Y[column]):
            return True
    
    # Check if any column in X has multiple values and is numeric
    for column in X.columns:
        if len(X[column].unique()) > 1 and pd.api.types.is_numeric_dtype(X[column]):
            return True
    
    # Do not plot
    return False

def plot_probabilities(Y_values, probabilities_values, probabilities_quantiles):
    # Extract the column name dynamically from Y_values
    y_column = Y_values.columns[0]

    # Convert R objects back to numpy arrays for plotting
    probabilities_values = np.array(probabilities_values).flatten()
    probabilities_quantiles = np.array(probabilities_quantiles)

    # Ensure quantiles array is correctly shaped for plotting
    if probabilities_quantiles.ndim == 3:
        lower_quantiles = probabilities_quantiles[:, 0, 0]
        upper_quantiles = probabilities_quantiles[:, 0, -1]
    elif probabilities_quantiles.ndim == 2 and probabilities_quantiles.shape[1] >= 2:
        lower_quantiles = probabilities_quantiles[:, 0]
        upper_quantiles = probabilities_quantiles[:, -1]
    else:
        logging.error("Unexpected shape of quantiles array.")
        lower_quantiles = np.zeros(Y_values.shape[0])
        upper_quantiles = np.zeros(Y_values.shape[0])

    # Personalized plot
    # Plot the quantiles with a customized appearance
    plt.fill_between(
        Y_values[y_column], 
        lower_quantiles, 
        upper_quantiles,
        color='skyblue', 
        alpha=0.5, 
        edgecolor='darkblue', 
        linewidth=2,
        label='Uncertainty (Quantiles)'
    )

    plt.ylim(0, None)
    plt.xlabel('MDS-UPDRS-III difference')
    plt.ylabel('Probability')

    # Overlay the probability distribution curve
    # Interpolate to make the plot look smoother
    spl = make_interp_spline(Y_values['diff.MDS.UPRS.III'], probabilities_values, k=3)
    Y_smooth = np.linspace(Y_values['diff.MDS.UPRS.III'].min(), Y_values['diff.MDS.UPRS.III'].max(), 500)
    prob_smooth = spl(Y_smooth)

    plt.plot(Y_smooth, prob_smooth, color='red', linewidth=2, linestyle='-', label='Probability')

    # Add the 0-change line
    plt.axvline(x=0, color='blue', linestyle='--', linewidth=2, label='0-change Line')

    # Add legend to explain the components of the plot
    plt.legend()

    plt.show()