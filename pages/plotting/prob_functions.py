import os
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QMessageBox
from pages.plotting.variables import get_input_value
from pages.plotting.config import reset_configuration, update_configuration, write_configuration
from r_integration.inferno_functions import run_Pr, run_tailPr
from pages.plotting.plotting import plot_pr_probabilities, plot_tailpr_probabilities, plot_tailpr_probabilities_multi

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, '.inferno_app')
LEARNT_FOLDER = os.path.join(APP_DIR, 'learnt')


def run_pr_function(self):
    """ Run the Pr function and plot the probabilities."""
    if not all_values_filled(self):
        QMessageBox.warning(self, "Error", "Please fill out all value-fields for the selected variables.")
        return

    y_values = get_input_value(self, self.selected_y_values)
    x_values = get_input_value(self, self.selected_x_values)

    Y_df = parse_and_validate_input_values(y_values)
    X_df = parse_and_validate_input_values(x_values)
    if Y_df is None or X_df is None:
        return

    self.Y = Y_df 
    self.X = X_df
    
    learnt_dir = os.path.join(LEARNT_FOLDER, self.pr_learnt_combobox.currentText())

    try:
        self.probabilities_values, self.probabilities_quantiles = run_Pr(self.Y, learnt_dir, self.X)
        reset_configuration(self)
        update_configuration(self)
        write_configuration(self)
        plot_pr_probabilities(self)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to plot probabilities using Pr function: {str(e)}")

def run_tailpr_function(self):
    """Run the tailPr function and plot the probabilities."""
    if not all_values_filled(self):
        QMessageBox.warning(self, "Error", "Please fill out all value-fields...")
        return

    y_values = get_input_value(self, self.selected_y_values)
    x_values = get_input_value(self, self.selected_x_values)
    Y_df = parse_and_validate_input_values(y_values)
    X_df = parse_and_validate_input_values(x_values)
    if Y_df is None or X_df is None:
        return

    self.Y = Y_df
    self.X = X_df

    y_variable = self.selected_y_values[0] if self.selected_y_values else None
    eq, lower_tail = determine_inequality(self, y_variable)

    categorical_variable = self.categorical_variable_combobox.currentText()
    if categorical_variable == "No":
        categorical_variable = None

    learnt_dir = os.path.join(LEARNT_FOLDER, self.pr_learnt_combobox.currentText())

    try:
        if categorical_variable and categorical_variable in self.variable_values:
            selected_categories = self.variable_values[categorical_variable]
            if len(selected_categories) > 1:
                self.probabilities_values = []
                self.probabilities_quantiles = []
                for cat_val in selected_categories:
                    X_single = build_single_category_X(X_df, cat_val, categorical_variable)

                    single_values, single_quantiles = run_tailPr(self.Y, learnt_dir, eq, lower_tail, X_single)
                    self.probabilities_values.append(single_values)
                    self.probabilities_quantiles.append(single_quantiles)

                reset_configuration(self)
                update_configuration(self)
                write_configuration(self)
                plot_tailpr_probabilities_multi(self, selected_categories)
            else:
                self.probabilities_values, self.probabilities_quantiles = run_tailPr(self.Y, learnt_dir, eq, lower_tail, self.X)
                reset_configuration(self)
                update_configuration(self)
                write_configuration(self)
                plot_tailpr_probabilities(self)
        else:
            self.probabilities_values, self.probabilities_quantiles = run_tailPr(self.Y, learnt_dir, eq, lower_tail, self.X)
            reset_configuration(self)
            update_configuration(self)
            write_configuration(self)
            plot_tailpr_probabilities(self)

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to plot probabilities using tailPr function: {str(e)}")
        return

def build_single_category_X(X_df, cat_val, cat_var):
    X_single = X_df.copy()
    X_single[cat_var] = cat_val
    return X_single

