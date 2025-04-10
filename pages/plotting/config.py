import os
import json
import importlib.resources
from PySide6.QtWidgets import (QDialog, QFormLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QMessageBox, QScrollArea, QWidget, QVBoxLayout)
from PySide6.QtCore import Qt
from appdirs import user_data_dir
from pages.shared.custom_combobox import CustomComboBox
from pages.plotting.variables import is_numeric


APP_DIR = user_data_dir("Inferno App", "inferno")
USER_CONFIG_PATH = os.path.join(APP_DIR, 'config/plotting_config.json')


def load_configuration(self):
    """Load configuration from JSON file."""
    with open(USER_CONFIG_PATH, 'r') as f:
        self.config = json.load(f)


def write_configuration(self):
    """Write configuration to JSON file."""
    with open(USER_CONFIG_PATH, 'w') as f:
        json.dump(self.config, f)


def reset_configuration(self):
    """Reset the configuration to default values."""
    with importlib.resources.open_text('pages.plotting', 'default_config.json') as f:
        self.config = json.load(f)


def update_configuration(self):
    """Update the configuration dynamically based on current selections and data in PlottingPage."""
    plot_variable = self.plot_variable_combobox.currentText()
    categorical_variable = self.categorical_variable_combobox.currentText()
    if categorical_variable == "No":
        categorical_variable = None

    self.config['shared']['x_label'] = plot_variable

    if self.selected_func == "tailPr":
        other_values = []
        all_selected_vars = self.selected_x_values
        for var in all_selected_vars:
            if var == plot_variable or var == categorical_variable:
                continue
            val = self.variable_values.get(var)
            if isinstance(val, list):
                if len(val) == 1:
                    other_values.append(val[0])
                else:
                    other_values.append(", ".join(val))
            elif isinstance(val, dict):
                start_val = val.get('start', '')
                end_val = val.get('end', '')
                if end_val:
                    other_values.append(f"{start_val}-{end_val}")
                else:
                    other_values.append(str(start_val))
            else:
                other_values.append(str(val))

        if categorical_variable and categorical_variable in self.variable_values:
            categories = self.variable_values[categorical_variable]
            for i, category in enumerate(categories, start=1):
                plot_key = f"plot_{i}"
                self.config[plot_key]['probability_label'] = f"{', '.join(other_values)}, {category}"
                self.config[plot_key]['uncertantity_label'] = ""
        else:
            plot_key = "plot_1"
            self.config[plot_key]['probability_label'] = ", ".join(other_values)
            self.config[plot_key]['uncertantity_label'] = ""

    elif self.selected_func == "Pr":
        num_variables = self.probabilities_values.shape[1] if self.probabilities_values is not None else 1

        other_values = []
        all_selected_vars = self.selected_y_values + self.selected_x_values
        for var in all_selected_vars:
            if var == plot_variable or var == categorical_variable:
                continue
            val = self.variable_values.get(var)
            if isinstance(val, list):
                if len(val) == 1:
                    other_values.append(val[0])
                else:
                    other_values.append(", ".join(val))
            elif isinstance(val, dict):
                start_val = val.get('start', '')
                end_val = val.get('end', '')
                if end_val:
                    other_values.append(f"{start_val}-{end_val}")
                else:
                    other_values.append(str(start_val))
            else:
                other_values.append(str(val))

        line_labels = []
        if is_numeric(self, plot_variable):
            categorical_y_values = []
            categorical_x_values = []

            for y_var in self.selected_y_values:
                if y_var in self.variable_values:
                    selected_y_values = self.variable_values[y_var]
                    if isinstance(selected_y_values, list) and len(selected_y_values) > 1:
                        categorical_y_values.append((y_var, selected_y_values))

            for x_var in self.selected_x_values:
                if x_var in self.variable_values:
                    selected_x_values = self.variable_values[x_var]
                    if isinstance(selected_x_values, list) and len(selected_x_values) > 1:
                        categorical_x_values.append((x_var, selected_x_values))

            line_labels = []

            # Case 1: Categorical Y-values exist
            if categorical_y_values:
                for y_var, y_vals in categorical_y_values:
                    for y_val in y_vals:
                        label_parts = [y_val] 
                        label_parts.extend(other_values)
                        line_labels.append(", ".join(label_parts))

            # Case 2: Categorical X-values exist (and Y-variable is numeric)
            elif categorical_x_values:
                for x_var, x_vals in categorical_x_values:
                    for x_val in x_vals:
                        label_parts = [x_val]
                        label_parts.extend(other_values)
                        line_labels.append(", ".join(label_parts))

            # Case 3: Default fallback if no categorical Y/X-values exist
            else:
                label = ", ".join(other_values) if other_values else "Probability"
                line_labels = [label] * num_variables

        for i, label in enumerate(line_labels, start=1):
            plot_key = f"plot_{i}"
            if plot_key in self.config:
                self.config[plot_key]['probability_label'] = label

