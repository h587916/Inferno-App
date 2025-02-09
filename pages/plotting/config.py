import os
import json
import importlib.resources
from PySide6.QtWidgets import (QDialog, QFormLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QMessageBox, QScrollArea, QWidget, QVBoxLayout)
from PySide6.QtCore import Qt
from appdirs import user_data_dir
from pages.plotting.custom_combobox import CustomComboBox


APP_DIR = user_data_dir("Inferno App", "inferno")
USER_CONFIG_PATH = os.path.join(APP_DIR, 'config/plotting_config.json')


def load_configuration(page):
    """Load configuration from JSON file."""
    with open(USER_CONFIG_PATH, 'r') as f:
        page.config = json.load(f)


def write_configuration(page):
    """Write configuration to JSON file."""
    with open(USER_CONFIG_PATH, 'w') as f:
        json.dump(page.config, f)


def reset_configuration(page):
    """Reset the configuration to default values."""
    with importlib.resources.open_text('pages.plotting', 'default_config.json') as f:
        page.config = json.load(f)


def update_configuration(page):
    """Update the configuration dynamically based on current selections and data in PlottingPage."""
    plot_variable = page.plot_variable_combobox.currentText()
    categorical_variable = page.categorical_variable_combobox.currentText()
    if categorical_variable == "No":
        categorical_variable = None

    page.config['shared']['x_label'] = plot_variable

    if page.selected_func == "tailPr":
        other_values = []
        all_selected_vars = page.selected_x_values
        for var in all_selected_vars:
            if var == plot_variable or var == categorical_variable:
                continue
            val = page.variable_values.get(var)
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

        if categorical_variable and categorical_variable in page.variable_values:
            categories = page.variable_values[categorical_variable]
            for i, category in enumerate(categories, start=1):
                plot_key = f"plot_{i}"
                page.config[plot_key]['probability_label'] = f"{', '.join(other_values)}, {category}"
                page.config[plot_key]['uncertantity_label'] = ""
        else:
            plot_key = "plot_1"
            page.config[plot_key]['probability_label'] = ", ".join(other_values)
            page.config[plot_key]['uncertantity_label'] = ""

    elif page.selected_func == "Pr":
        num_variables = page.probabilities_values.shape[1] if page.probabilities_values is not None else 1

        other_values = []
        all_selected_vars = page.selected_y_values + page.selected_x_values
        for var in all_selected_vars:
            if var == plot_variable or var == categorical_variable:
                continue
            val = page.variable_values.get(var)
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
        if categorical_variable and categorical_variable in page.variable_values:
            categorical_values = page.variable_values[categorical_variable]
            for cat_val in categorical_values:
                line_label_parts = list(other_values) + [cat_val]
                line_labels.append(", ".join(line_label_parts))
        else:
            if num_variables > 1:
                # Try to see if plot_variable is in Y or X
                if plot_variable in page.Y.columns:
                    x_line_values = page.Y[plot_variable].unique()
                elif plot_variable in page.X.columns:
                    x_line_values = page.X[plot_variable].unique()
                else:
                    x_line_values = [f"Line {i+1}" for i in range(num_variables)]
                x_line_values = list(map(str, x_line_values))
                for val in x_line_values:
                    line_label_parts = list(other_values) + [val]
                    line_labels.append(", ".join(line_label_parts))
            else:
                label = ", ".join(other_values) if other_values else "Line 1"
                line_labels.append(label)

        for i, label in enumerate(line_labels, start=1):
            plot_key = f"plot_{i}"
            if plot_key in page.config:
                page.config[plot_key]['probability_label'] = label


