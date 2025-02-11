import os
import pandas as pd
from PySide6.QtWidgets import QMessageBox, QListWidget, QAbstractItemView, QHBoxLayout, QLabel, QLineEdit, QWidget, QSizePolicy
from PySide6.QtCore import Qt
from pages.custom_combobox import CustomComboBox
from pages.plotting.plotting import clear_plot
from appdirs import user_data_dir


APP_DIR = user_data_dir("Inferno App", "inferno")
LEARNT_FOLDER = os.path.join(APP_DIR, 'learnt')


def load_variables_into_lists(self):
    """Load variates from the metadata.csv file into the list widgets."""
    learnt_folder = self.pr_learnt_combobox.currentText()
    metadata_path = os.path.join(LEARNT_FOLDER, learnt_folder, 'metadata.csv')

    if not os.path.exists(metadata_path):
        QMessageBox.warning(None, "Error", "Metadata file not found.")
        return
    
    try:
        self.metadata_df = pd.read_csv(metadata_path)
        self.Y_listwidget.clear()
        self.X_listwidget.clear()

        variates = self.metadata_df["name"].tolist()
        for var_name in variates:
            self.metadata_dict[var_name] = get_metadata_for_selected_value(self, var_name)

        for var_name in variates:
            var_type = self.metadata_dict[var_name].get("type", "").lower()

            self.X_listwidget.addItem(var_name)

            if self.selected_func == "tailPr":
                if var_type == "continuous" or (var_type == "ordinal" and "options" not in self.metadata_dict[var_name]):
                    self.Y_listwidget.addItem(var_name)
            else:
                self.Y_listwidget.addItem(var_name)

        adjust_list_widget_height(self.Y_listwidget)
        adjust_list_widget_height(self.X_listwidget)

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load metadata: {str(e)}")

def adjust_list_widget_height(list_widget, max_visible_items=20):
    num_items = list_widget.count()
    visible_items = min(num_items, max_visible_items)
    row_height = list_widget.sizeHintForRow(0) if list_widget.count() > 0 else 20
    total_height = row_height * visible_items + 2 * list_widget.frameWidth()
    list_widget.setFixedHeight(total_height)
    list_widget.setMinimumHeight(40)

def get_metadata_for_selected_value(self, variable_name):
    """Retrieve metadata for a single selected variable from the metadata.csv file."""
    try:
        row = self.metadata_df[self.metadata_df["name"] == variable_name].iloc[0]

        total_columns = len(self.metadata_df.columns)
        v_column_count = total_columns - 7
        v_columns = [f"V{i}" for i in range(1, v_column_count + 1)]
        
        var_type = row["type"].lower()
        var_metadata = {"type": var_type}

        if var_type == "nominal":
            var_metadata["options"] = [row[col] for col in v_columns if pd.notna(row.get(col))]

        elif var_type == "continuous":
            var_metadata["domainmin"] = float(row.get("domainmin"))
            var_metadata["domainmax"] = float(row.get("domainmax"))

        elif var_type == "ordinal":
            options = [row[col] for col in v_columns if pd.notna(row.get(col))]
            if options:
                var_metadata["options"] = options
            else:
                var_metadata["domainmin"] = float(row.get("domainmin"))
                var_metadata["domainmax"] = float(row.get("domainmax"))

        return var_metadata

    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to retrieve metadata for {variable_name}: {str(e)}")
        return {}


def is_numeric(self, variable):
    """Check if a variable is numeric based on its metadata."""
    var_metadata = self.metadata_dict.get(variable, {})
    var_type = var_metadata.get("type", "").lower()
    return var_type == "continuous" or (var_type == "ordinal" and "options" not in var_metadata)


def update_plot_variable_combobox(self, selected_vars):
        """Update the plot variable combobox based on the selected function type."""
        self.plot_variable_combobox.blockSignals(True)
        self.plot_variable_combobox.clear()

        if not selected_vars:
            self.plot_variable_frame.hide()
            self.plot_variable_combobox.blockSignals(False)
            return

        added_any_numeric = False
        for var in selected_vars:
            if is_numeric(self, var):
                self.plot_variable_combobox.addItem(var)
                added_any_numeric = True

        self.plot_variable_combobox.setCurrentIndex(-1)
        self.plot_variable_combobox.blockSignals(False)

        if added_any_numeric:
            self.plot_variable_frame.show()
        else:
            self.plot_variable_frame.hide()