def configure_plot(self):
    """Open a dialog to configure plot settings."""
    dialog = QDialog(self)
    dialog.setFixedWidth(350)
    dialog.setMaximumHeight(850)
    dialog.setWindowTitle("Configure Plot Settings")

    # Scroll area setup
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    # Main content widget inside the scroll area
    content_widget = QWidget()
    layout = QFormLayout(content_widget)

    # Shared Fields
    self.width_probability_curve_edit = QLineEdit(str(self.config['shared']['width_probability_curve']))
    self.width_uncertainty_area_edit = QLineEdit(str(self.config['shared']['width_uncertainty_area']))
    self.alpha_uncertainty_area_edit = QLineEdit(str(self.config['shared']['alpha_uncertainty_area']))
    self.xlabel_edit = QLineEdit(str(self.config['shared']['x_label']))
    self.ylabel_edit = QLineEdit(str(self.config['shared']['y_label']))
    self.y_axis_min_edit = QLineEdit(str(self.config['shared']['y_axis_min']))
    self.y_axis_max_edit = QLineEdit(str(self.config['shared']['y_axis_max']))

    general_label = QLabel("General")
    general_label.setObjectName("sectionLabel")
    layout.addRow(general_label, QLabel())
    layout.addRow("Uncertainty Area Alpha:", self.alpha_uncertainty_area_edit)
    layout.addRow("Uncertainty Area Width:", self.width_uncertainty_area_edit)
    layout.addRow("Probability Curve Width:", self.width_probability_curve_edit)
    layout.addRow("X-label:", self.xlabel_edit)
    layout.addRow("Y-label:", self.ylabel_edit)
    layout.addRow("Y-axis Min Value:", self.y_axis_min_edit)
    layout.addRow("Y-axis Max Value:", self.y_axis_max_edit)
    layout.addRow("", QLabel())

    # X-line
    self.draw_x_line_checkbox = QCheckBox()
    self.draw_x_line_checkbox.setChecked(self.config['x_line'].get('draw', False))
    self.x_line_value_edit = QLineEdit(str(self.config['x_line']['value']))
    self.color_x_line_combo = CustomComboBox()
    self.color_x_line_combo.addItems(["blue", "green", "red", "black", "yellow", "cyan", "magenta"])
    self.color_x_line_combo.setCurrentText(self.config['x_line']['color'])
    self.width_x_line_edit = QLineEdit(str(self.config['x_line']['width']))
    self.x_line_label_edit = QLineEdit(str(self.config['x_line']['label']))
    self.linestyle_x_line_combo = CustomComboBox()
    self.linestyle_x_line_combo.addItems(["-", "--", "-.", ":"])
    self.linestyle_x_line_combo.setCurrentText(self.config['x_line']['linestyle'])

    x_line_label = QLabel("X-line")
    x_line_label.setObjectName("sectionLabel")
    layout.addRow(x_line_label, QLabel())
    layout.addRow("Draw X-line:", self.draw_x_line_checkbox)
    layout.addRow("X-value:", self.x_line_value_edit)
    layout.addRow("Color:", self.color_x_line_combo)
    layout.addRow("Line Width:", self.width_x_line_edit)
    layout.addRow("Line Style:", self.linestyle_x_line_combo)
    layout.addRow("Label:", self.x_line_label_edit)
    layout.addRow("", QLabel())

    # Y-line
    self.draw_y_line_checkbox = QCheckBox()
    self.draw_y_line_checkbox.setChecked(self.config['y_line'].get('draw', False))
    self.y_line_value_edit = QLineEdit(str(self.config['y_line']['value']))
    self.color_y_line_combo = CustomComboBox()
    self.color_y_line_combo.addItems(["blue", "green", "red", "black", "yellow", "cyan", "magenta"])
    self.color_y_line_combo.setCurrentText(self.config['y_line']['color'])
    self.width_y_line_edit = QLineEdit(str(self.config['y_line']['width']))
    self.y_line_label_edit = QLineEdit(str(self.config['y_line']['label']))
    self.linestyle_y_line_combo = CustomComboBox()
    self.linestyle_y_line_combo.addItems(["-", "--", "-.", ":"])
    self.linestyle_y_line_combo.setCurrentText(self.config['y_line']['linestyle'])

    y_line_label = QLabel("Y-line")
    y_line_label.setObjectName("sectionLabel")
    layout.addRow(y_line_label, QLabel())
    layout.addRow("Draw Y-line:", self.draw_y_line_checkbox)
    layout.addRow("Y-value:", self.y_line_value_edit)
    layout.addRow("Color:", self.color_y_line_combo)
    layout.addRow("Line Width:", self.width_y_line_edit)
    layout.addRow("Line Style:", self.linestyle_y_line_combo)
    layout.addRow("Label:", self.y_line_label_edit)
    layout.addRow("", QLabel())

    # Plot 1
    self.first_color_probability_curve_combo = CustomComboBox()
    self.first_color_probability_curve_combo.addItems(["blue", "green", "red", "black", "yellow", "cyan", "magenta"])
    self.first_color_probability_curve_combo.setCurrentText(self.config['plot_1']['color_probability_curve'])
    self.first_color_uncertainty_area_combo = CustomComboBox()
    self.first_color_uncertainty_area_combo.addItems(["lightblue", "lightgreen", "lightsalmon", "lightgray", "lightyellow", "lightcyan", "lightpink"])
    self.first_color_uncertainty_area_combo.setCurrentText(self.config['plot_1']['color_uncertainty_area'])
    self.first_probability_label_edit = QLineEdit(self.config['plot_1']['probability_label'])
    self.first_uncertantity_label_edit = QLineEdit(self.config['plot_1']['uncertantity_label'])
    self.first_probability_linestyle_combo = CustomComboBox()
    self.first_probability_linestyle_combo.addItems(["-", "--", "-.", ":"])
    self.first_probability_linestyle_combo.setCurrentText(self.config['plot_1']['linestyle'])

    first_label = QLabel("1st Plot")
    first_label.setObjectName("sectionLabel")
    layout.addRow(first_label, QLabel())
    layout.addRow("Probability Curve Color:", self.first_color_probability_curve_combo)
    layout.addRow("Uncertainty Area Color:", self.first_color_uncertainty_area_combo)
    layout.addRow("Probability Label:", self.first_probability_label_edit)
    layout.addRow("Uncertainty Label:", self.first_uncertantity_label_edit)
    layout.addRow("Line Style:", self.first_probability_linestyle_combo)
    layout.addRow("", QLabel())

    # Plot 2
    self.second_color_probability_curve_combo = CustomComboBox()
    self.second_color_probability_curve_combo.addItems(["blue", "green", "red", "black", "yellow", "cyan", "magenta"])
    self.second_color_probability_curve_combo.setCurrentText(self.config['plot_2']['color_probability_curve'])
    self.second_color_uncertainty_area_combo = CustomComboBox()
    self.second_color_uncertainty_area_combo.addItems(["lightblue", "lightgreen", "lightsalmon", "lightgray", "lightyellow", "lightcyan", "lightpink"])
    self.second_color_uncertainty_area_combo.setCurrentText(self.config['plot_2']['color_uncertainty_area'])
    self.second_probability_label_edit = QLineEdit(self.config['plot_2']['probability_label'])
    self.second_uncertantity_label_edit = QLineEdit(self.config['plot_2']['uncertantity_label'])
    self.second_probability_linestyle_combo = CustomComboBox()
    self.second_probability_linestyle_combo.addItems(["-", "--", "-.", ":"])
    self.second_probability_linestyle_combo.setCurrentText(self.config['plot_2']['linestyle'])

    second_label = QLabel("2nd Plot")
    second_label.setObjectName("sectionLabel")
    layout.addRow(second_label, QLabel())
    layout.addRow("Probability Curve Color:", self.second_color_probability_curve_combo)
    layout.addRow("Uncertainty Area Color:", self.second_color_uncertainty_area_combo)
    layout.addRow("Probability Label:", self.second_probability_label_edit)
    layout.addRow("Uncertainty Label:", self.second_uncertantity_label_edit)
    layout.addRow("Line Style:", self.second_probability_linestyle_combo)

    # Set up the scroll area
    scroll_area.setWidget(content_widget)

    # Add scroll area and save button to the dialog layout
    dialog_layout = QVBoxLayout(dialog)
    dialog_layout.addWidget(scroll_area)
    dialog_layout.addSpacing(5)
    save_button = QPushButton("Save")
    save_button.setObjectName("saveButton")
    save_button.clicked.connect(lambda: save_configuration(self, dialog))
    dialog_layout.addWidget(save_button, alignment=Qt.AlignRight)

    dialog.setLayout(dialog_layout)
    dialog.exec_()


