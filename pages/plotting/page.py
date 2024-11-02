import os
import json
import numpy as np
import pandas as pd
import importlib.resources
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QHBoxLayout, 
                                QComboBox, QListWidget, QFileDialog, QAbstractItemView, QFormLayout, QLineEdit, 
                                QFrame, QMessageBox, QSizePolicy, QAbstractItemView, QSpacerItem, QDialog)
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
        self.plot = False

        main_layout = QVBoxLayout()

        # Set title
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 30px;")
        main_layout.addWidget(self.title_label)

        # Area to display results
        self.plot_canvas = None
        self.plot_layout = QVBoxLayout()
        main_layout.addLayout(self.plot_layout)

        # Create the QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Make sure the widget inside resizes appropriately

        # Set a frame around the scroll area
        self.scroll_area.setFrameShape(QFrame.Box) 
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid black; }") 
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create a content widget that will go inside the scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Set spacing and margin adjustments for compact appearance
        content_layout.setSpacing(5)  # Adjust this value for more or less space between rows
        content_layout.setContentsMargins(50, 20, 50, 20)  # left, top, right, bottom

        # Learnt folder selection
        learnt_layout = QHBoxLayout()
        learnt_label = QLabel("Select a learnt folder:")
        self.pr_learnt_combobox = CustomComboBox()
        self.pr_learnt_combobox.currentIndexChanged.connect(self.on_learnt_folder_selected)
        fixed_label_width = 120  # You can adjust this to ensure both labels end at the same point
        learnt_label.setFixedWidth(fixed_label_width)
        learnt_layout.addWidget(learnt_label)
        learnt_layout.addWidget(self.pr_learnt_combobox)
        learnt_layout.setSpacing(5)  # Adjust the spacing between label and combobox
        content_layout.addLayout(learnt_layout)

        # Dataset selection
        dataset_layout = QHBoxLayout() 
        dataset_label = QLabel("Select a dataset:")
        self.pr_dataset_combobox = CustomComboBox()
        self.pr_dataset_combobox.currentIndexChanged.connect(self.on_dataset_selected_pr)
        dataset_label.setFixedWidth(fixed_label_width)
        dataset_label.setStyleSheet("padding-left: 23px;")
        dataset_layout.addWidget(dataset_label)
        dataset_layout.addWidget(self.pr_dataset_combobox)
        dataset_layout.setSpacing(5)  # Adjust the spacing between label and combobox
        content_layout.addLayout(dataset_layout)

        # Add space between the file selection and the variate selection
        spacer_label = QLabel()
        spacer_label.setFixedHeight(20)
        content_layout.addWidget(spacer_label)

        # Target (Y) selection - multi-select list widget for selecting the target variables
        self.Y_listwidget = QListWidget()
        self.Y_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.Y_listwidget.itemSelectionChanged.connect(self.on_Y_label_selected)
        self.Y_listwidget.setMinimumHeight(self.Y_listwidget.sizeHintForRow(0) * self.Y_listwidget.count() + 150)
        self.Y_label_widget = QLabel("Select target variable(s) Y:")
        self.Y_label_widget.hide()
        content_layout.addWidget(self.Y_label_widget)
        content_layout.addWidget(self.Y_listwidget)
        self.selected_y_values = []

        # X conditions selection (multi-select list widget)
        self.X_listwidget = QListWidget()
        self.X_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.X_listwidget.itemSelectionChanged.connect(self.on_X_label_selected)
        self.X_listwidget.setMinimumHeight(self.X_listwidget.sizeHintForRow(0) * self.X_listwidget.count() + 150)
        self.X_label_widget = QLabel("Select conditional variable(s) X (optional):")
        self.X_label_widget.hide()
        content_layout.addWidget(self.X_label_widget)
        content_layout.addWidget(self.X_listwidget)
        self.selected_x_values = []

        # Combobox for selecting which variate should have a ranged value
        self.ranged_value_label = QLabel("Which variable should be plotted against the X axis?")
        self.ranged_value_combobox = CustomComboBox()
        self.ranged_value_combobox.currentIndexChanged.connect(self.on_ranged_value_selected)
        self.ranged_value_label.hide()
        self.ranged_value_combobox.hide()
        content_layout.addWidget(self.ranged_value_label)
        content_layout.addWidget(self.ranged_value_combobox)

        # Layout to give values to the selected Y and X variates
        self.values_widget = QWidget()
        self.values_layout = QFormLayout()
        self.values_widget.setLayout(self.values_layout)
        content_layout.addWidget(self.values_widget)
        self.values_widget.hide()

        # Set the content widget to the scroll area
        self.scroll_area.setWidget(content_widget)

        # Create an intermediate layout to center the scroll_area
        intermediate_layout = QVBoxLayout()
        intermediate_layout.addWidget(self.scroll_area, alignment=Qt.AlignCenter)  # Center the scroll area

        # Add the intermediate layout to the main layout
        main_layout.addLayout(intermediate_layout)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setContentsMargins(0, 10, 0, 10)  # left, top, right, bottom

        # Button to run the Pr function
        create_plot_button = QPushButton("Generate Plot")
        create_plot_button.clicked.connect(self.on_create_plot_button_clicked)
        create_plot_button.setFixedWidth(150)
        button_layout.addWidget(create_plot_button)

        # Add a spacer to separate the buttons
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        button_layout.addItem(spacer)

        # Button to configure plot settings
        configure_plot_button = QPushButton("Configure Plot")
        configure_plot_button.clicked.connect(self.configure_plot)
        configure_plot_button.setFixedWidth(150)
        button_layout.addWidget(configure_plot_button)

        button_layout.addItem(spacer)

        # Button to save the plot
        download_plot_button = QPushButton("Download Plot")
        download_plot_button.clicked.connect(self.download_plot)
        download_plot_button.setFixedWidth(150)
        button_layout.addWidget(download_plot_button)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)

        # Set layout
        self.setLayout(main_layout)

        # Apply the stylesheet
        with importlib.resources.open_text('pages.plotting', 'styles.qss') as f:
            style = f.read()
            self.setStyleSheet(style)

        # Connect to file manager signals
        self.file_manager.files_updated.connect(self.load_files_pr)
        self.file_manager.learnt_folders_updated.connect(self.load_result_folders_pr)

        # Refresh the list of files and learnt folders
        self.file_manager.refresh()

        # Update the title after initializing all widgets
        self.update_title()


    ### HELPER FUNCTIONS ###

    def resizeEvent(self, event):
        # Get the size of the main window
        current_size = self.size()

        # Set a percentage of the available space for the scroll area
        scroll_area_width = int(current_size.width() * 0.50)  # 50% of the width
        self.scroll_area.setFixedWidth(scroll_area_width)
        if self.plot:
            scroll_area_height = int(current_size.height() * 0.30) # 30% of the height
            self.scroll_area.setFixedHeight(scroll_area_height)
        else:
            scroll_area_height = int(current_size.height() * 0.80) # 80% of the height
            self.scroll_area.setFixedHeight(scroll_area_height)

        # Call the base class's resizeEvent to ensure normal behavior
        super().resizeEvent(event)

    def update_title(self):
        """Update the title based on the selected values and input values."""
        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)
        data = self.pr_learnt_combobox.currentText()

        y_labels = ", ".join([f"{label}={y_values.get(label, '') or 'y'}" for label in self.selected_y_values])
        x_labels = ", ".join([f"{label}={x_values.get(label, '') or 'x'}" for label in self.selected_x_values])

        if y_labels and x_labels:
            title = f"P({y_labels} | {x_labels}, {data})"
        elif y_labels:
            title = f"P({y_labels} | {self.data})"
        elif x_labels:
            title = f"P(Y=y | {x_labels}, {data})"
        elif data:
            title = f"P(Y=y | X=x, {data})"
        else:
            title = "P(Y=y | X=x, data)"

        self.title_label.setText(title)

    def load_files_pr(self):
        """Load dataset files into the PR dataset combobox from the FileManager."""
        self.pr_dataset_combobox.clear()

        # Disconnect the signal temporarily while loading items
        self.pr_dataset_combobox.currentIndexChanged.disconnect(self.on_dataset_selected_pr)

        if self.file_manager.uploaded_files:
            self.pr_dataset_combobox.addItems(self.file_manager.uploaded_files)
            self.pr_dataset_combobox.setCurrentIndex(-1)
        else:
            self.pr_dataset_combobox.addItem("No datasets available")
            self.pr_dataset_combobox.setItemData(1, Qt.NoItemFlags)

        # Reconnect the signal after the combobox is populated
        self.pr_dataset_combobox.currentIndexChanged.connect(self.on_dataset_selected_pr)

    def on_dataset_selected_pr(self, index):
        """Load variables only when a dataset is selected by the user."""
        # Ensure an item is selected (index >= 0)
        if index >= 0:
            # Load variables for the new dataset
            self.load_pr_variables()
            self.Y_label_widget.show()
            self.X_label_widget.show()

            # Clear selections in Y and X list widgets
            self.Y_listwidget.clearSelection()
            self.X_listwidget.clearSelection()

            # Reset selected variables lists
            self.selected_y_values = []
            self.selected_x_values = []

            # Clear any input values in the input boxes
            self.clear_values_layout()

            # Update the title to reset it to default
            self.update_title()

    def load_result_folders_pr(self):
        """Load learnt folders into the PR learnt combobox from the FileManager."""
        self.pr_learnt_combobox.clear()

        if self.file_manager.learnt_folders:
            self.pr_learnt_combobox.addItems(self.file_manager.learnt_folders)
            self.pr_learnt_combobox.setCurrentIndex(-1)
        else:
            self.pr_learnt_combobox.addItem("No learnt folders available")
            self.pr_learnt_combobox.setItemData(1, Qt.NoItemFlags)
        
        self.update_title()

    def on_learnt_folder_selected(self, index):
        """Update the data value when a learnt folder is selected."""
        if index >= 0:
            self.data = self.pr_learnt_combobox.currentText()
        else:
            self.data = "data"
        self.update_title()

    def on_Y_label_selected(self):
        selected_items = self.Y_listwidget.selectedItems()
        self.selected_y_values = [item.text() for item in selected_items]
        self.update_combobox()
        self.update_title()
    
    def on_X_label_selected(self):
        selected_items = self.X_listwidget.selectedItems()
        self.selected_x_values = [item.text() for item in selected_items]
        self.update_combobox()
        self.update_title()
    
    def update_combobox(self):
        """Update the combobox with the selected Y values."""
        self.ranged_value_combobox.blockSignals(True)  # Temporarily block signals

        self.ranged_value_combobox.clear()
        combined_values = self.selected_y_values + self.selected_x_values
        self.ranged_value_combobox.addItems(combined_values)

        self.ranged_value_combobox.setCurrentIndex(-1)

        if self.selected_y_values and self.selected_x_values:
            self.ranged_value_label.show()
            self.ranged_value_combobox.show()
        else:
            self.ranged_value_label.hide()
            self.ranged_value_combobox.hide()

        self.ranged_value_combobox.blockSignals(False)  # Re-enable signals

        self.clear_values_layout()

    def clear_values_layout(self):
        """Clear and hide the values layout."""
        while self.values_layout.count():
            item = self.values_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.values_widget.hide()
    
    def on_ranged_value_selected(self, index):
        if index >= 0:
            self.update_values_layout()

    def update_values_layout(self):
        """Update the values layout with input boxes for selected Y and X variates."""
        self.clear_values_layout()

        # Add input boxes for selected Y variates
        for y_value in self.selected_y_values:
            label = QLabel(f"{y_value} = ")
            input_box = QLineEdit()
            input_box.setPlaceholderText("y")
            input_box.textChanged.connect(self.on_value_changed)

            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setStyleSheet("QFrame { border: 1px solid #0288d1; }")

            frame_layout = QVBoxLayout(frame)
            frame_layout.addWidget(input_box)

            self.values_layout.addRow(label, frame)

        # Add input boxes for selected X variates
        for x_value in self.selected_x_values:
            label = QLabel(f"{x_value} = ")
            input_box = QLineEdit()
            input_box.setPlaceholderText("x")
            input_box.textChanged.connect(self.on_value_changed)
            
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setStyleSheet("QFrame { border: 1px solid #0288d1; }")

            frame_layout = QVBoxLayout(frame)
            frame_layout.addWidget(input_box)

            self.values_layout.addRow(label, frame)

        self.values_widget.show()

    def get_input_value(self, selected_values):
        """Get the input value from the QLineEdit widgets inside the QFrames."""
        input_values = {}
        for i in range(self.values_layout.rowCount()):
            label_item = self.values_layout.itemAt(i, QFormLayout.LabelRole)
            widget_item = self.values_layout.itemAt(i, QFormLayout.FieldRole)
            if label_item and widget_item:
                label_text = label_item.widget().text().split('=')[0].strip()
                if label_text in selected_values:
                    frame = widget_item.widget()
                    if isinstance(frame, QFrame):
                        input_box = frame.findChild(QLineEdit)
                        if input_box:
                            input_values[label_text] = input_box.text()
        return input_values
    
    def on_value_changed(self):
        self.y_value = self.get_input_value(self.selected_y_values)
        self.x_value = self.get_input_value(self.selected_x_values)
        self.update_title()

    def on_create_plot_button_clicked(self):
        self.plot = True
        
        current_size = self.size()
        scroll_area_width = int(current_size.width() * 0.5)  # 50% of the width
        scroll_area_height = int(current_size.height() * 0.30) # 30% of the height
        self.scroll_area.setFixedSize(scroll_area_width, scroll_area_height)

        self.run_pr_function()

    def load_pr_variables(self):
        """Load available variables for the Pr function."""
        selected_dataset = self.pr_dataset_combobox.currentText()

        if selected_dataset == "No datasets available":
            QMessageBox.warning(None, "Error", "Please select a valid dataset.")
            return
        
        dataset_path = os.path.join(UPLOAD_FOLDER, selected_dataset)

        try:
            # Open and close the file safely to avoid permission errors
            with open(dataset_path, 'r') as f:
                data = pd.read_csv(f)

            # Clear previous items in list widgets
            self.Y_listwidget.clear()
            self.X_listwidget.clear()

            # Populate the list widgets with column names
            self.Y_listwidget.addItems(data.columns)
            self.X_listwidget.addItems(data.columns)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load dataset variables: {str(e)}")

    def run_pr_function(self):

        # Get input values for Y and X
        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)

        # Parse input values to get lists
        Y_dict = {}
        for var_name, value_string in y_values.items():
            value_list = self.parse_input_value(value_string)
            if not value_list:
                QMessageBox.warning(None, "Invalid Input", f"Invalid input for {var_name}: {value_string}")
                return
            Y_dict[var_name] = value_list

        X_dict = {}
        for var_name, value_string in x_values.items():
            value_list = self.parse_input_value(value_string)
            if not value_list:
                QMessageBox.warning(None, "Invalid Input", f"Invalid input for {var_name}: {value_string}")
                return
            X_dict[var_name] = value_list

        # Create DataFrames
        self.Y = pd.DataFrame(Y_dict)
        self.X = pd.DataFrame(X_dict)
        
        learnt_dir = os.path.join(LEARNT_FOLDER, self.pr_learnt_combobox.currentText())

        try:
            self.probabilities_values, self.probabilities_quantiles = run_Pr(self.Y, learnt_dir, self.X)

            if self.should_plot(self.Y, self.X):
                self.plot_probabilities()
        
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to run the Pr function: {str(e)}")

    def parse_input_value(self, value_string):
        if ':' in value_string:
            # It's a range
            start_str, end_str = value_string.split(':', 1)
            # Remove any parentheses or whitespace
            start_str = start_str.strip().strip('()')
            end_str = end_str.strip().strip('()')
            # Convert to numbers
            try:
                start_val = float(start_str)
                end_val = float(end_str)
                # Decide on the number of points
                num_points = int(abs(end_val - start_val)) + 1
                if start_val.is_integer() and end_val.is_integer():
                    # Use integers
                    value_list = list(range(int(start_val), int(end_val) + 1))
                else:
                    # Use numpy.linspace for floats
                    value_list = np.linspace(start_val, end_val, num=num_points).tolist()
            except ValueError:
                # Handle error
                QMessageBox.warning(None, "Invalid Input", f"Invalid range input: {value_string}")
                value_list = []
        else:
            # Single value
            value_list = [value_string.strip()]
        return value_list

    def should_plot(self, Y, X):
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

    def plot_probabilities(self):
        self.load_configuration()

        # Clear previous plot if any
        if self.plot_canvas is not None:
            self.plot_layout.removeWidget(self.plot_canvas)
            self.plot_canvas.deleteLater()
            self.plot_canvas = None

        # Create a Figure and FigureCanvas
        figure = Figure()
        ax = figure.add_subplot(111)
        self.plot_canvas = FigureCanvas(figure)
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the canvas to the plot_layout
        self.plot_layout.addWidget(self.plot_canvas)

        # Extract the column name dynamically from Y_values
        y_column = self.Y.columns[0]

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
        # Interpolate to make the plot look smoother
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

        # Open a file dialog to choose save location and filename
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
                # Save the figure
                self.plot_canvas.figure.savefig(file_path)
                QMessageBox.information(self, "Success", f"Plot saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save plot: {str(e)}")
