import os
import pandas as pd
import importlib.resources
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QHBoxLayout, QListWidget, QFileDialog, QAbstractItemView, QFormLayout, QMessageBox, QSizePolicy, QAbstractItemView, QSpacerItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from pages.plotting.config import load_configuration, reset_configuration, write_configuration, configure_plot
from pages.plotting.variables import load_variables_into_lists, update_plot_variable_combobox, sync_variable_selections, clear_input_layout, update_values_layout_pr, clear_list_widget, update_values_layout_tailpr, update_categorical_variable_combobox, get_input_value
from pages.plotting.prob_functions import run_pr_function, run_tailpr_function
from pages.plotting.plotting import plot_pr_probabilities, plot_tailpr_probabilities, plot_tailpr_probabilities_multi, clear_plot
from pages.shared.custom_combobox import CustomComboBox
from appdirs import user_data_dir


APP_DIR = user_data_dir("Inferno App", "inferno")
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

        font = QFont()
        font.setPointSize(11)

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

        input_label = QLabel("Data selection")
        input_label.setObjectName("inputLabel")
        left_layout.addWidget(input_label)

        # Learnt folder selection
        self.learn_frame = QFrame()
        self.learn_frame.setObjectName("learnFrame")
        learnt_layout = QHBoxLayout(self.learn_frame)
        learnt_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        learnt_layout.setSpacing(5)

        learnt_label = QLabel("Select a learnt folder:")
        self.pr_learnt_combobox = CustomComboBox()
        self.pr_learnt_combobox.setFont(font)
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
        self.probability_function_combobox.setFont(font)
        self.probability_function_combobox.addItems(["Pr", "tailPr"])
        self.probability_function_combobox.setCurrentIndex(-1)

        self.probability_function_combobox.setItemData(
            0, 
            ("Pr: Calculates the posterior probabilities: <em>P(Y | X, data)</em>, where Y and X are two (non-overlapping) sets of joint variables. \n"
            "The function also gives quantiles about the possible variability of the probability P(Y | X, newdata, data) that we could have if more learning data were provided. \n"
            "In the generated plot from this app, the X-axis will show the defined range of a selected numeric Y-variable, and the Y-axis will show the calculated probability values."),
            Qt.ToolTipRole
        )

        self.probability_function_combobox.setItemData(
            1, 
            ("TailPr: Calculates the cumulative posterior probabilities: <em>P(Y ≤ y | X, data)</em> or <em>P(Y > y | X, data)</em>, where Y and X are two (non-overlapping) sets of joint variables. \n"
            "The function also returns quantiles representing the uncertainty in the estimated cumulative probability <em>P(Y ≤ y | X, newdata, data)</em>, reflecting how this estimate might vary if additional learning data were provided. \n"
            "In the generated plot from this app, the X-axis will show the defined range of a selected numeric X-variable, and the Y-axis will show the calculated cumulative probabilities."),
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

        input_label = QLabel("Variable selection")
        input_label.setObjectName("inputLabel")
        variable_selection_layout.addWidget(input_label)

        self.Y_label_widget = QLabel("")
        variable_selection_layout.addWidget(self.Y_label_widget)

        self.Y_listwidget = QListWidget()
        self.Y_listwidget.setFont(font)
        self.Y_listwidget.itemSelectionChanged.connect(self.on_Y_variable_selected)
        variable_selection_layout.addWidget(self.Y_listwidget)

        variable_selection_layout.addSpacing(20)
        
        self.X_label_widget = QLabel("")
        self.X_label_widget.hide()
        variable_selection_layout.addWidget(self.X_label_widget)

        self.X_listwidget = QListWidget()
        self.X_listwidget.setFont(font)
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

        plot_variable_label = QLabel("Variable to plot against the X-axis:")
        self.plot_variable_combobox = CustomComboBox()
        self.plot_variable_combobox = CustomComboBox()
        self.plot_variable_combobox.setFont(font)
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

        categorical_variable_label = QLabel("Categorical variable with two values?")
        self.categorical_variable_combobox = CustomComboBox()
        self.categorical_variable_combobox.setFont(font)
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
        self.values_layout.setLabelAlignment(Qt.AlignRight)
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
        clear_all_button.setObjectName("redButton")
        clear_all_button.clicked.connect(self.on_clear_all_button_clicked)
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
        self.download_plot_button.clicked.connect(self.on_download_plot_button_clicked)
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
        with importlib.resources.open_text('pages.shared', 'styles.qss') as f:
            common_style = f.read()

        with importlib.resources.open_text('pages.plotting', 'styles.qss') as f:
            page_style = f.read()
            
        self.setStyleSheet(common_style + page_style)

        # Connect to file manager signals
        self.file_manager.learnt_folders_updated.connect(self.load_learnt_folders)
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
    def load_learnt_folders(self):
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
        self.probability_function_combobox.blockSignals(True)
        self.probability_function_combobox.setCurrentIndex(-1)
        self.probability_function_frame.hide()
        self.probability_function_combobox.blockSignals(False)

        self.variable_selection_frame.hide()
        self.Y_listwidget.clear()
        self.X_listwidget.clear()
        self.Y_listwidget.clearSelection()
        self.X_listwidget.clearSelection()
        self.selected_y_values = []
        self.selected_x_values = []

        clear_input_layout(self)
        self.selected_func = None
        
        if index >= 0:
            self.data = self.pr_learnt_combobox.currentText()
            self.probability_function_frame.show()
        else:
            self.data = "data"
        self.update_plot_title()

    ############# PROBABILITY FUNCTION  SELECTION #############
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

    ############# VARIABLE SELECTION AND INPUT FIELDS #############
    def on_Y_variable_selected(self):
        """Update the selected Y variables and input fields based on the selected items."""
        selected_items = self.Y_listwidget.selectedItems()
        new_selected_y_values = [item.text() for item in selected_items]

        added_variables = list(set(new_selected_y_values) - set(self.selected_y_values))
        removed_variables = list(set(self.selected_y_values) - set(new_selected_y_values))

        self.selected_y_values = new_selected_y_values

        sync_variable_selections(self, added_variables, removed_variables)

        if self.selected_func == "Pr":
            update_plot_variable_combobox(self, self.selected_y_values + self.selected_x_values)

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

        if self.selected_func == "Pr":
            update_plot_variable_combobox(self, self.selected_y_values + self.selected_x_values)

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

    ############# PLOTTING AND PLOT CONFIG #############
    def on_generate_plot_button_clicked(self):
        """Run the appropiate probability function and plot the probabilities."""
        if self.selected_func == "Pr":
            run_pr_function(self)
        elif self.selected_func == "tailPr":
            run_tailpr_function(self)
        else:
            QMessageBox.warning(self, "Error", "Please select a valid probability function.")

    def on_configure_button_clicked(self):
        """Open the configuration dialog to change plot settings."""
        load_configuration(self)
        configure_plot(self)
        if self.probabilities_values is not None and self.probabilities_quantiles is not None:
            if self.selected_func == "Pr":
                plot_pr_probabilities(self)
            elif self.selected_func == "tailPr":
                categorical_variable = self.categorical_variable_combobox.currentText()
                if categorical_variable and categorical_variable in self.variable_values:
                    selected_categories = self.variable_values[categorical_variable]
                    if len(selected_categories) > 1:
                        plot_tailpr_probabilities_multi(self, selected_categories)
                    else:
                        plot_tailpr_probabilities(self)
                else:
                    plot_tailpr_probabilities(self)

    def on_download_plot_button_clicked(self):
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


    ############# CLEAR ALL #############
    def on_clear_all_button_clicked(self):
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
        clear_plot(self)