def configure_plot(page):
    """Open a dialog to configure plot settings."""
    dialog = QDialog(page)
    dialog.setFixedWidth(300)
    dialog.setMaximumHeight(850)
    dialog.setWindowTitle("Configure Plot Settings")

    # Scroll area setup
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    # Main content widget inside the scroll area
    content_widget = QWidget()
    layout = QFormLayout(content_widget)

    # Shared Fields
    page.width_probability_curve_edit = QLineEdit(str(page.config['shared']['width_probability_curve']))
    page.width_uncertainty_area_edit = QLineEdit(str(page.config['shared']['width_uncertainty_area']))
    page.alpha_uncertainty_area_edit = QLineEdit(str(page.config['shared']['alpha_uncertainty_area']))
    page.xlabel_edit = QLineEdit(str(page.config['shared']['x_label']))
    page.ylabel_edit = QLineEdit(str(page.config['shared']['y_label']))

    general_label = QLabel("General")
    general_label.setObjectName("sectionLabel")
    layout.addRow(general_label, QLabel())
    layout.addRow("Uncertainty Area Alpha:", page.alpha_uncertainty_area_edit)
    layout.addRow("Uncertainty Area Width:", page.width_uncertainty_area_edit)
    layout.addRow("Probability Curve Width:", page.width_probability_curve_edit)
    layout.addRow("X-label:", page.xlabel_edit)
    layout.addRow("Y-label:", page.ylabel_edit)
    layout.addRow("", QLabel())

    # X-line
    page.draw_x_line_checkbox = QCheckBox()
    page.draw_x_line_checkbox.setChecked(page.config['x_line'].get('draw', False))
    page.x_line_value_edit = QLineEdit(str(page.config['x_line']['value']))
    page.color_x_line_combo = CustomComboBox()
    page.color_x_line_combo.addItems(["blue", "green", "red", "black", "yellow", "cyan", "magenta"])
    page.color_x_line_combo.setCurrentText(page.config['x_line']['color'])
    page.width_x_line_edit = QLineEdit(str(page.config['x_line']['width']))
    page.x_line_label_edit = QLineEdit(str(page.config['x_line']['label']))

    x_line_label = QLabel("X-line")
    x_line_label.setObjectName("sectionLabel")
    layout.addRow(x_line_label, QLabel())
    layout.addRow("Draw X-line:", page.draw_x_line_checkbox)
    layout.addRow("X-value:", page.x_line_value_edit)
    layout.addRow("Color:", page.color_x_line_combo)
    layout.addRow("Line Width:", page.width_x_line_edit)
    layout.addRow("Label:", page.x_line_label_edit)
    layout.addRow("", QLabel())

    # Y-line
    page.draw_y_line_checkbox = QCheckBox()
    page.draw_y_line_checkbox.setChecked(page.config['y_line'].get('draw', False))
    page.y_line_value_edit = QLineEdit(str(page.config['y_line']['value']))
    page.color_y_line_combo = CustomComboBox()
    page.color_y_line_combo.addItems(["blue", "green", "red", "black", "yellow", "cyan", "magenta"])
    page.color_y_line_combo.setCurrentText(page.config['y_line']['color'])
    page.width_y_line_edit = QLineEdit(str(page.config['y_line']['width']))
    page.y_line_label_edit = QLineEdit(str(page.config['y_line']['label']))

    y_line_label = QLabel("Y-line")
    y_line_label.setObjectName("sectionLabel")
    layout.addRow(y_line_label, QLabel())
    layout.addRow("Draw Y-line:", page.draw_y_line_checkbox)
    layout.addRow("Y-value:", page.y_line_value_edit)
    layout.addRow("Color:", page.color_y_line_combo)
    layout.addRow("Line Width:", page.width_y_line_edit)
    layout.addRow("Label:", page.y_line_label_edit)
    layout.addRow("", QLabel())

    # Plot 1
    page.first_color_probability_curve_combo = CustomComboBox()
    page.first_color_probability_curve_combo.addItems(["blue", "green", "red", "black", "yellow", "cyan", "magenta"])
    page.first_color_probability_curve_combo.setCurrentText(page.config['plot_1']['color_probability_curve'])
    page.first_color_uncertainty_area_combo = CustomComboBox()
    page.first_color_uncertainty_area_combo.addItems(["lightblue", "lightgreen", "lightsalmon", "lightgray", "lightyellow", "lightcyan", "lightpink"])
    page.first_color_uncertainty_area_combo.setCurrentText(page.config['plot_1']['color_uncertainty_area'])
    page.first_probability_label_edit = QLineEdit(page.config['plot_1']['probability_label'])
    page.first_uncertantity_label_edit = QLineEdit(page.config['plot_1']['uncertantity_label'])

    first_label = QLabel("1st Plot")
    first_label.setObjectName("sectionLabel")
    layout.addRow(first_label, QLabel())
    layout.addRow("Probability Curve Color:", page.first_color_probability_curve_combo)
    layout.addRow("Uncertainty Area Color:", page.first_color_uncertainty_area_combo)
    layout.addRow("Probability Label:", page.first_probability_label_edit)
    layout.addRow("Uncertainty Label:", page.first_uncertantity_label_edit)
    layout.addRow("", QLabel())

    # Plot 2
    page.second_color_probability_curve_combo = CustomComboBox()
    page.second_color_probability_curve_combo.addItems(["blue", "green", "red", "black", "yellow", "cyan", "magenta"])
    page.second_color_probability_curve_combo.setCurrentText(page.config['plot_2']['color_probability_curve'])
    page.second_color_uncertainty_area_combo = CustomComboBox()
    page.second_color_uncertainty_area_combo.addItems(["lightblue", "lightgreen", "lightsalmon", "lightgray", "lightyellow", "lightcyan", "lightpink"])
    page.second_color_uncertainty_area_combo.setCurrentText(page.config['plot_2']['color_uncertainty_area'])
    page.second_probability_label_edit = QLineEdit(page.config['plot_2']['probability_label'])
    page.second_uncertantity_label_edit = QLineEdit(page.config['plot_2']['uncertantity_label'])

    second_label = QLabel("2nd Plot")
    second_label.setObjectName("sectionLabel")
    layout.addRow(second_label, QLabel())
    layout.addRow("Probability Curve Color:", page.second_color_probability_curve_combo)
    layout.addRow("Uncertainty Area Color:", page.second_color_uncertainty_area_combo)
    layout.addRow("Probability Label:", page.second_probability_label_edit)
    layout.addRow("Uncertainty Label:", page.second_uncertantity_label_edit)

    # Set up the scroll area
    scroll_area.setWidget(content_widget)

    # Add scroll area and save button to the dialog layout
    dialog_layout = QVBoxLayout(dialog)
    dialog_layout.addWidget(scroll_area)
    dialog_layout.addSpacing(5)
    save_button = QPushButton("Save")
    save_button.setObjectName("saveButton")
    save_button.clicked.connect(lambda: save_configuration(page, dialog))
    dialog_layout.addWidget(save_button, alignment=Qt.AlignRight)

    dialog.setLayout(dialog_layout)
    dialog.exec_()


