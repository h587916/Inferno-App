import os
import numpy as np
import pandas as pd
import importlib.resources
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QHBoxLayout, 
                                QComboBox, QListWidget, QFileDialog, QAbstractItemView, QFormLayout, QLineEdit, 
                                QMessageBox, QSizePolicy, QAbstractItemView, QSpacerItem)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from r_integration.inferno_functions import run_Pr, run_tailPr
from scipy.interpolate import make_interp_spline
from pages.plotting.config import load_configuration, reset_configuration, write_configuration, update_configuration, configure_plot
from pages.plotting.variables import load_variables_into_lists, update_plot_variable_combobox, sync_variable_selections, clear_input_layout, update_values_layout_pr, clear_list_widget, update_values_layout_tailpr, update_categorical_variable_combobox, get_input_value
from pages.plotting.custom_combobox import CustomComboBox

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, '.inferno_app')

UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
LEARNT_FOLDER = os.path.join(APP_DIR, 'learnt')

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
        self.selected_func = None
        reset_configuration(self)
        write_configuration(self)

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

        # Select probability function
        self.probability_function_frame = QFrame()
        self.probability_function_frame.setObjectName("probabilityFunctionFrame")
        self.probability_function_frame.hide()
        probability_function_layout = QHBoxLayout(self.probability_function_frame)
        probability_function_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        probability_function_layout.setSpacing(5)

        probability_function_label = QLabel("Select a probability function:")
        self.probability_function_combobox = CustomComboBox()
        self.probability_function_combobox.addItems(["Pr", "tailPr"])
        self.probability_function_combobox.setCurrentIndex(-1)

        self.probability_function_combobox.setItemData(
            0, 
            ("Pr: Calculates P(Y | X, data). This function computes the probability of a range of values for a numeric Y-variable \n"
            "against specified values of X-variables. The results include quantiles representing the variability in the probabilities \n"
            "if additional data were available, as well as samples of possible probability values. In the plot, the defined range for the \n"
            "numeric Y-variable is displayed on the X-axis, and the probability values are plotted on the Y-axis."),
            Qt.ToolTipRole
        )

        self.probability_function_combobox.setItemData(
            1, 
            ("TailPr: Calculates P(Y <= y | X, data) or P(Y > y | X, data). This function computes cumulative probabilities \n"
            "for a specific value of a numeric Y-variable against specified X-variables. The results include quantiles showing variability \n"
            "in cumulative probabilities if additional data were available, as well as samples of possible values. The plot displays the numeric \n"
            "X-variable on the X-axis and the cumulative probabilities on the Y-axis."),
            Qt.ToolTipRole
        )

        self.probability_function_combobox.currentIndexChanged.connect(self.on_probability_function_selected)

        probability_function_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.probability_function_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        probability_function_layout.addWidget(probability_function_label)
        probability_function_layout.addWidget(self.probability_function_combobox)
        left_layout.addWidget(self.probability_function_frame, alignment=Qt.AlignTop)

        # Variable selection frame
        self.variable_selection_frame = QFrame()
        self.variable_selection_frame.setObjectName("variableSelectionFrame")
        self.variable_selection_frame.hide()
        variable_selection_layout = QVBoxLayout(self.variable_selection_frame)

        self.Y_label_widget = QLabel("")
        variable_selection_layout.addWidget(self.Y_label_widget)

        self.Y_listwidget = QListWidget()
        self.Y_listwidget.itemSelectionChanged.connect(self.on_Y_variable_selected)
        variable_selection_layout.addWidget(self.Y_listwidget)

        variable_selection_layout.addSpacing(20)
        
        self.X_label_widget = QLabel("")
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

        plot_variable_label = QLabel("Select the variable to plot against the X-axis:") # TODO: oppdater tekst
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
        create_plot_button.clicked.connect(self.on_generate_plot_button_clicked)
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
        y_values = get_input_value(self, self.selected_y_values)
        x_values = get_input_value(self, self.selected_x_values)
        data = self.pr_learnt_combobox.currentText()

        if self.selected_func == "tailPr":
            formatted_y_labels = []
            for y_var in self.selected_y_values:
                y_dict = y_values.get(y_var, {})
                inequality = y_dict.get('inequality', '')
                val = y_dict.get('value', '').strip()
                if inequality and val:
                    formatted_y_labels.append(f"{y_var}{inequality}{val}")
                else:
                    formatted_y_labels.append(f"{y_var}=y")

            x_labels = ", ".join([
                f"{label}={self.format_value(x_values.get(label, '')) or 'x'}"
                for label in self.selected_x_values
            ])

            y_labels_str = ", ".join(formatted_y_labels)

            if y_labels_str and x_labels:
                title = f"P({y_labels_str} | {x_labels}, {data})"
            elif y_labels_str:
                title = f"P({y_labels_str} | {data})"
            elif x_labels:
                title = f"P(Y=y | {x_labels}, {data})"
            elif data:
                title = f"P(Y=y | X=x, {data})"
            else:
                title = "P(Y=y | X=x, data)"

        elif self.selected_func == "Pr":
            y_labels = ", ".join(
                f"{label}={self.format_value(y_values.get(label, '')) or 'y'}"
                for label in self.selected_y_values
            )
            x_labels = ", ".join(
                f"{label}={self.format_value(x_values.get(label, '')) or 'x'}"
                for label in self.selected_x_values
            )

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
        """Display the probability function frame when a learnt folder is selected."""
        if index >= 0:
            self.data = self.pr_learnt_combobox.currentText()
            self.probability_function_frame.show()
        else:
            self.data = "data"
            self.probability_function_frame.hide()
        self.update_plot_title()

    ############# PROBABILITY FUNCTION #############
    def on_probability_function_selected(self, index):
        """Update the UI based on the selected probability function."""
        if index >= 0:

            self.selected_func = self.probability_function_combobox.currentText()
            if self.selected_func == "tailPr":
                self.Y_listwidget.setSelectionMode(QAbstractItemView.SingleSelection)
                self.Y_label_widget.setText("Select target Y-variable:")
                self.X_label_widget.setText("Select conditional X-variable(s):")
            elif self.selected_func == "Pr":
                self.Y_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
                self.Y_label_widget.setText("Select target Y-variable(s):")
                self.X_label_widget.setText("Select conditional X-variable(s) (optional):")

            load_variables_into_lists(self)
            self.variable_selection_frame.show()

            self.Y_listwidget.clearSelection()
            self.X_listwidget.clearSelection()

            self.selected_y_values = []
            self.selected_x_values = []

            clear_input_layout(self)

    ############# VARIABLE SELECTION #############
    def on_Y_variable_selected(self):
        """Update the selected Y variables and input fields based on the selected items."""
        selected_items = self.Y_listwidget.selectedItems()
        new_selected_y_values = [item.text() for item in selected_items]

        added_variables = list(set(new_selected_y_values) - set(self.selected_y_values))
        removed_variables = list(set(self.selected_y_values) - set(new_selected_y_values))

        self.selected_y_values = new_selected_y_values

        sync_variable_selections(self, added_variables, removed_variables)

        if self.selected_func == "Pr":
            update_plot_variable_combobox(self, self.selected_y_values)

    def on_X_variable_selected(self):
        """Update the selected X variables and input fields based on the selected items."""
        selected_items = self.X_listwidget.selectedItems()
        new_selected_x_values = [item.text() for item in selected_items]

        added_variables = list(set(new_selected_x_values) - set(self.selected_x_values))
        removed_variables = list(set(self.selected_x_values) - set(new_selected_x_values))

        self.selected_x_values = new_selected_x_values

        sync_variable_selections(self, added_variables, removed_variables)

        if self.selected_func == "tailPr":
            update_plot_variable_combobox(self, self.selected_x_values)

    def on_plot_variable_selected(self, index):
        """Update the the values layout based on the selected plot variable."""
        clear_input_layout(self)
        
        if index >= 0:
            if self.selected_func == "tailPr":
                update_values_layout_tailpr(self)
            elif self.selected_func == "Pr":
                update_values_layout_pr(self)
            self.input_frame.show()
            update_categorical_variable_combobox(self)
        else:
            self.input_frame.hide()
            self.categorical_variable_combobox.clear()
            self.categorical_variable_frame.hide()

    def on_categorical_variable_selected(self, index):
        """Update the values layout based on the selected categorical variable."""
        clear_list_widget(self)
        clear_input_layout(self)

        if self.selected_func == "tailPr":
            update_values_layout_tailpr(self)
        elif self.selected_func == "Pr":
            update_values_layout_pr(self)

        self.input_frame.show()

    ############# RUN PROBABILITY FUNCTION #############
    def run_pr_function(self):
        """ Run the Pr function and plot the probabilities."""
        if not self.all_values_filled():
            QMessageBox.warning(self, "Error", "Please fill out all value-fields for the selected variables.")
            return

        y_values = get_input_value(self, self.selected_y_values)
        x_values = get_input_value(self, self.selected_x_values)

        Y_df = self.parse_and_validate_input_values(y_values)
        if Y_df is None:
            return
        X_df = self.parse_and_validate_input_values(x_values)
        if X_df is None:
            return
    
        self.Y = Y_df 
        self.X = X_df
        
        learnt_dir = os.path.join(LEARNT_FOLDER, self.pr_learnt_combobox.currentText())

        try:
            self.probabilities_values, self.probabilities_quantiles = run_Pr(self.Y, learnt_dir, self.X)
            reset_configuration(self)
            update_configuration(self)
            write_configuration(self)
            self.plot_pr_probabilities()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to plot probabilities using Pr function: {str(e)}")

    def run_tailpr_function(self):
        """Run the tailPr function and plot the probabilities."""
        if not self.all_values_filled():
            QMessageBox.warning(self, "Error", "Please fill out all value-fields...")
            return

        y_values = get_input_value(self, self.selected_y_values)
        x_values = get_input_value(self, self.selected_x_values)
        Y_df = self.parse_and_validate_input_values(y_values)
        X_df = self.parse_and_validate_input_values(x_values)
        if Y_df is None or X_df is None:
            return

        self.Y = Y_df
        self.X = X_df

        y_variable = self.selected_y_values[0] if self.selected_y_values else None
        eq, lower_tail = self.determine_inequality(y_variable)

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
                        X_single = self.build_single_category_X(X_df, cat_val, categorical_variable)

                        single_values, single_quantiles = run_tailPr(self.Y, learnt_dir, eq, lower_tail, X_single)
                        self.probabilities_values.append(single_values)
                        self.probabilities_quantiles.append(single_quantiles)

                    reset_configuration(self)
                    update_configuration(self)
                    write_configuration(self)
                    self.plot_tailpr_probabilities_multi(selected_categories)
                else:
                    self.probabilities_values, self.probabilities_quantiles = run_tailPr(self.Y, learnt_dir, eq, lower_tail, self.X)
                    reset_configuration(self)
                    update_configuration(self)
                    write_configuration(self)
                    self.plot_tailpr_probabilities()
            else:
                self.probabilities_values, self.probabilities_quantiles = run_tailPr(self.Y, learnt_dir, eq, lower_tail, self.X)
                reset_configuration(self)
                update_configuration(self)
                write_configuration(self)
                self.plot_tailpr_probabilities()

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to plot probabilities using tailPr function: {str(e)}")
            return

    def build_single_category_X(self, X_df, cat_val, cat_var):
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

    ############# PLOTTING #############
    def on_generate_plot_button_clicked(self):
        """Run the appropiate probability function and plot the probabilities."""
        if self.selected_func == "Pr":
            self.run_pr_function()
        elif self.selected_func == "tailPr":
            self.run_tailpr_function()
        else:
            QMessageBox.warning(self, "Error", "Please select a valid probability function.")

    def plot_pr_probabilities(self):
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

        if self.config['x_line'].get('draw', False):
            ax.axvline(
                x=self.config['x_line']['value'], 
                color=self.config['x_line']['color'], 
                linestyle='--', linewidth=self.config['x_line']['width'], 
                label=self.config['x_line']['label']
            )

        if self.config['y_line'].get('draw', False):
            ax.axhline(
                y=self.config['y_line']['value'], 
                color=self.config['y_line']['color'], 
                linestyle='--', linewidth=self.config['y_line']['width'], 
                label=self.config['y_line']['label']
            )

        ax.set_xlabel(self.config['shared']['x_label'])
        ax.set_ylabel(self.config['shared']['y_label'])
        ax.legend()

        self.plot_canvas.draw()

    def plot_tailpr_probabilities(self):
        """Plot cumulative probabilities and quantiles for tailPr."""
        self.clear_plot()

        figure = Figure()
        ax = figure.add_subplot(111)
        self.plot_canvas = FigureCanvas(figure)
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_layout.insertWidget(1, self.plot_canvas)

        probabilities_values = np.array(self.probabilities_values)
        probabilities_quantiles = np.array(self.probabilities_quantiles)

        plot_variable = self.plot_variable_combobox.currentText()
        if plot_variable in self.Y.columns:
            x_values = self.Y[plot_variable]
        elif plot_variable in self.X.columns:
            x_values = self.X[plot_variable]
        else:
            QMessageBox.warning(None, "Error", f"The selected plot variable '{plot_variable}' was not found in Y or X.")
            return

        try:
            spl = make_interp_spline(x_values, probabilities_values[0, :], k=3)
            x_smooth = np.linspace(x_values.min(), x_values.max(), 500)
            prob_smooth = spl(x_smooth)
        except ValueError:
            x_smooth = x_values
            prob_smooth = probabilities_values[0, :]

        if not self.config['plot_1']['probability_label']:
            self.config['plot_1']['probability_label'] = "Probability"
        if not self.config['plot_1']['uncertantity_label']:
            self.config['plot_1']['uncertantity_label'] = "5.5%, 94.5%"

        ax.plot(
            x_smooth,
            prob_smooth,
            color=self.config['plot_1']['color_probability_curve'],
            linewidth=self.config['shared']['width_probability_curve'],
            linestyle='-',
            label=self.config['plot_1']['probability_label']
        )

        ax.fill_between(
            x_values,
            probabilities_quantiles[0, :, 0],
            probabilities_quantiles[0, :, -1],
            color=self.config['plot_1']['color_uncertainty_area'],
            alpha=self.config['shared']['alpha_uncertainty_area'],
            edgecolor=self.config['plot_1']['color_probability_curve'],
            linewidth=self.config['shared']['width_uncertainty_area'],
            label=self.config['plot_1']['uncertantity_label'] 
        )

        if self.config['x_line'].get('draw', True):
            ax.axvline(
                x=self.config['x_line']['value'],
                color=self.config['x_line']['color'],
                linestyle='--',
                linewidth=self.config['x_line']['width'],
                label=self.config['x_line']['label']
            )

        if self.config['y_line'].get('draw', True):
            ax.axhline(
                y=self.config['y_line']['value'],
                color=self.config['y_line']['color'],
                linestyle='--',
                linewidth=self.config['y_line']['width'],
                label=self.config['y_line']['label']
            )

        y_variable = self.selected_y_values[0] if self.selected_y_values else None
        inequality = self.variable_values.get(y_variable, {}).get('inequality', '')
        value = self.variable_values.get(y_variable, {}).get('value', '')

        ax.set_xlabel(self.config['shared']['x_label'])
        ax.set_ylabel(f"Probability of {y_variable} {inequality} {value}")
        ax.legend()

        self.plot_canvas.draw()

    def plot_tailpr_probabilities_multi(self, categories):
        """Plot cumulative probabilities and quantiles for tailPr with multiple categories."""
        self.clear_plot()

        figure = Figure()
        ax = figure.add_subplot(111)
        self.plot_canvas = FigureCanvas(figure)
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_layout.insertWidget(1, self.plot_canvas)

        plot_variable = self.plot_variable_combobox.currentText()

        if plot_variable in self.Y.columns:
            x_values = self.Y[plot_variable]
        elif plot_variable in self.X.columns:
            x_values = self.X[plot_variable]
        else:
            QMessageBox.warning(None, "Error", f"Plot variable '{plot_variable}' not found in Y or X.")
            return

        for i in range(len(categories)):
            plot_key = f"plot_{i+1}"

            probabilities = np.array(self.probabilities_values[i])
            quantiles = np.array(self.probabilities_quantiles[i])

            try:
                spl = make_interp_spline(x_values, probabilities[0, :], k=3)
                x_smooth = np.linspace(x_values.min(), x_values.max(), 500)
                prob_smooth = spl(x_smooth)
            except ValueError:
                x_smooth = x_values
                prob_smooth = probabilities[0, :]

            if not self.config[plot_key]['probability_label']:
                self.config[plot_key]['probability_label'] = "Probability"
            if not self.config[plot_key]['uncertantity_label']:
                self.config[plot_key]['uncertantity_label'] = "5.5%, 94.5%"

            ax.plot(
                x_smooth,
                prob_smooth,
                color=self.config[plot_key]['color_probability_curve'], 
                linewidth=self.config['shared']['width_probability_curve'], 
                linestyle='-', 
                label=self.config[plot_key]['probability_label']
            )

            ax.fill_between(
                x_values, 
                quantiles[0, :, 0],
                quantiles[0, :, -1],
                color=self.config[plot_key]['color_uncertainty_area'], 
                alpha=self.config['shared']['alpha_uncertainty_area'], 
                edgecolor=self.config[plot_key]['color_probability_curve'], 
                linewidth=self.config['shared']['width_uncertainty_area'],
                label=self.config[plot_key]['uncertantity_label']
            )

        if self.config['x_line'].get('draw', False):
            ax.axvline(
                x=self.config['x_line']['value'], 
                color=self.config['x_line']['color'], 
                linestyle='--', 
                linewidth=self.config['x_line']['width'], 
                label=self.config['x_line']['label']
            )

        if self.config['y_line'].get('draw', False):
            ax.axhline(
                y=self.config['y_line']['value'], 
                color=self.config['y_line']['color'], 
                linestyle='--', 
                linewidth=self.config['y_line']['width'], 
                label=self.config['y_line']['label']
            )

        y_variable = self.selected_y_values[0] if self.selected_y_values else None
        inequality = self.variable_values.get(y_variable, {}).get('inequality', '')
        value = self.variable_values.get(y_variable, {}).get('value', '')

        ax.set_xlabel(self.config['shared']['x_label'])
        ax.set_ylabel(f"Probability of {y_variable} {inequality} {value}")
        ax.legend()
        self.plot_canvas.draw()

    def on_configure_button_clicked(self):
        """Open the configuration dialog to change plot settings."""
        load_configuration(self)
        configure_plot(self)
        if self.probabilities_values is not None and self.probabilities_quantiles is not None:
            if self.selected_func == "Pr":
                self.plot_pr_probabilities()
            elif self.selected_func == "tailPr":
                categorical_variable = self.categorical_variable_combobox.currentText()
                if categorical_variable and categorical_variable in self.variable_values:
                    selected_categories = self.variable_values[categorical_variable]
                    if len(selected_categories) > 1:
                        self.plot_tailpr_probabilities_multi(selected_categories)
                    else:
                        self.plot_tailpr_probabilities()
                else:
                    self.plot_tailpr_probabilities()

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

        clear_input_layout(self)
        self.update_plot_title()
        self.clear_plot()
