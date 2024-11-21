import os
import json
import numpy as np
import pandas as pd
import importlib.resources
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QHBoxLayout, 
                                QComboBox, QListWidget, QFileDialog, QAbstractItemView, QFormLayout, QLineEdit, 
                                QMessageBox, QSizePolicy, QAbstractItemView, QDialog, QSpacerItem)
from PySide6.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from r_integration.inferno_functions import run_Pr
from scipy.interpolate import make_interp_spline

# Define the base directory paths (consistent with file_manager.py)
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, '.inferno_app')

UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
LEARNT_FOLDER = os.path.join(APP_DIR, 'learnt')
USER_CONFIG_PATH = os.path.join(APP_DIR, 'config/plotting_config.json')

class CustomComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()

class PlottingPage(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.plot = False
        self.plot_canvas = None
        self.selected_y_values = []
        self.selected_x_values = []
        self.metadata_df = pd.DataFrame()
        self.metadata_dict = {}
        self.variable_values = {}
        self.input_fields = {}

        main_layout = QVBoxLayout()

        # Set page title
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 40)  # left, top, right, bottom
        title_label = QLabel("Plotting Probabilities")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        main_layout.addLayout(title_layout)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(50, 0, 50, 20) # left, top, right, bottom

        # --- Left side of the page ---
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)

        # Learnt folder selection
        self.learn_frame = QFrame()
        self.learn_frame.setObjectName("learnFrame")
        learnt_layout = QHBoxLayout(self.learn_frame)
        learnt_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        learnt_layout.setSpacing(5)

        learnt_label = QLabel("Select a learnt folder:")
        self.pr_learnt_combobox = CustomComboBox()
        self.pr_learnt_combobox.currentIndexChanged.connect(self.on_learnt_folder_selected)

        learnt_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.pr_learnt_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        learnt_layout.addWidget(learnt_label)
        learnt_layout.addWidget(self.pr_learnt_combobox)

        left_layout.addWidget(self.learn_frame, alignment=Qt.AlignTop)

        # Variable selection frame
        self.variable_selection_frame = QFrame()
        self.variable_selection_frame.setObjectName("variableSelectionFrame")
        self.variable_selection_frame.hide()
        variable_selection_layout = QVBoxLayout(self.variable_selection_frame)

        Y_label_widget = QLabel("Select target Y-variables:")
        variable_selection_layout.addWidget(Y_label_widget)

        self.Y_listwidget = QListWidget()
        self.Y_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.Y_listwidget.itemSelectionChanged.connect(self.on_Y_variable_selected)
        variable_selection_layout.addWidget(self.Y_listwidget)

        variable_selection_layout.addSpacing(20)
        
        self.X_label_widget = QLabel("Select conditional X-variables (optional):")
        self.X_label_widget.hide()
        variable_selection_layout.addWidget(self.X_label_widget)

        self.X_listwidget = QListWidget()
        self.X_listwidget.hide()
        self.X_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.X_listwidget.itemSelectionChanged.connect(self.on_X_variable_selected)
        variable_selection_layout.addWidget(self.X_listwidget)

        left_layout.addWidget(self.variable_selection_frame, alignment=Qt.AlignTop)

        # Which variable should be plotted against the probabilities
        self.plot_variable_frame = QFrame()
        self.plot_variable_frame.setObjectName("plotVariableFrame")
        self.plot_variable_frame.hide()
        plot_variable_layout = QHBoxLayout(self.plot_variable_frame)
        plot_variable_layout.setContentsMargins(0, 0, 0, 0)
        plot_variable_layout.setSpacing(5)

        plot_variable_label = QLabel("Select the variable to plot against the X-axis:")
        self.plot_variable_combobox = CustomComboBox()
        self.plot_variable_combobox.currentIndexChanged.connect(self.on_plot_variable_selected)

        plot_variable_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.plot_variable_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        plot_variable_layout.addWidget(plot_variable_label)
        plot_variable_layout.addWidget(self.plot_variable_combobox)

        left_layout.addWidget(self.plot_variable_frame, alignment=Qt.AlignTop)

        # Input Values Frame
        self.input_frame = QFrame()
        self.input_frame.setObjectName("inputFrame")
        self.input_frame.hide()
        input_layout = QVBoxLayout(self.input_frame)

        values_widget = QWidget()
        self.values_layout = QFormLayout()
        values_widget.setLayout(self.values_layout)
        input_layout.addWidget(values_widget)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 10, 0, 10)  # left, top, right, bottom

        create_plot_button = QPushButton("Generate Plot")
        create_plot_button.clicked.connect(self.run_pr_function)
        create_plot_button.setFixedWidth(150)
        button_layout.addWidget(create_plot_button)

        clear_all_button = QPushButton("Clear All")
        clear_all_button.clicked.connect(self.clear_all)
        clear_all_button.setFixedWidth(150)
        button_layout.addWidget(clear_all_button)

        input_layout.addLayout(button_layout)
        left_layout.addWidget(self.input_frame)

        # Wrap the left side in a widget
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMinimumWidth(400)
        left_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # --- Right side of the page ---
        right_layout = QVBoxLayout()

        # Fixed-size box for the plot
        self.plot_frame = QFrame()
        self.plot_frame.setObjectName("plotFrame")
        self.plot_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_layout = QVBoxLayout(self.plot_frame)
        self.plot_layout.setContentsMargins(0, 20, 0, 10) # left, top, right, bottom

        # Set plot title
        self.plot_title = QLabel()
        self.plot_title.setObjectName("plotTitle")
        self.plot_title.setWordWrap(True)
        self.plot_title.setAlignment(Qt.AlignCenter)
        self.plot_layout.addWidget(self.plot_title)
        self.plot_layout.addStretch(1)

        # Add Configure and Download Buttons
        self.plot_button_layout = QHBoxLayout()
        self.plot_button_layout.setAlignment(Qt.AlignCenter)
        self.plot_button_layout.setContentsMargins(0, 10, 0, 10) # left, top, right, bottom
        self.plot_button_layout.setSpacing(20)

        self.configure_plot_button = QPushButton("Configure")
        self.configure_plot_button.clicked.connect(self.configure_plot)
        self.configure_plot_button.setFixedWidth(100)
        self.plot_button_layout.addWidget(self.configure_plot_button)

        self.download_plot_button = QPushButton("Download")
        self.download_plot_button.clicked.connect(self.download_plot)
        self.download_plot_button.setFixedWidth(100)
        self.plot_button_layout.addWidget(self.download_plot_button)

        # Add the frames to the right layout
        right_layout.addWidget(self.plot_frame)
        right_layout.addLayout(self.plot_button_layout)
        right_layout.addStretch()

        # Wrap the right side in a widget
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the content to the scroll layout, then to the main layout
        scroll_layout.addWidget(left_widget, stretch=0)
        scroll_layout.addSpacing(50)
        scroll_layout.addWidget(right_widget, stretch=1)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # Apply the stylesheet
        with importlib.resources.open_text('pages.plotting', 'styles.qss') as f:
            style = f.read()
            self.setStyleSheet(style)

        # Connect to file manager signals
        self.file_manager.learnt_folders_updated.connect(self.load_result_folders_pr)
        self.file_manager.refresh()

        # Update the title after initializing all widgets
        self.update_plot_title()


    ############# RESIZE EVENT #############
    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_height = self.height() * 0.7  # Adjust the factor to set the height you want relative to the window
        self.plot_frame.setMinimumHeight(new_height)

    ############# PLOT TITLE ############# 
    def update_plot_title(self):
        """Update the title based on the selected values and input values."""
        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)
        data = self.pr_learnt_combobox.currentText()

        def format_value(value):
            if isinstance(value, dict):
                start = value.get('start', '')
                end = value.get('end', '')
                if start and end:
                    return f"{start}:{end}"
                elif start:
                    return f"{start}"
                else:
                    return ''
            else:
                return value or ''

        y_labels = ", ".join([f"{label}={format_value(y_values.get(label, '')) or 'y'}" for label in self.selected_y_values])
        x_labels = ", ".join([f"{label}={format_value(x_values.get(label, '')) or 'x'}" for label in self.selected_x_values])

        if y_labels and x_labels:
            title = f"P({y_labels} | {x_labels}, {data})"
        elif y_labels:
            title = f"P({y_labels} | {data})"
        elif x_labels:
            title = f"P(Y=y | {x_labels}, {data})"
        elif data:
            title = f"P(Y=y | X=x, {data})"
        else:
            title = "P(Y=y | X=x, data)"

        self.plot_title.setText(title)


    ############# LEARNT FOLDERS #############
    def load_result_folders_pr(self):
        """Load learnt folders into the PR learnt combobox from the FileManager."""
        self.pr_learnt_combobox.clear()

        self.pr_learnt_combobox.currentIndexChanged.disconnect(self.on_learnt_folder_selected) # Disconnect the signal

        if self.file_manager.learnt_folders:
            self.pr_learnt_combobox.addItems(self.file_manager.learnt_folders)
            self.pr_learnt_combobox.setCurrentIndex(-1)
        else:
            self.pr_learnt_combobox.addItem("No learnt folders available")
            self.pr_learnt_combobox.setItemData(1, Qt.NoItemFlags)

        self.pr_learnt_combobox.currentIndexChanged.connect(self.on_learnt_folder_selected) # Reconnect the signal

    def on_learnt_folder_selected(self, index):
        """Update the data value when a learnt folder is selected."""
        if index >= 0:
            self.data = self.pr_learnt_combobox.currentText()
            self.load_metadata_pr()
            self.variable_selection_frame.show()

            self.Y_listwidget.clearSelection()
            self.X_listwidget.clearSelection()

            self.selected_y_values = []
            self.selected_x_values = []

            self.clear_input_layout()
        else:
            self.data = "data"
        self.update_plot_title()

    ############# VARIABLE SELECTION #############
    def load_metadata_pr(self):
        """Load variates from the metadata.csv file in the selected learnt folder."""
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
            self.Y_listwidget.addItems(variates)
            self.X_listwidget.addItems(variates)

            self.adjust_list_widget_height(self.Y_listwidget)
            self.adjust_list_widget_height(self.X_listwidget)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load metadata: {str(e)}")

    def adjust_list_widget_height(self, list_widget, max_visible_items=20):
        num_items = list_widget.count()
        visible_items = min(num_items, max_visible_items)
        row_height = list_widget.sizeHintForRow(0) if list_widget.count() > 0 else 20
        total_height = row_height * visible_items + 2 * list_widget.frameWidth()
        list_widget.setFixedHeight(total_height)

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

    def on_Y_variable_selected(self):
        """Update the selected Y variables and input fields based on the selected items."""
        selected_items = self.Y_listwidget.selectedItems()
        new_selected_y_values = [item.text() for item in selected_items]

        added_variables = list(set(new_selected_y_values) - set(self.selected_y_values))
        removed_variables = list(set(self.selected_y_values) - set(new_selected_y_values))

        self.selected_y_values = new_selected_y_values

        self.update_selected_variables(added_variables, removed_variables)

    def on_X_variable_selected(self):
        """Update the selected X variables and input fields based on the selected items."""
        selected_items = self.X_listwidget.selectedItems()
        new_selected_x_values = [item.text() for item in selected_items]

        added_variables = list(set(new_selected_x_values) - set(self.selected_x_values))
        removed_variables = list(set(self.selected_x_values) - set(new_selected_x_values))

        self.selected_x_values = new_selected_x_values

        self.update_selected_variables(added_variables, removed_variables)

    def update_selected_variables(self, added_variables, removed_variables):
        """Update the selected variables and input fields based on the added and removed variables."""
        self.clear_input_layout()

        self.plot_variable_combobox.blockSignals(True)  # Block signals temporarily

        for value in added_variables:
            if value not in self.metadata_dict:
                self.metadata_dict[value] = self.get_metadata_for_selected_value(value)
                var_type = self.metadata_dict[value].get("type")
                if var_type == "continuous" or (var_type == "ordinal" and "options" not in self.metadata_dict[value]):
                    self.plot_variable_combobox.addItem(value)
                
        for value in removed_variables:
            if value in self.metadata_dict:
                del self.metadata_dict[value]
                self.plot_variable_combobox.removeItem(self.plot_variable_combobox.findText(value))

        self.plot_variable_combobox.setCurrentIndex(-1)
        self.plot_variable_combobox.blockSignals(False)  # Unblock signals after updating

        self.update_disabled_items()
        self.update_X_list_visibility()
        self.update_plot_title()
        self.clear_plot()

    def update_disabled_items(self):
        """Disable selected items in the opposite list to prevent cross-selection."""
        # Disable Y-selected items in the X list
        for i in range(self.X_listwidget.count()):
            item = self.X_listwidget.item(i)
            item.setFlags(item.flags() | Qt.ItemIsEnabled)
            if item.text() in self.selected_y_values:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

        # Disable X-selected items in the Y list
        for i in range(self.Y_listwidget.count()):
            item = self.Y_listwidget.item(i)
            item.setFlags(item.flags() | Qt.ItemIsEnabled)
            if item.text() in self.selected_x_values:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

    def update_X_list_visibility(self):
        """Show or hide the input frame based on the selected Y and X values."""
        if self.Y_listwidget.selectedItems():
            self.X_label_widget.show()
            self.X_listwidget.show()
            self.plot_variable_frame.show()
        else:
            self.X_label_widget.hide()
            self.X_listwidget.clearSelection()
            self.selected_x_values = []
            self.X_listwidget.hide()
            self.plot_variable_frame.hide()
            self.clear_input_layout()

    def on_plot_variable_selected(self, index):
        """Update the the values layout based on the selected plot variable."""
        self.clear_input_layout()
        if index >= 0:
            selected_variable = self.plot_variable_combobox.currentText()
            if selected_variable in self.selected_x_values:
                self.update_values_layout_tailpr()
            else:
                self.update_values_layout_pr()
                self.input_frame.show()

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

    ############# INPUT VALUES #############
    def update_values_layout_pr(self):
        """Update the values layout based on the selected variables."""
        variables = self.selected_y_values + self.selected_x_values

        longest_variable = max(variables, key=len, default="")
        font_metrics = self.fontMetrics()
        label_width = font_metrics.horizontalAdvance(f"{longest_variable} = ")

        plot_variable = self.plot_variable_combobox.currentText()

        for variable in variables:
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(f"{variable} = ")
            label.setAlignment(Qt.AlignRight)
            label.setFixedWidth(label_width)

            var_type = self.metadata_dict.get(variable, {}).get("type")

            if var_type == "nominal" or (var_type == "ordinal" and "options" in self.metadata_dict[variable]):
                options = self.metadata_dict[variable].get("options", [])
                input_box = QComboBox()
                input_box.addItems(options)
                if variable in self.variable_values:
                    input_box.setCurrentText(self.variable_values[variable])
                input_box.currentIndexChanged.connect(self.value_changed)

                row_layout.addWidget(label)
                row_layout.addWidget(input_box)
                self.values_layout.addRow(row_layout)
                self.input_fields[variable] = (label, input_box)

            elif var_type == "continuous" or (var_type == "ordinal" and "options" not in self.metadata_dict[variable]):
                ranged_layout = QHBoxLayout()
                ranged_layout.setAlignment(Qt.AlignLeft)

                start_label = QLabel("From ")
                start_input = QLineEdit()
                start_input.setFixedSize(70, 30)
                start_input.setPlaceholderText("Enter value")
                start_input.textChanged.connect(self.value_changed)
                start_input.setAlignment(Qt.AlignCenter)

                end_label = QLabel(" To ")
                end_input = QLineEdit()
                end_input.setFixedSize(70, 30)

                if variable == plot_variable:
                    end_input.setPlaceholderText("Enter value")
                else:
                    end_input.setPlaceholderText("(optional)")
                end_input.textChanged.connect(self.value_changed)
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

                row_layout.addWidget(label)
                row_layout.addLayout(ranged_layout)
                self.values_layout.addRow(row_layout)
                self.input_fields[variable] = (label, {'start': start_input, 'end': end_input, 'start_label': start_label, 'end_label': end_label})

            else:
                QMessageBox.warning(None, "Invalid Type", f"Invalid variable type for {variable}: {var_type}")

            self.add_custom_spacing(self.values_layout, 3)
    
    def update_values_layout_tailpr(self):
        """Update the values layout based on the selected variables."""
        QMessageBox.warning(None, "TODO", "Logic for plotting variables from the X-list is not implemented yet.")
        self.clear_input_layout()

    def add_custom_spacing(self, layout, height):
        """ Adds custom vertical spacing to a QFormLayout using a transparent QWidget with fixed height. """
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(height)
        spacer_widget.setStyleSheet("background-color: transparent;")
        layout.addRow(spacer_widget)

    def value_changed(self):
        """Update the stored variable values when the input value changes."""
        self.get_input_value(self.selected_y_values + self.selected_x_values)
        self.clear_plot()
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
                else:
                    if isinstance(widget, QComboBox):
                        input_values[variable] = widget.currentText()
                    else:
                        QMessageBox.warning(None, "Invalid Input", f"Invalid input field for {variable}")
        self.variable_values.update(input_values)
        return input_values

    ############# RUN PROBABILITY FUNCTION #############
    def run_pr_function(self):
        """ Run the Pr function and plot the probabilities."""
        if not self.all_values_filled():
            QMessageBox.warning(self, "Incomplete Input", "Please fill out all value-fields for the selected variables.")
            return
        
        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)

        Y_dict = self.parse_and_validate_input_values(y_values)
        if Y_dict is None:
            return
        X_dict = self.parse_and_validate_input_values(x_values)
        if X_dict is None:
            return
    
        self.Y = pd.DataFrame(Y_dict)
        self.X = pd.DataFrame(X_dict)
        
        learnt_dir = os.path.join(LEARNT_FOLDER, self.pr_learnt_combobox.currentText())

        try:
            if self.should_plot():
                self.probabilities_values, self.probabilities_quantiles = run_Pr(self.Y, learnt_dir, self.X)
                self.plot_probabilities()
            else:
                QMessageBox.warning(None, "No Plot", "No plot generated. No numeric variable with multiple values to plot.")
        
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to run the Pr function: {str(e)}")

    def parse_input_value(self, value):
        """Parse the input value string for non-nominal types, supporting range (a:b) input."""
        if isinstance(value, dict) and 'start' in value:
            start_str = value['start']
            end_str = value['end']
            try:
                start_val = float(start_str)
                if not end_str:
                    return [start_val]
                else:
                    end_val = float(end_str)
                    num_points = int(abs(end_val - start_val)) + 1
                    if start_val.is_integer() and end_val.is_integer():
                        value_list = list(range(int(start_val), int(end_val) + 1))
                    else:
                        value_list = np.linspace(start_val, end_val, num=num_points).tolist()
                    return value_list
            except ValueError:
                QMessageBox.warning(None, "Invalid Input", f"Invalid numeric input: {start_str} or {end_str}")
                return []
        else:
            value_string = value
            if isinstance(value_string, str):
                return [value_string]
            else:
                return value_string
    
    def all_values_filled(self):
        """Check if all selected Y and X variables have been assigned values."""
        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)
        plot_variable = self.plot_variable_combobox.currentText()

        for variable in self.selected_y_values + self.selected_x_values:
            value = y_values.get(variable) or x_values.get(variable)
            if value is None:
                return False
            if isinstance(value, dict):
                start = value.get('start', '').strip()
                end = value.get('end', '').strip()
                if not start:
                    return False
                if variable == plot_variable and not end:
                    return False
            else:
                if not value:
                    return False
        return True
    
    def parse_and_validate_input_values(self, values):
        """Parse and validate input values."""
        parsed_values = {}
        for var_name, value in values.items():

            if isinstance(value, dict) and 'start' in value:
                start_str = value['start']
                end_str = value['end']
                try:
                    start_val = float(start_str)
                except ValueError:
                    QMessageBox.warning(None, "Invalid Input", f"Invalid numeric input for start value in {var_name}: {start_str}")
                    return None
                
                if not end_str:
                    variable_value = [start_val]
                else:
                    try:
                        end_val = float(end_str)
                    except ValueError:
                        QMessageBox.warning(None, "Invalid Input", f"Invalid numeric input for end value in {var_name}: {end_str}")
                        return None
                    
                    if end_val < start_val:
                        QMessageBox.warning(None, "Invalid Input", f"End value must be greater than start value for {var_name}")
                        return
                    
                    num_points = int(abs(end_val - start_val)) + 1
                    if start_val.is_integer() and end_val.is_integer():
                        variable_value = list(range(int(start_val), int(end_val) + 1))
                    else:
                        variable_value = np.linspace(start_val, end_val, num=num_points).tolist()
            else:
                value_string = value
                if isinstance(value_string, str):
                    variable_value = [value_string]
                else:
                    variable_value = value_string

            parsed_values[var_name] = variable_value
        return parsed_values

    ############# PLOTTING #############
    def should_plot(self):
        """Check if the plot should be generated based on the input data."""
        # Check if any column in Y has multiple values and is numeric
        for column in self.Y.columns:
            if len(self.Y[column].unique()) > 1 and pd.api.types.is_numeric_dtype(self.Y[column]):
                return True
        
        # Check if any column in X has multiple values and is numeric
        for column in self.X.columns:
            if len(self.X[column].unique()) > 1 and pd.api.types.is_numeric_dtype(self.X[column]):
                return True
        
        return False

    def plot_probabilities(self):
        """Plot the probabilities and uncertainty."""
        self.load_configuration()
        self.clear_plot()

        # Create a Figure and FigureCanvas
        figure = Figure()
        ax = figure.add_subplot(111)
        self.plot_canvas = FigureCanvas(figure)
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_layout.insertWidget(1, self.plot_canvas)

        # Convert to numpy arrays
        probabilities_values = np.array(self.probabilities_values).flatten()
        probabilities_quantiles = np.array(self.probabilities_quantiles)

        # Ensure quantiles array is correctly shaped for plotting
        if probabilities_quantiles.ndim == 3:
            lower_quantiles = probabilities_quantiles[:, 0, 0]
            upper_quantiles = probabilities_quantiles[:, 0, -1]
        elif probabilities_quantiles.ndim == 2 and probabilities_quantiles.shape[1] >= 2:
            lower_quantiles = probabilities_quantiles[:, 0]
            upper_quantiles = probabilities_quantiles[:, -1]
        else:
            lower_quantiles = np.zeros(self.Y.shape[0])
            upper_quantiles = np.zeros(self.Y.shape[0])

        # Plot the quantiles
        y_column = self.Y.columns[0]

        ax.fill_between(
            self.Y[y_column], 
            lower_quantiles, 
            upper_quantiles,
            color=self.color_uncertainty_area, 
            alpha=self.alpha_uncertainty_area, 
            edgecolor='darkblue', 
            linewidth=self.width_uncertainty_area,
            label='Uncertainty'
        )

        ax.set_ylim(0, None)
        ax.set_xlabel(y_column)
        ax.set_ylabel('Probability')

        # Overlay the probability distribution curve
        spl = make_interp_spline(self.Y[y_column], probabilities_values, k=3)
        Y_smooth = np.linspace(self.Y[y_column].min(), self.Y[y_column].max(), 500)
        prob_smooth = spl(Y_smooth)

        ax.plot(Y_smooth, prob_smooth, color=self.color_probability_curve, linewidth=self.width_probability_curve, linestyle='-', label='Probability')

        # Add the 0-change line
        ax.axvline(x=0, color=self.color_zero_change_line, linestyle='--', linewidth=self.width_zero_change_line, label='0-change Line')

        # Add legend to explain the components of the plot
        ax.legend()

        # Draw the canvas
        self.plot_canvas.draw()
        self.plot = True

    def load_configuration(self):
        """Load configuration from JSON file"""
        if os.path.exists(USER_CONFIG_PATH):
            with open(USER_CONFIG_PATH, 'r') as f:
                config = json.load(f)
                self.color_probability_curve = config.get('plot_colors').get('probability_curve')
                self.color_uncertainty_area = config.get('plot_colors').get('uncertainty_area')
                self.color_zero_change_line = config.get('plot_colors').get('zero_change_line')
                self.width_probability_curve = config.get('line_widths').get('probability_curve')
                self.width_zero_change_line = config.get('line_widths').get('zero_change_line')
                self.width_uncertainty_area = config.get('line_widths').get('uncertainty_area')
                self.alpha_uncertainty_area = config.get('alpha_values').get('uncertainty_area')
                self.xlabel = config.get('x_label')
                self.ylabel = config.get('y_label')
        else:
            # Default values
            self.color_probability_curve = 'blue'
            self.color_uncertainty_area = 'lightblue'
            self.color_zero_change_line = 'red'
            self.width_probability_curve = 2
            self.width_zero_change_line = 2
            self.width_uncertainty_area = 2
            self.alpha_uncertainty_area = 0.3
            self.xlabel = 'X-axis Label'
            self.ylabel = 'Y-axis Label'

    def configure_plot(self):
        """Open a dialog to configure plot settings."""
        self.load_configuration()

        dialog = QDialog(self)
        dialog.setMinimumWidth(300)
        dialog.setWindowTitle("Configure Plot Settings")

        layout = QFormLayout()

        self.color_probability_curve_edit = QLineEdit(self.color_probability_curve)
        self.color_uncertainty_area_edit = QLineEdit(self.color_uncertainty_area)
        self.color_zero_change_line_edit = QLineEdit(self.color_zero_change_line)
        self.width_probability_curve_edit = QLineEdit(str(self.width_probability_curve))
        self.width_zero_change_line_edit = QLineEdit(str(self.width_zero_change_line))
        self.width_uncertainty_area_edit = QLineEdit(str(self.width_uncertainty_area))
        self.alpha_uncertainty_area_edit = QLineEdit(str(self.alpha_uncertainty_area))
        self.xlabel_edit = QLineEdit(self.xlabel)
        self.ylabel_edit = QLineEdit(self.ylabel)

        layout.addRow("Probability Curve Color:", self.color_probability_curve_edit)
        layout.addRow("Uncertainty Area Color:", self.color_uncertainty_area_edit)
        layout.addRow("Zero Change Line Color:", self.color_zero_change_line_edit)
        layout.addRow("Probability Curve Width:", self.width_probability_curve_edit)
        layout.addRow("Zero Change Line Width:", self.width_zero_change_line_edit)
        layout.addRow("Uncertainty Area Width:", self.width_uncertainty_area_edit)
        layout.addRow("Uncertainty Area Alpha:", self.alpha_uncertainty_area_edit)
        layout.addRow("X-axis Label:", self.xlabel_edit)
        layout.addRow("Y-axis Label:", self.ylabel_edit)

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_configuration(dialog))

        layout.addWidget(save_button)
        dialog.setLayout(layout)
        dialog.exec_()

        if self.plot:
            self.plot_probabilities()

    def save_configuration(self, dialog):
        self.color_probability_curve = self.color_probability_curve_edit.text()
        self.color_uncertainty_area = self.color_uncertainty_area_edit.text()
        self.color_zero_change_line = self.color_zero_change_line_edit.text()
        self.width_probability_curve = int(self.width_probability_curve_edit.text())
        self.width_zero_change_line = int(self.width_zero_change_line_edit.text())
        self.width_uncertainty_area = int(self.width_uncertainty_area_edit.text())
        self.alpha_uncertainty_area = float(self.alpha_uncertainty_area_edit.text())
        self.xlabel = self.xlabel_edit.text()
        self.ylabel = self.ylabel_edit.text()

        config = {
            "plot_colors": {
                "probability_curve": self.color_probability_curve,
                "uncertainty_area": self.color_uncertainty_area,
                "zero_change_line": self.color_zero_change_line
            },
            "line_widths": {
                "probability_curve": self.width_probability_curve,
                "zero_change_line": self.width_zero_change_line,
                "uncertainty_area": self.width_uncertainty_area
            },
            "alpha_values": {
                "uncertainty_area": self.alpha_uncertainty_area
            },
            "x_label": self.xlabel,
            "y_label": self.ylabel
        }
        with open(USER_CONFIG_PATH, 'w') as f:
            json.dump(config, f)
        dialog.accept()

    def download_plot(self):
        if self.plot_canvas is None:
            QMessageBox.warning(self, "No Plot", "There is no plot to save.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Plot As",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf);;All Files (*)",
            options=options
        )

        if file_path:
            try:
                self.plot_canvas.figure.savefig(file_path)
                QMessageBox.information(self, "Success", f"Plot saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save plot: {str(e)}")

    def clear_plot(self):
        """Clear the plot from the canvas."""
        if self.plot:
            self.plot_layout.removeWidget(self.plot_canvas)
            self.plot_canvas.deleteLater()
            self.plot_canvas = None
            self.plot = False

    ############# CLEAR ALL #############
    def clear_all(self):
        """Clears all selections and resets the interface."""

        self.pr_learnt_combobox.setCurrentIndex(-1)

        self.Y_listwidget.clear()
        self.X_listwidget.clear()

        self.variable_selection_frame.hide()

        self.Y_listwidget.clearSelection()
        self.X_listwidget.clearSelection()

        self.selected_y_values = []
        self.selected_x_values = []

        self.plot_variable_frame.hide()
        self.plot_variable_combobox.clear()

        self.clear_input_layout()
        self.update_plot_title()
        self.clear_plot()