def save_configuration(page, dialog):
    """Save the configuration values."""
    try:
        config = {
            "shared": {
                "x_label": page.xlabel_edit.text(),
                "y_label": page.ylabel_edit.text(),
                "width_probability_curve": validate_and_parse_float(page.width_probability_curve_edit.text(), "Probability Curve Width"),
                "width_uncertainty_area": validate_and_parse_float(page.width_uncertainty_area_edit.text(), "Uncertainty Area Width"),
                "alpha_uncertainty_area": validate_and_parse_float(page.alpha_uncertainty_area_edit.text(), "Uncertainty Area Alpha")
            },
            "x_line": {
                "draw": page.draw_x_line_checkbox.isChecked(),
                "value": validate_and_parse_float(page.x_line_value_edit.text(), "X-value"),
                "color": page.color_x_line_combo.currentText(),
                "width": validate_and_parse_float(page.width_x_line_edit.text(), "Line Width"),
                "label": page.x_line_label_edit.text()
            },
            "y_line": {
                "draw": page.draw_y_line_checkbox.isChecked(),
                "value": validate_and_parse_float(page.y_line_value_edit.text(), "Y-value"),
                "color": page.color_y_line_combo.currentText(),
                "width": validate_and_parse_float(page.width_y_line_edit.text(), "Line Width"),
                "label": page.y_line_label_edit.text()
            },
            "plot_1": {
                "color_probability_curve": page.first_color_probability_curve_combo.currentText(),
                "color_uncertainty_area": page.first_color_uncertainty_area_combo.currentText(),
                "probability_label": page.first_probability_label_edit.text(),
                "uncertantity_label": page.first_uncertantity_label_edit.text()
            },
            "plot_2": {
                "color_probability_curve": page.second_color_probability_curve_combo.currentText(),
                "color_uncertainty_area": page.second_color_uncertainty_area_combo.currentText(),
                "probability_label": page.second_probability_label_edit.text(),
                "uncertantity_label": page.second_uncertantity_label_edit.text()
            }
        }

        if not validate_configuration(page, config):
            return
        
        page.config = config
        write_configuration(page)
        dialog.accept()

    except ValueError as e:
        QMessageBox.warning(page, "Invalid Input", str(e))
        return


def validate_and_parse_float(value, field_name):
    """Validate and parse a string value as a float."""
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid value for {field_name}: {value}. Please enter a numeric value.")


def validate_configuration(page, config):
    """Validate the configuration values."""
    if config['shared']['width_probability_curve'] <= 0:
        QMessageBox.warning(page, "Invalid Input", "'Probability Curve Width' must be positive.")
        return False
    
    if config['shared']['width_uncertainty_area'] < 0:
        QMessageBox.warning(page, "Invalid Input", "'Uncertainty Area Width' cannot be negative.")
        return False
    
    if config['shared']['alpha_uncertainty_area'] < 0 or config['shared']['alpha_uncertainty_area'] > 1:
        QMessageBox.warning(page, "Invalid Input", "'Uncertainty Area Alpha' must be between 0 and 1.")
        return False

    if config['x_line']['width'] < 0:
        QMessageBox.warning(page, "Invalid Input", "X-line 'Line Width' cannot be negative.")
        return False
    
    if config['y_line']['width'] < 0:
        QMessageBox.warning(page, "Invalid Input", "Y-line 'Line Width' cannot be negative.")
        return False

    return True