def determine_inequality(self, y_variable):
    """Determine the inequality logic for the tailPr function."""
    eq = True
    lower_tail = True

    if not y_variable:
        return eq, lower_tail 

    y_value_dict = self.variable_values.get(y_variable, {})
    inequality = y_value_dict.get('inequality', '<=')

    if inequality == '<':
        eq = False
        lower_tail = True
    elif inequality == '>':
        eq = False
        lower_tail = False
    elif inequality == '<=':
        eq = True
        lower_tail = True
    elif inequality == '>=':
        eq = True
        lower_tail = False

    return eq, lower_tail

def all_values_filled(self):
    """Check if all selected Y and X variables have been assigned values."""
    y_values = get_input_value(self, self.selected_y_values)
    x_values = get_input_value(self, self.selected_x_values)
    plot_variable = self.plot_variable_combobox.currentText()
    categorical_variable = self.categorical_variable_combobox.currentText()
    if categorical_variable == "No":
        categorical_variable = None

    for variable in self.selected_y_values + self.selected_x_values:
        value = y_values.get(variable) or x_values.get(variable)
        if value is None:
            return False

        if self.selected_func == "tailPr":
            if variable in self.selected_y_values:
                if not isinstance(value, dict):
                    return False
                inequality = value.get('inequality', '').strip()
                numeric_val = value.get('value', '').strip()
                if not inequality or not numeric_val:
                    return False
            else:
                if variable == plot_variable:
                    if not isinstance(value, dict):
                        return False
                    start = value.get('start', '').strip()
                    end = value.get('end', '').strip()
                    if not start or not end: 
                        return False
                else:
                    if isinstance(value, dict) and 'start' in value:
                        start = value.get('start', '').strip()
                        if not start:
                            return False
                    elif isinstance(value, list):
                        if not value:
                            return False
                    else:
                        if not value:
                            return False

        else:
            if isinstance(value, dict) and 'start' in value and 'end' in value:
                start = value.get('start', '').strip()
                end = value.get('end', '').strip()
                if not start:
                    return False
                if variable == plot_variable and not end:
                    return False
            elif isinstance(value, list):
                if not value and variable == categorical_variable:
                    return False
            else:
                if not value:
                    return False
    return True

def parse_and_validate_input_values(values):
    """Parse and validate input values and expand shorter arrays."""
    parsed_values = {}
    max_length = 0

    for var_name, value in values.items():
        if isinstance(value, dict) and 'start' in value:
            start_str = value['start']
            end_str = value['end']
            try:
                start_val = float(start_str)
            except ValueError:
                QMessageBox.warning(None, "Error", f"Invalid numeric input for start value in {var_name}: {start_str}")
                return None

            if not end_str:
                variable_value = [start_val]
            else:
                try:
                    end_val = float(end_str)
                except ValueError:
                    QMessageBox.warning(None, "Error", f"Invalid numeric input for end value in {var_name}: {end_str}")
                    return None

                if end_val < start_val:
                    QMessageBox.warning(None, "Error", f"End value must be greater than start value for {var_name}")
                    return None

                num_points = int(abs(end_val - start_val)) + 1
                if start_val.is_integer() and end_val.is_integer():
                    variable_value = list(range(int(start_val), int(end_val) + 1))
                else:
                    variable_value = np.linspace(start_val, end_val, num=num_points).tolist()

        elif isinstance(value, dict) and 'inequality' in value and 'value' in value:
            numeric_value = value['value']
            try:
                numeric_val = float(numeric_value)
            except ValueError:
                QMessageBox.warning(None, "Error", f"Invalid numeric input for {var_name}: {numeric_value}")
                return None
            variable_value = [numeric_val]

        elif isinstance(value, list):
            if not value:
                QMessageBox.warning(None, "Error", f"No values selected for {var_name}")
                return None
            variable_value = value

        else:
            str_val = str(value).strip()
            try:
                float_val = float(str_val)
                variable_value = [float_val]
            except ValueError:
                variable_value = [str_val]

        parsed_values[var_name] = variable_value
        max_length = max(max_length, len(variable_value))

    for var_name, variable_value in parsed_values.items():
        if len(variable_value) < max_length:
            repeats = max_length // len(variable_value) + (max_length % len(variable_value) > 0)
            parsed_values[var_name] = (variable_value * repeats)[:max_length]

    df = pd.DataFrame(parsed_values)
    return df