def sync_variable_selections(self, added_variables, removed_variables):
    """Update metadata, comboboxes, and UI components in response to changes in selected variables in the list widgets."""
    self.plot_variable_combobox.blockSignals(True)

    for value in added_variables:
        if value not in self.metadata_dict:
            self.metadata_dict[value] = get_metadata_for_selected_value(self, value)
    
    for value in removed_variables:
        if value in self.metadata_dict:
            del self.metadata_dict[value]
            idx = self.plot_variable_combobox.findText(value)
            if idx >= 0:
                self.plot_variable_combobox.removeItem(idx)

    self.plot_variable_combobox.setCurrentIndex(-1)
    self.plot_variable_combobox.blockSignals(False)

    if self.plot_variable_combobox.currentIndex() < 0:
        self.categorical_variable_combobox.clear()
        self.categorical_variable_frame.hide()
        clear_input_layout(self)

    update_disabled_items(self)
    update_X_list_visibility(self)
    self.update_plot_title()
    clear_plot(self)

def update_categorical_variable_combobox(self):
    """Update the categorical variable combobox based on selected X variables."""
    if self.plot_variable_combobox.currentIndex() < 0:
        self.categorical_variable_combobox.clear()
        self.categorical_variable_frame.hide()
        return
    elif self.plot_variable_combobox.currentText() in self.selected_x_values:
        variables = self.selected_y_values
    elif self.plot_variable_combobox.currentText() in self.selected_y_values:
        variables = self.selected_x_values
    
    categorical_variables = []

    for variable in variables:
        if not is_numeric(self, variable):
            categorical_variables.append(variable)

    if categorical_variables:
        self.categorical_variable_combobox.blockSignals(True)
        self.categorical_variable_combobox.clear()
        self.categorical_variable_combobox.addItem("No")
        self.categorical_variable_combobox.addItems(categorical_variables)
        self.categorical_variable_combobox.setCurrentIndex(0)
        self.categorical_variable_combobox.blockSignals(False)
        self.categorical_variable_frame.show()
    else:
        self.categorical_variable_combobox.clear()
        self.categorical_variable_frame.hide()

def update_disabled_items(self):
    """Disable selected items in the opposite list to prevent cross-selection."""
    disable_item(self.Y_listwidget, self.selected_x_values)
    disable_item(self.X_listwidget, self.selected_y_values)

def disable_item(listwidget, selected_values):
    for i in range(listwidget.count()):
        item = listwidget.item(i)
        item.setFlags(item.flags() | Qt.ItemIsEnabled)
        if item.text() in selected_values:
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

def update_X_list_visibility(self):
    """Show or hide the input frame based on the selected Y and X values."""
    if self.selected_func == "tailPr":
        self.plot_variable_frame.hide()

    if self.Y_listwidget.selectedItems():
        self.X_label_widget.show()
        self.X_listwidget.show()

        if self.selected_func == "Pr":
            self.plot_variable_frame.show()
    else:
        self.X_label_widget.hide()
        self.X_listwidget.clearSelection()
        self.selected_x_values = []
        self.X_listwidget.hide()
        self.plot_variable_frame.hide()
        clear_input_layout(self)

def clear_input_layout(self):
    """Clear and hide the values layout."""
    while self.values_layout.count():
        item = self.values_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
    self.variable_values.clear()
    self.input_fields.clear()
    self.input_frame.hide()