def save_configuration(self, dialog):
    """Save the configuration values."""
    try:
        config = {
            "shared": {
                "x_label": self.xlabel_edit.text(),
                "y_label": self.ylabel_edit.text(),
                "width_probability_curve": validate_and_parse_float(self.width_probability_curve_edit.text(), "Probability Curve Width"),
                "width_uncertainty_area": validate_and_parse_float(self.width_uncertainty_area_edit.text(), "Uncertainty Area Width"),
                "alpha_uncertainty_area": validate_and_parse_float(self.alpha_uncertainty_area_edit.text(), "Uncertainty Area Alpha"),
                "y_axis_min": validate_and_parse_optional_float(self.y_axis_min_edit.text(), "Y-axis Min Value"),
                "y_axis_max": validate_and_parse_optional_float(self.y_axis_max_edit.text(), "Y-axis Max Value")
            },
            "x_line": {
                "draw": self.draw_x_line_checkbox.isChecked(),
                "value": validate_and_parse_float(self.x_line_value_edit.text(), "X-value"),
                "color": self.color_x_line_combo.currentText(),
                "width": validate_and_parse_float(self.width_x_line_edit.text(), "Line Width"),
                "label": self.x_line_label_edit.text(),
                "linestyle": self.linestyle_x_line_combo.currentText()
            },
            "y_line": {
                "draw": self.draw_y_line_checkbox.isChecked(),
                "value": validate_and_parse_float(self.y_line_value_edit.text(), "Y-value"),
                "color": self.color_y_line_combo.currentText(),
                "width": validate_and_parse_float(self.width_y_line_edit.text(), "Line Width"),
                "label": self.y_line_label_edit.text(),
                "linestyle": self.linestyle_y_line_combo.currentText()
            },
            "plot_1": {
                "color_probability_curve": self.first_color_probability_curve_combo.currentText(),
                "color_uncertainty_area": self.first_color_uncertainty_area_combo.currentText(),
                "probability_label": self.first_probability_label_edit.text(),
                "uncertantity_label": self.first_uncertantity_label_edit.text(),
                "linestyle": self.first_probability_linestyle_combo.currentText()
            },
            "plot_2": {
                "color_probability_curve": self.second_color_probability_curve_combo.currentText(),
                "color_uncertainty_area": self.second_color_uncertainty_area_combo.currentText(),
                "probability_label": self.second_probability_label_edit.text(),
                "uncertantity_label": self.second_uncertantity_label_edit.text(),
                "linestyle": self.second_probability_linestyle_combo.currentText()
            }
        }

        if not validate_configuration(self, config):
            return
        
        self.config = config
        write_configuration(self)
        dialog.accept()

    except ValueError as e:
        QMessageBox.warning(self, "Invalid Input", str(e))
        return


