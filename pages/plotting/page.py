import os
import json
import numpy as np
import pandas as pd
import importlib.resources
from itertools import product
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QHBoxLayout, 
                                QComboBox, QListWidget, QFileDialog, QAbstractItemView, QFormLayout, QLineEdit, 
                                QMessageBox, QSizePolicy, QAbstractItemView, QDialog, QSpacerItem, QCheckBox)
from PySide6.QtCore import Qt
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
        self.plot_canvas = None
        self.selected_y_values = []
        self.selected_x_values = []
        self.metadata_df = pd.DataFrame()
        self.metadata_dict = {}
        self.variable_values = {}
        self.input_fields = {}
        self.current_list_widget = None
        self.config = {}
        self.probabilities_values = None
        self.probabilities_quantiles = None
        self.reset_configuration()
        self.write_configuration()

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

        # Should a categorical X-variable be plotted multiple times?
        self.categorical_variable_frame = QFrame()
        self.categorical_variable_frame.setObjectName("categoricalVariableFrame")
        self.categorical_variable_frame.hide()
        categorical_variable_layout = QHBoxLayout(self.categorical_variable_frame)
        categorical_variable_layout.setContentsMargins(0, 0, 0, 0)
        categorical_variable_layout.setSpacing(5)

        categorical_variable_label = QLabel("Plot a categorical X-variable with multiple values?")
        self.categorical_variable_combobox = CustomComboBox()
        self.categorical_variable_combobox.currentIndexChanged.connect(self.on_categorical_variable_selected)

        categorical_variable_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.categorical_variable_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        categorical_variable_layout.addWidget(categorical_variable_label)
        categorical_variable_layout.addWidget(self.categorical_variable_combobox)

        left_layout.addWidget(self.categorical_variable_frame, alignment=Qt.AlignTop)
        left_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # Input Values Frame
        self.input_frame = QFrame()
        self.input_frame.setObjectName("inputFrame")
        self.input_frame.hide()
        input_layout = QVBoxLayout(self.input_frame)

        input_label = QLabel("Provide values for the selected variables:")
        input_label.setObjectName("inputLabel")
        input_layout.addWidget(input_label)

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
        clear_all_button.setObjectName("clearButton")
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
        self.configure_plot_button.clicked.connect(self.on_configure_button_clicked)
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
        new_height = self.height() * 0.7
        self.plot_frame.setMinimumHeight(new_height)

    ############# PLOT TITLE ############# 
    def update_plot_title(self):
        """Update the title based on the selected values and input values."""
        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)
        data = self.pr_learnt_combobox.currentText()

        y_labels = ", ".join([f"{label}={self.format_value(y_values.get(label, '')) or 'y'}" for label in self.selected_y_values])
        x_labels = ", ".join([f"{label}={self.format_value(x_values.get(label, '')) or 'x'}" for label in self.selected_x_values])

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

    def format_value(self, value):
        if isinstance(value, dict):
            start = value.get('start', '')
            end = value.get('end', '')
            if start and end:
                return f"{start}:{end}"
            elif start:
                return f"{start}"
            else:
                return ''
        elif isinstance(value, list):
            return f"[{', '.join(value)}]"
        else:
            return value or ''

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

        if self.plot_variable_combobox.currentIndex() < 0:
            self.categorical_variable_combobox.clear()
            self.categorical_variable_frame.hide()
            self.clear_input_layout()

        self.update_disabled_items()
        self.update_X_list_visibility()
        self.update_plot_title()
        self.clear_plot()

    def update_categorical_variable_combobox(self):
        """Update the categorical variable combobox based on selected X variables."""
        if self.plot_variable_combobox.currentIndex() < 0:
            self.categorical_variable_combobox.clear()
            self.categorical_variable_frame.hide()
            return 
        
        categorical_variables = []

        for variable in self.selected_x_values:
            var_metadata = self.metadata_dict.get(variable, {})
            var_type = var_metadata.get("type")
            if var_type == "nominal" or (var_type == "ordinal" and "options" in var_metadata):
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
        self.disable_item(self.Y_listwidget, self.selected_x_values)
        self.disable_item(self.X_listwidget, self.selected_y_values)

    def disable_item(self, listwidget, selected_values):
        for i in range(listwidget.count()):
            item = listwidget.item(i)
            item.setFlags(item.flags() | Qt.ItemIsEnabled)
            if item.text() in selected_values:
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
            self.update_categorical_variable_combobox()
        else:
            self.input_frame.hide()
            self.categorical_variable_combobox.clear()
            self.categorical_variable_frame.hide()

    def on_categorical_variable_selected(self, index):
        """Update the values layout based on the selected categorical variable."""
        self.clear_list_widget()
        self.clear_input_layout()
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
        self.clear_list_widget()
        variables = self.selected_y_values + self.selected_x_values

        longest_variable = max(variables, key=len, default="")
        font_metrics = self.fontMetrics()
        label_width = font_metrics.horizontalAdvance(f"{longest_variable} = ")

        plot_variable = self.plot_variable_combobox.currentText()
        categorical_variable = self.categorical_variable_combobox.currentText()
        if categorical_variable == "No":
            categorical_variable = None

        for variable in variables:
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(f"{variable} = ")
            label.setAlignment(Qt.AlignRight)
            label.setFixedWidth(label_width)

            var_type = self.metadata_dict.get(variable, {}).get("type")

            if variable == categorical_variable:
                options = self.metadata_dict[variable].get("options", [])
                list_widget = QListWidget()
                list_widget.itemSelectionChanged.connect(lambda: self.limit_selection(list_widget, 2))
                list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
                list_widget.addItems(options)
                if variable in self.variable_values:
                    selected_options = self.variable_values[variable]
                    for i in range(list_widget.count()):
                        item = list_widget.item(i)
                        if item.text() in selected_options:
                            item.setSelected(True)
                list_widget.itemSelectionChanged.connect(self.value_changed)
                self.adjust_list_widget_height(list_widget)
                list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                list_widget.setObjectName("listWidget")

                row_layout.addWidget(label)
                row_layout.addWidget(list_widget)
                self.values_layout.addRow(row_layout)

                self.input_fields[variable] = (label, list_widget)
                self.current_list_widget = list_widget

            elif var_type == "nominal" or (var_type == "ordinal" and "options" in self.metadata_dict[variable]):
                options = self.metadata_dict[variable].get("options", [])
                input_box = CustomComboBox()
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
                start_input.setObjectName("inputField")
                start_input.setFixedSize(70, 30)
                start_input.setPlaceholderText("Enter value")
                start_input.textChanged.connect(self.value_changed)
                start_input.setAlignment(Qt.AlignCenter)

                end_label = QLabel(" To ")
                end_input = QLineEdit()
                end_input.setObjectName("inputField")
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
                QMessageBox.warning(None, "Error", f"Invalid variable type for {variable}: {var_type}")

            self.add_custom_spacing(self.values_layout, 3)

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
                elif isinstance(widget, QListWidget):
                    selected_items = widget.selectedItems()
                    values = [item.text() for item in selected_items]
                    input_values[variable] = values
                else:
                    if isinstance(widget, CustomComboBox):
                        input_values[variable] = widget.currentText()
                    else:
                        QMessageBox.warning(None, "Error", f"Invalid input field for {variable}")
        self.variable_values.update(input_values)
        return input_values

    ############# RUN PROBABILITY FUNCTION #############
    def run_pr_function(self):
        """ Run the Pr function and plot the probabilities."""
        if not self.all_values_filled():
            QMessageBox.warning(self, "Error", "Please fill out all value-fields for the selected variables.")
            return

        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)

        Y_df  = self.parse_and_validate_input_values(y_values)
        if Y_df is None:
            return
        X_df = self.parse_and_validate_input_values(x_values)
        if X_df is None:
            return
    
        self.Y = Y_df 
        self.X = X_df
        
        learnt_dir = os.path.join(LEARNT_FOLDER, self.pr_learnt_combobox.currentText())

        if self.should_plot():
            try:
                self.probabilities_values, self.probabilities_quantiles = run_Pr(self.Y, learnt_dir, self.X)
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to run the Pr function: {str(e)}")
                return

            try:
                self.reset_configuration()
                self.update_configuration()
                self.write_configuration()
                self.plot_probabilities()
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to plot probabilities: {str(e)}")
        else:
            QMessageBox.warning(None, "Error", "No plot generated. No numeric variable with multiple values to plot.")
    
    def all_values_filled(self):
        """Check if all selected Y and X variables have been assigned values."""
        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)
        plot_variable = self.plot_variable_combobox.currentText()
        categorical_variable = self.categorical_variable_combobox.currentText()
        if categorical_variable == "No":
            categorical_variable = None

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
            elif isinstance(value, list):
                if not value and variable == categorical_variable:
                    return False
            else:
                if not value:
                    return False
        return True
    
    def parse_and_validate_input_values(self, values):
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
                    variable_value = list(range(int(start_val), int(end_val) + 1)) if start_val.is_integer() and end_val.is_integer() else np.linspace(start_val, end_val, num=num_points).tolist()
            elif isinstance(value, list):
                if not value:
                    QMessageBox.warning(None, "Error", f"No values selected for {var_name}")
                    return None
                variable_value = value
            else:
                variable_value = [value]

            parsed_values[var_name] = variable_value
            if len(variable_value) > max_length:
                max_length = len(variable_value)

        for var_name, variable_value in parsed_values.items():
            if len(variable_value) < max_length:
                repeats = max_length // len(variable_value) + (max_length % len(variable_value) > 0)
                parsed_values[var_name] = (variable_value * repeats)[:max_length]

        df = pd.DataFrame(parsed_values)
        return df


    ############# PLOTTING #############
    def should_plot(self):
        """Check if the plot should be generated based on the input data."""
        for df in [self.Y, self.X]:
            for column in df.columns:
                if len(df[column].unique()) > 1 and pd.api.types.is_numeric_dtype(df[column]):
                    return True
        
        categorical_variable = self.categorical_variable_combobox.currentText()
        if categorical_variable != "No" and categorical_variable in self.X.columns:
            if len(self.X[categorical_variable].unique()) > 1:
                return True
            
        for column in self.Y.columns:
            if len(self.Y[column].unique()) > 1 and pd.api.types.is_numeric_dtype(self.Y[column]):
                return True
            
        for column in self.X.columns:
            if len(self.X[column].unique()) > 1 and pd.api.types.is_numeric_dtype(self.X[column]):
                return True

        return False

    def plot_probabilities(self):
        """Plot the probabilities and uncertainty for multiple variables."""
        self.clear_plot()

        figure = Figure()
        ax = figure.add_subplot(111)
        self.plot_canvas = FigureCanvas(figure)
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_layout.insertWidget(1, self.plot_canvas)
        
        probabilities_values = np.array(self.probabilities_values)
        probabilities_quantiles = np.array(self.probabilities_quantiles)

        num_variables = probabilities_values.shape[1]

        plot_variable = self.plot_variable_combobox.currentText()
        if plot_variable in self.Y.columns:
            x_values = self.Y[plot_variable]
        elif plot_variable in self.X.columns:
            x_values = self.X[plot_variable]
        else:
            QMessageBox.warning(None, "Error", f"The selected plot variable '{plot_variable}' was not found in Y or X.")
            return

        for i in range(num_variables):
            plot_key = f"plot_{i+1}"

            if probabilities_quantiles.ndim == 3:
                lower_quantiles = probabilities_quantiles[:, i, 0]
                upper_quantiles = probabilities_quantiles[:, i, -1]
            elif probabilities_quantiles.ndim == 2 and probabilities_quantiles.shape[1] >= 2:
                lower_quantiles = probabilities_quantiles[:, 0]
                upper_quantiles = probabilities_quantiles[:, -1]
            else:
                lower_quantiles = np.zeros(len(x_values))
                upper_quantiles = np.zeros(len(x_values))

            ax.fill_between(
                x_values, 
                lower_quantiles, 
                upper_quantiles,
                color=self.config[plot_key]['color_uncertainty_area'], 
                alpha=self.config['shared']['alpha_uncertainty_area'], 
                edgecolor=self.config[plot_key]['color_probability_curve'], 
                linewidth=self.config['shared']['width_uncertainty_area'],
                label=self.config[plot_key]['uncertantity_label']
            )

            try:
                spl = make_interp_spline(x_values, probabilities_values[:, i], k=3)
                x_smooth = np.linspace(x_values.min(), x_values.max(), 500)
                prob_smooth = spl(x_smooth)
            except ValueError:
                x_smooth = x_values
                prob_smooth = probabilities_values[:, i]

            ax.plot(
                x_smooth, 
                prob_smooth, 
                color=self.config[plot_key]['color_probability_curve'], 
                linewidth=self.config['shared']['width_probability_curve'], 
                linestyle='-', 
                label=self.config[plot_key]['probability_label']
            )
        if self.config['shared'].get('draw_x_change_line', True):
            ax.axvline(
                x=self.config['shared']['x_line_value'], 
                color=self.config['shared']['color_x_change_line'], 
                linestyle='--', linewidth=self.config['shared']['width_x_change_line'], 
                label=self.config['shared']['x_line_label']
            )
        ax.set_xlabel(self.config['shared']['x_label'])
        ax.set_ylabel(self.config['shared']['y_label'])
        ax.legend()

        self.plot_canvas.draw()

    def on_configure_button_clicked(self):
        """Open the configuration dialog to change plot settings."""
        self.load_configuration()
        self.configure_plot()
        if self.probabilities_values is not None and self.probabilities_quantiles is not None:
            self.plot_probabilities()
    
    def load_configuration(self):
        """Load configuration from JSON file"""
        with open(USER_CONFIG_PATH, 'r') as f:
            self.config = json.load(f)

    def write_configuration(self):
        """Write configuration to JSON file"""
        with open(USER_CONFIG_PATH, 'w') as f:
            json.dump(self.config, f)

    def reset_configuration(self):
        """Reset the configuration to default values."""
        with importlib.resources.open_text('pages.plotting', 'default_config.json') as f:
            self.config = json.load(f)

    def update_configuration(self):
        """Update the configuration (x_label and probability labels) dynamically based on current selections and data."""
        plot_variable = self.plot_variable_combobox.currentText()
        categorical_variable = self.categorical_variable_combobox.currentText()
        if categorical_variable == "No":
            categorical_variable = None

        self.config['shared']['x_label'] = plot_variable

        num_variables = self.probabilities_values.shape[1]

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
        if categorical_variable and categorical_variable in self.variable_values:
            categorical_values = self.variable_values[categorical_variable]
            for cat_val in categorical_values:
                line_label_parts = list(other_values) + [cat_val]
                line_labels.append(", ".join(line_label_parts))
        else:
            if num_variables > 1:
                if plot_variable in self.Y.columns:
                    x_line_values = self.Y[plot_variable].unique()
                elif plot_variable in self.X.columns:
                    x_line_values = self.X[plot_variable].unique()
                else:
                    x_line_values = ["Line " + str(i+1) for i in range(num_variables)]

                x_line_values = list(map(str, x_line_values))
                for val in x_line_values:
                    line_label_parts = list(other_values) + [val]
                    line_labels.append(", ".join(line_label_parts))
            else:
                label = ", ".join(other_values) if other_values else "Line 1"
                line_labels.append(label)

        for i, label in enumerate(line_labels, start=1):
            plot_key = f"plot_{i}"
            if plot_key in self.config:
                self.config[plot_key]['probability_label'] = label

    def configure_plot(self):
        """Open a dialog to configure plot settings."""
        dialog = QDialog(self)
        dialog.setMinimumWidth(300)
        dialog.setWindowTitle("Configure Plot Settings")

        layout = QFormLayout()

        # Predefined color options
        color_options = ["blue", "green", "red", "black", "yellow", "cyan", "magenta"]
        lighter_color_options = ["lightblue", "lightgreen", "lightsalmon", "lightgray", "lightyellow", "lightcyan", "lightpink"]

        # Shared Fields
        self.width_probability_curve_edit = QLineEdit(str(self.config['shared']['width_probability_curve']))
        self.width_uncertainty_area_edit = QLineEdit(str(self.config['shared']['width_uncertainty_area']))
        self.alpha_uncertainty_area_edit = QLineEdit(str(self.config['shared']['alpha_uncertainty_area']))
        self.xlabel_edit = QLineEdit(str(self.config['shared']['x_label']))
        self.ylabel_edit = QLineEdit(str(self.config['shared']['y_label']))

        self.draw_x_change_line_checkbox = QCheckBox()
        self.draw_x_change_line_checkbox.setChecked(self.config['shared'].get('draw_x_change_line', True))
        self.x_line_value_edit = QLineEdit(str(self.config['shared']['x_line_value']))

        # ComboBox for color_x_change_line
        self.color_x_change_line_combo = QComboBox()
        self.color_x_change_line_combo.addItems(color_options)
        current_x_line_color = self.config['shared']['color_x_change_line']
        if current_x_line_color not in color_options:
            self.color_x_change_line_combo.addItem(current_x_line_color)
        self.color_x_change_line_combo.setCurrentText(current_x_line_color)

        self.width_x_change_line_edit = QLineEdit(str(self.config['shared']['width_x_change_line']))
        self.x_line_label_edit = QLineEdit(str(self.config['shared']['x_line_label']))

        general_label = QLabel("General")
        general_label.setObjectName("sectionLabel")
        layout.addRow(general_label, QLabel())
        layout.addRow("Uncertainty Area Alpha:", self.alpha_uncertainty_area_edit)
        layout.addRow("Uncertainty Area Width:", self.width_uncertainty_area_edit)
        layout.addRow("Probability Curve Width:", self.width_probability_curve_edit)
        layout.addRow("X-label:", self.xlabel_edit)
        layout.addRow("Y-label:", self.ylabel_edit)
        layout.addRow("", QLabel())

        change_line_label = QLabel("X-change Line")
        change_line_label.setObjectName("sectionLabel")
        layout.addRow(change_line_label, QLabel())
        layout.addRow("Draw X-change Line:", self.draw_x_change_line_checkbox)
        layout.addRow("X-value:", self.x_line_value_edit)
        layout.addRow("Color:", self.color_x_change_line_combo)
        layout.addRow("Line Width:", self.width_x_change_line_edit)
        layout.addRow("Label:", self.x_line_label_edit)
        layout.addRow("", QLabel())

        # For plot_1
        self.first_color_probability_curve_combo = QComboBox()
        self.first_color_probability_curve_combo.addItems(color_options)
        cpc_1 = self.config['plot_1']['color_probability_curve']
        if cpc_1 not in color_options:
            self.first_color_probability_curve_combo.addItem(cpc_1)
        self.first_color_probability_curve_combo.setCurrentText(cpc_1)

        self.first_color_uncertainty_area_combo = QComboBox()
        self.first_color_uncertainty_area_combo.addItems(lighter_color_options)
        cua_1 = self.config['plot_1']['color_uncertainty_area']
        if cua_1 not in lighter_color_options:
            self.first_color_uncertainty_area_combo.addItem(cua_1)
        self.first_color_uncertainty_area_combo.setCurrentText(cua_1)

        self.first_probability_label_edit = QLineEdit(self.config['plot_1']['probability_label'])
        self.first_uncertantity_label_edit = QLineEdit(self.config['plot_1']['uncertantity_label'])

        first_label = QLabel("1st Plot")
        first_label.setObjectName("sectionLabel")
        layout.addRow(first_label, QLabel())
        layout.addRow("Probability Curve Color:", self.first_color_probability_curve_combo)
        layout.addRow("Uncertainty Area Color:", self.first_color_uncertainty_area_combo)
        layout.addRow("Probability Label:", self.first_probability_label_edit)
        layout.addRow("Uncertainty Label:", self.first_uncertantity_label_edit)
        layout.addRow("", QLabel())

        # For plot_2
        self.second_color_probability_curve_combo = QComboBox()
        self.second_color_probability_curve_combo.addItems(color_options)
        cpc_2 = self.config['plot_2']['color_probability_curve']
        if cpc_2 not in color_options:
            self.second_color_probability_curve_combo.addItem(cpc_2)
        self.second_color_probability_curve_combo.setCurrentText(cpc_2)

        self.second_color_uncertainty_area_combo = QComboBox()
        self.second_color_uncertainty_area_combo.addItems(lighter_color_options)
        cua_2 = self.config['plot_2']['color_uncertainty_area']
        if cua_2 not in lighter_color_options:
            self.second_color_uncertainty_area_combo.addItem(cua_2)
        self.second_color_uncertainty_area_combo.setCurrentText(cua_2)

        self.second_probability_label_edit = QLineEdit(self.config['plot_2']['probability_label'])
        self.second_uncertantity_label_edit = QLineEdit(self.config['plot_2']['uncertantity_label'])

        second_label = QLabel("2nd Plot")
        second_label.setObjectName("sectionLabel")
        layout.addRow(second_label, QLabel())
        layout.addRow("Probability Curve Color:", self.second_color_probability_curve_combo)
        layout.addRow("Uncertainty Area Color:", self.second_color_uncertainty_area_combo)
        layout.addRow("Probability Label:", self.second_probability_label_edit)
        layout.addRow("Uncertainty Label:", self.second_uncertantity_label_edit)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        save_button = QPushButton("Save")
        save_button.setObjectName("saveButton")
        save_button.clicked.connect(lambda: self.save_configuration(dialog))
        button_layout.addWidget(save_button)

        layout.addRow(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def save_configuration(self, dialog):
        """Save the configuration values"""
        try:
            config = {
                "shared": {
                    "x_label": self.xlabel_edit.text(),
                    "y_label": self.ylabel_edit.text(),
                    "color_x_change_line": self.color_x_change_line_combo.currentText(),
                    "width_probability_curve": self.validate_and_parse_float(self.width_probability_curve_edit.text(), "Probability Curve Width"),
                    "width_x_change_line": self.validate_and_parse_float(self.width_x_change_line_edit.text(), "Line Width"),
                    "width_uncertainty_area": self.validate_and_parse_float(self.width_uncertainty_area_edit.text(), "Uncertainty Area Width"),
                    "alpha_uncertainty_area": self.validate_and_parse_float(self.alpha_uncertainty_area_edit.text(), "Uncertainty Area Alpha"),
                    "x_line_value": self.validate_and_parse_float(self.x_line_value_edit.text(), "X-value"),
                    "draw_x_change_line": self.draw_x_change_line_checkbox.isChecked(),
                    "x_line_label": self.x_line_label_edit.text()
                },
                "plot_1": {
                    "color_probability_curve": self.first_color_probability_curve_combo.currentText(),
                    "color_uncertainty_area": self.first_color_uncertainty_area_combo.currentText(),
                    "probability_label": self.first_probability_label_edit.text(),
                    "uncertantity_label": self.first_uncertantity_label_edit.text()
                },
                "plot_2": {
                    "color_probability_curve": self.second_color_probability_curve_combo.currentText(),
                    "color_uncertainty_area": self.second_color_uncertainty_area_combo.currentText(),
                    "probability_label": self.second_probability_label_edit.text(),
                    "uncertantity_label": self.second_uncertantity_label_edit.text()
                }
            }

            if not self.validate_configuration(config):
                return
            
            self.config = config
            self.write_configuration()
            dialog.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return

    def validate_and_parse_float(self, value, field_name):
        """Validate and parse a string value as a float."""
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Invalid value for {field_name}: {value}. Please enter a numeric value.")

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

        if config['shared']['width_x_change_line'] < 0:
            QMessageBox.warning(self, "Invalid Input", "X-change 'Line Width' cannot be negative.")
            return False

        return True

    def download_plot(self):
        """Download the plot as a PNG, JPEG, or PDF file."""
        if self.plot_canvas is None:
            QMessageBox.warning(self, "Error", "There is no plot to download.")
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
        try:
            if self.plot_canvas is not None:
                self.plot_layout.removeWidget(self.plot_canvas)
                self.plot_canvas.deleteLater()
                self.plot_canvas = None
        except Exception:
            pass

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
        
        self.categorical_variable_frame.hide()
        self.categorical_variable_combobox.clear()

        self.probabilities_values = None
        self.probabilities_quantiles = None

        self.clear_input_layout()
        self.update_plot_title()
        self.clear_plot()