def update_values_layout_pr(self):
    """Update the values layout based on the selected variables."""
    clear_list_widget(self)
    variables = self.selected_y_values + self.selected_x_values
    plot_variable = self.plot_variable_combobox.currentText()
    categorical_variable = self.categorical_variable_combobox.currentText()

    font = QLabel().font()
    font.setPointSize(10)

    for variable in variables:
        label = QLabel(f"{variable} = ")
        label.setObjectName("variables")

        var_type = self.metadata_dict.get(variable, {}).get("type")

        if variable == categorical_variable:
            options = self.metadata_dict[variable].get("options", [])
            list_widget = QListWidget()
            list_widget.setFont(font)
            list_widget.itemSelectionChanged.connect(lambda: limit_selection(self, list_widget, 2))
            list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
            list_widget.addItems(options)
            if variable in self.variable_values:
                selected_options = self.variable_values[variable]
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    if item.text() in selected_options:
                        item.setSelected(True)
            list_widget.itemSelectionChanged.connect(lambda: value_changed(self))
            adjust_list_widget_height(list_widget)
            list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            list_widget.setObjectName("listWidget")

            self.values_layout.addRow(label, list_widget)

            self.input_fields[variable] = (label, list_widget)
            self.current_list_widget = list_widget

        elif var_type == "nominal" or (var_type == "ordinal" and "options" in self.metadata_dict[variable]):
            options = self.metadata_dict[variable].get("options", [])
            input_box = CustomComboBox()
            input_box.setFont(font)
            input_box.addItems(options)
            if variable in self.variable_values:
                input_box.setCurrentText(self.variable_values[variable])
            input_box.currentIndexChanged.connect(lambda: value_changed(self))

            self.values_layout.addRow(label, input_box)
            self.input_fields[variable] = (label, input_box)

        elif var_type == "continuous" or (var_type == "ordinal" and "options" not in self.metadata_dict[variable]):
            if variable == plot_variable:
                ranged_layout = QHBoxLayout()
                ranged_layout.setAlignment(Qt.AlignLeft)

                start_label = QLabel("From ")
                start_label.setObjectName("variables")
                start_input = QLineEdit()
                start_input.setObjectName("inputField")
                start_input.setFixedSize(70, 30)
                start_input.setPlaceholderText("Enter value")
                start_input.textChanged.connect(lambda: value_changed(self))
                start_input.setAlignment(Qt.AlignCenter)

                end_label = QLabel(" To ")
                end_label.setObjectName("variables")
                end_input = QLineEdit()
                end_input.setObjectName("inputField")
                end_input.setFixedSize(70, 30)
                end_input.setPlaceholderText("Enter value")
                end_input.textChanged.connect(lambda: value_changed(self))
                end_input.setAlignment(Qt.AlignCenter)

                if variable in self.variable_values:
                    start_val = self.variable_values[variable].get('start', '')
                    end_val = self.variable_values[variable].get('end', '')
                    start_input.setText(start_val)
                    end_input.setText(end_val)

                ranged_layout.addWidget(start_label)
                ranged_layout.addWidget(start_input)
                ranged_layout.addWidget(end_label)
                ranged_layout.addWidget(end_input)
                ranged_layout.addStretch()

                self.values_layout.addRow(label, ranged_layout)
                self.input_fields[variable] = (label, {'start': start_input, 'end': end_input, 'start_label': start_label, 'end_label': end_label})

            else:
                input_box = QLineEdit()
                input_box.setObjectName("inputField")
                input_box.setFixedSize(70, 30)
                input_box.setPlaceholderText("Enter value")
                input_box.textChanged.connect(lambda: value_changed(self))
                input_box.setAlignment(Qt.AlignCenter)

                if variable in self.variable_values:
                    input_box.setText(self.variable_values[variable])

                self.values_layout.addRow(label, input_box)
                self.input_fields[variable] = (label, input_box)

        else:
            QMessageBox.warning(None, "Error", f"Invalid variable type for {variable}: {var_type}")

        add_custom_spacing(self.values_layout, 3)

def clear_list_widget(self):
    if self.current_list_widget:
        self.current_list_widget.deleteLater()
        self.current_list_widget = None

def limit_selection(self, list_widget, max_items):
    """Limit the selection in the list_widget to a maximum number of items."""
    selected_items = list_widget.selectedItems()
    if len(selected_items) > max_items:
        for item in selected_items[max_items:]:
            item.setSelected(False)
        QMessageBox.warning(self, "Selection Limit", f"You can select maximum {max_items} variables.")