def validate_and_parse_float(value, field_name):
    """Validate and parse a string value as a float."""
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid value for {field_name}: {value}. Please enter a numeric value.")

def validate_and_parse_optional_float(value, field_name):
    """Parse a float if the value is provided; otherwise return None."""
    if value.strip() == "None":
        return None
    return validate_and_parse_float(value, field_name)

def validate_configuration(self, config):
    """Validate the configuration values."""
    if config['shared']['width_probability_curve'] <= 0:
        QMessageBox.warning(self, "Invalid Input", "'Probability Curve Width' must be positive.")
        return False
    
    if config['shared']['width_uncertainty_area'] < 0:
        QMessageBox.warning(self, "Invalid Input", "'Uncertainty Area Width' cannot be negative.")
        return False
    
    if config['shared']['alpha_uncertainty_area'] < 0 or config['shared']['alpha_uncertainty_area'] > 1:
        QMessageBox.warning(self, "Invalid Input", "'Uncertainty Area Alpha' must be between 0 and 1.")
        return False

    if config['x_line']['width'] < 0:
        QMessageBox.warning(self, "Invalid Input", "X-line 'Line Width' cannot be negative.")
        return False
    
    if config['y_line']['width'] < 0:
        QMessageBox.warning(self, "Invalid Input", "Y-line 'Line Width' cannot be negative.")
        return False

    return True