def update_values_layout_tailpr(self):
    """Update the values layout specifically for the TailPr function."""
    clear_input_layout(self)

    variables = self.selected_y_values + self.selected_x_values
    plot_var = self.plot_variable_combobox.currentText()
    categorical_variable = self.categorical_variable_combobox.currentText()
    
    font = QLabel().font()
    font.setPointSize(10)

    for variable in variables:
        label = QLabel(f"{variable} = ")
        label.setObjectName("variables")

        var_metadata = self.metadata_dict.get(variable, {})
        var_type = var_metadata.get("type", "")

        if variable in self.selected_y_values:
            tailpr_y_layout = QHBoxLayout()
            tailpr_y_layout.setAlignment(Qt.AlignLeft)

            inequality_box = CustomComboBox()
            inequality_box.setFont(font)
            inequality_box.addItems(["<", ">", "<=", ">="])
            inequality_box.currentIndexChanged.connect(lambda: value_changed(self))

            value_input = QLineEdit()
            value_input.setObjectName("inputField")
            value_input.setFixedSize(70, 30)
            value_input.setPlaceholderText("Enter numeric value")
            value_input.textChanged.connect(lambda: value_changed(self))
            value_input.setAlignment(Qt.AlignCenter)

            if variable in self.variable_values:
                stored_val = self.variable_values[variable]
                if isinstance(stored_val, dict):
                    inequality = stored_val.get('inequality', '<')
                    numeric_val = stored_val.get('value', '')
                    inequality_box.setCurrentText(inequality)
                    value_input.setText(numeric_val)

            tailpr_y_layout.addWidget(inequality_box)
            tailpr_y_layout.addWidget(value_input)
            tailpr_y_layout.addStretch()

            self.values_layout.addRow(label, tailpr_y_layout)

            self.input_fields[variable] = (
                label,
                {
                    'inequality': inequality_box,
                    'value': value_input
                }
            )

        elif variable == categorical_variable:
            options = self.metadata_dict[variable].get("options", [])
            list_widget = QListWidget()
            list_widget.setFont(font)
            list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
            list_widget.addItems(options)
            list_widget.itemSelectionChanged.connect(lambda: limit_selection(self, list_widget, 2))
            if variable in self.variable_values:
                selected_options = self.variable_values[variable]
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    if item.text() in selected_options:
                        item.setSelected(True)
            list_widget.itemSelectionChanged.connect(lambda: value_changed(self))
            adjust_list_widget_height(list_widget)
            list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            list_widget.setObjectName("listWidget")

            self.values_layout.addRow(label, list_widget)

            self.input_fields[variable] = (label, list_widget)
            self.current_list_widget = list_widget 

        elif var_type == "nominal" or (var_type == "ordinal" and "options" in var_metadata):
            options = var_metadata.get("options", [])
            input_box = CustomComboBox()
            input_box.setFont(font)
            input_box.addItems(options)
            if variable in self.variable_values:
                input_box.setCurrentText(self.variable_values[variable])
            input_box.currentIndexChanged.connect(lambda: value_changed(self))

            self.values_layout.addRow(label, input_box)
            self.input_fields[variable] = (label, input_box)

        elif var_type == "continuous" or (var_type == "ordinal" and "options" not in var_metadata):
            ranged_layout = QHBoxLayout()
            ranged_layout.setAlignment(Qt.AlignLeft)

            start_label = QLabel("From ")
            start_label.setObjectName("variables")
            start_input = QLineEdit()
            start_input.setObjectName("inputField")
            start_input.setFixedSize(70, 30)
            start_input.setPlaceholderText("Enter value")
            start_input.textChanged.connect(lambda: value_changed(self))
            start_input.setAlignment(Qt.AlignCenter)

            end_label = QLabel(" To ")
            end_label.setObjectName("variables")
            end_input = QLineEdit()
            end_input.setObjectName("inputField")
            end_input.setFixedSize(70, 30)
            if variable == plot_var:
                end_input.setPlaceholderText("Enter value")  # No "(optional)" text for the plot variable
            else:
                end_input.setPlaceholderText("(optional)")
            end_input.textChanged.connect(lambda: value_changed(self))
            end_input.setAlignment(Qt.AlignCenter)

            if variable in self.variable_values:
                stored_vals = self.variable_values[variable]
                if isinstance(stored_vals, dict):
                    start_val = stored_vals.get('start', '')
                    end_val = stored_vals.get('end', '')
                    start_input.setText(start_val)
                    end_input.setText(end_val)

            ranged_layout.addWidget(start_label)
            ranged_layout.addWidget(start_input)
            ranged_layout.addWidget(end_label)
            ranged_layout.addWidget(end_input)
            ranged_layout.addStretch()

            self.values_layout.addRow(label, ranged_layout)

            self.input_fields[variable] = (
                label,
                {
                    'start': start_input,
                    'end': end_input
                }
            )
        else:
            QMessageBox.warning(self, "Error", f"Invalid variable type for {variable}: {var_type}")

        add_custom_spacing(self.values_layout, 3)

def add_custom_spacing(layout, height):
    """ Adds custom vertical spacing to a QFormLayout using a transparent QWidget with fixed height. """
    spacer_widget = QWidget()
    spacer_widget.setFixedHeight(height)
    spacer_widget.setStyleSheet("background-color: transparent;")
    layout.addRow(spacer_widget)

def value_changed(self):
    """Update the stored variable values when the input value changes."""
    self.variable_values = get_input_value(self, self.selected_y_values + self.selected_x_values)
    clear_plot(self)
    self.update_plot_title()

def get_input_value(self, selected_values):
    """Get the input values from the widgets."""
    input_values = {}
    for variable in selected_values:
        if variable in self.input_fields:
            _, widget = self.input_fields[variable]

            if isinstance(widget, dict) and 'start' in widget and 'end' in widget:
                start_input = widget['start']
                end_input = widget['end']
                start_value = start_input.text()
                end_value = end_input.text()
                input_values[variable] = {'start': start_value, 'end': end_value}
            elif isinstance(widget, QListWidget):
                selected_items = widget.selectedItems()
                values = [item.text() for item in selected_items]
                input_values[variable] = values
            elif isinstance(widget, QLineEdit):
                value = widget.text()
                input_values[variable] = value
            elif isinstance(widget, dict) and 'inequality' in widget and 'value' in widget:
                inequality_box = widget['inequality']
                value_edit = widget['value']
                selected_inequality = inequality_box.currentText()
                numeric_value = value_edit.text()
                input_values[variable] = {
                    'inequality': selected_inequality,
                    'value': numeric_value
                }
            else:
                if isinstance(widget, CustomComboBox):
                    input_values[variable] = widget.currentText()
                else:
                    QMessageBox.warning(None, "Error", f"Invalid input field for {variable}")
    return input_values