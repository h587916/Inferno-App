import os
import json
import numpy as np
import pandas as pd
import importlib.resources
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QHBoxLayout, 
                                QComboBox, QListWidget, QFileDialog, QAbstractItemView, QFormLayout, QLineEdit, 
                                QMessageBox, QSizePolicy, QAbstractItemView, QSpacerItem, QDialog)
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
        self.plot_canvas = None
        main_layout = QVBoxLayout()
        self.selected_y_values = []
        self.selected_x_values = []

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

        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(50, 0, 50, 20) # left, top, right, bottom

        # --- Left side of the page ---
        left_layout = QVBoxLayout()

        # Learnt folder selection
        self.learn_frame = QFrame()
        self.learn_frame.setObjectName("learnFrame")
        learnt_layout = QHBoxLayout(self.learn_frame)

        learnt_label = QLabel("Select a learnt folder:")
        self.pr_learnt_combobox = CustomComboBox()
        self.pr_learnt_combobox.currentIndexChanged.connect(self.on_learnt_folder_selected)
        self.pr_learnt_combobox.setMaximumWidth(300)
        fixed_label_width = 120  # You can adjust this to ensure both labels end at the same point
        learnt_label.setFixedWidth(fixed_label_width)

        learnt_layout.addWidget(learnt_label)
        learnt_layout.addWidget(self.pr_learnt_combobox)
        learnt_layout.setSpacing(5)  # Adjust the spacing between label and combobox
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
        self.Y_listwidget.itemSelectionChanged.connect(self.on_Y_label_selected)
        variable_selection_layout.addWidget(self.Y_listwidget)
        # self.selected_y_values = []
        
        X_label_widget = QLabel("Select conditional X-variables (optional):")
        variable_selection_layout.addWidget(X_label_widget)

        self.X_listwidget = QListWidget()
        self.X_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.X_listwidget.itemSelectionChanged.connect(self.on_X_label_selected)
        variable_selection_layout.addWidget(self.X_listwidget)
        # self.selected_x_values = []

        left_layout.addWidget(self.variable_selection_frame, alignment=Qt.AlignTop)

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

        # --- Right side of the page ---
        right_layout = QVBoxLayout()

        # Fixed-size box for the plot
        plot_frame = QFrame()
        plot_frame.setObjectName("plotFrame")
        plot_frame.setFixedSize(800, 600)
        self.plot_layout = QVBoxLayout(plot_frame)
        self.plot_layout.setContentsMargins(0, 20, 0, 10) # left, top, right, bottom

        # Set plot title
        self.plot_title = QLabel()
        self.plot_title.setObjectName("plotTitle")
        self.plot_title.setWordWrap(True)
        self.plot_title.setAlignment(Qt.AlignCenter)
        self.plot_layout.addWidget(self.plot_title)

        # Placeholder for the plot canvas
        self.plot_canvas_placeholder = QWidget()
        self.plot_canvas_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_layout.addWidget(self.plot_canvas_placeholder)

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
        right_layout.addWidget(plot_frame, alignment=Qt.AlignTop)
        right_layout.addLayout(self.plot_button_layout)
        right_layout.addStretch()

        # Add the content to the scroll layout, then to the main layout
        scroll_layout.addLayout(left_layout)
        scroll_layout.addSpacing(50)
        scroll_layout.addLayout(right_layout)
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
        self.update_title()


    ### HELPER FUNCTIONS ###

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

        self.plot_title.setText(title)

    def load_result_folders_pr(self):
        """Load learnt folders into the PR learnt combobox from the FileManager."""
        self.pr_learnt_combobox.clear()

        # Disconnect the signal temporarily while loading items
        self.pr_learnt_combobox.currentIndexChanged.disconnect(self.on_learnt_folder_selected)

        if self.file_manager.learnt_folders:
            self.pr_learnt_combobox.addItems(self.file_manager.learnt_folders)
            self.pr_learnt_combobox.setCurrentIndex(-1)
        else:
            self.pr_learnt_combobox.addItem("No learnt folders available")
            self.pr_learnt_combobox.setItemData(1, Qt.NoItemFlags)

        # Reconnect the signal after the combobox is populated
        self.pr_learnt_combobox.currentIndexChanged.connect(self.on_learnt_folder_selected)

    def on_learnt_folder_selected(self, index):
        """Update the data value when a learnt folder is selected."""
        if index >= 0:
            self.data = self.pr_learnt_combobox.currentText()
            self.load_metadata_pr()
            self.variable_selection_frame.show()

            # Clear selections in Y and X list widgets
            self.Y_listwidget.clearSelection()
            self.X_listwidget.clearSelection()

            # Reset selected variables lists
            self.selected_y_values = []
            self.selected_x_values = []

            # Clear any input values in the input boxes
            self.clear_values_layout()
        else:
            self.data = "data"
        self.update_title()

    def load_metadata_pr(self):
        """Load variates from the metadata.csv file in the selected learnt folder."""
        learnt_folder = self.pr_learnt_combobox.currentText()
        metadata_path = os.path.join(LEARNT_FOLDER, learnt_folder, 'metadata.csv')

        if not os.path.exists(metadata_path):
            QMessageBox.warning(None, "Error", "Metadata file not found.")
            return
        
        try:
            metadata_df = pd.read_csv(metadata_path)

            self.Y_listwidget.clear()
            self.X_listwidget.clear()

            variates = metadata_df["name"].tolist()
            self.Y_listwidget.addItems(variates)
            self.X_listwidget.addItems(variates)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to load metadata: {str(e)}")

    def get_metadata_for_selected_values(self):
        """Retrieve metadata for selected Y and X values from the metadata.csv file in the learnt folder."""
        learnt_folder = self.pr_learnt_combobox.currentText()
        metadata_path = os.path.join(LEARNT_FOLDER, learnt_folder, 'metadata.csv')

        try:
            metadata_df = pd.read_csv(metadata_path)
            selected_values = self.selected_y_values + self.selected_x_values
            metadata_filtered = metadata_df[metadata_df["name"].isin(selected_values)]
            metadata_dict = metadata_filtered.set_index("name").to_dict("index")

            return metadata_dict

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read metadata: {str(e)}")
            return {}

    def on_Y_label_selected(self):
        selected_items = self.Y_listwidget.selectedItems()
        self.selected_y_values = [item.text() for item in selected_items]
        self.update_values_layout()
        self.update_title()
    
    def on_X_label_selected(self):
        selected_items = self.X_listwidget.selectedItems()
        self.selected_x_values = [item.text() for item in selected_items]
        self.update_values_layout()
        self.update_title()

    def clear_values_layout(self):
        """Clear and hide the values layout."""
        while self.values_layout.count():
            item = self.values_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def update_values_layout(self):
        """Update the values layout with input boxes for selected Y and X variates."""
        self.clear_values_layout()

        # Add input boxes for selected Y variates
        for y_value in self.selected_y_values:
            label = QLabel(f"{y_value} = ")
            input_box = QLineEdit()
            input_box.setPlaceholderText("y")
            input_box.textChanged.connect(self.update_title)

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
            input_box.textChanged.connect(self.update_title)
            
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setStyleSheet("QFrame { border: 1px solid #0288d1; }")

            frame_layout = QVBoxLayout(frame)
            frame_layout.addWidget(input_box)

            self.values_layout.addRow(label, frame)

        self.input_frame.show()

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

    def run_pr_function(self):
        """ Run the Pr function and plot the probabilities."""
        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)

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

        self.Y = pd.DataFrame(Y_dict)
        self.X = pd.DataFrame(X_dict)
        
        learnt_dir = os.path.join(LEARNT_FOLDER, self.pr_learnt_combobox.currentText())

        try:
            if self.should_plot():
                self.probabilities_values, self.probabilities_quantiles = run_Pr(self.Y, learnt_dir, self.X)
                self.plot_probabilities()
                self.plot = True
            else:
                QMessageBox.warning(None, "No Plot", "No plot generated. No numeric variable with multiple values to plot.")
        
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to run the Pr function: {str(e)}")

    def parse_input_value(self, value_string):
        """Parse the input value string and return a list of values."""
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

        # Clear previous plot if any
        if hasattr(self, 'plot_canvas') and self.plot_canvas is not None:
            self.plot_layout.removeWidget(self.plot_canvas)
            self.plot_canvas.deleteLater()
            self.plot_canvas = None

        # Create a Figure and FigureCanvas
        figure = Figure()
        ax = figure.add_subplot(111)
        self.plot_canvas = FigureCanvas(figure)
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the canvas to the plot_layout
        self.plot_layout.insertWidget(1, self.plot_canvas)

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

    def clear_all(self):
        """Clears all selections and resets the interface."""
        confirm = QMessageBox.question(self, "Clear All", f"Are you sure you want to clear all?", 
                                           QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            # Clear the comboboxes
            self.pr_learnt_combobox.setCurrentIndex(-1)

            # Clear the list widgets
            self.Y_listwidget.clear()
            self.X_listwidget.clear()

            # Hide the variable selection frame
            self.variable_selection_frame.hide()

            # Clear the selections
            self.Y_listwidget.clearSelection()
            self.X_listwidget.clearSelection()

            # Reset selected variables lists
            self.selected_y_values = []
            self.selected_x_values = []

            # Clear input values in values_layout
            self.clear_values_layout()

            # Hide the input frame
            self.input_frame.hide()

            # Reset the title to default
            self.update_title()

            if hasattr(self, 'plot_canvas') and self.plot_canvas is not None:
                self.plot_layout.removeWidget(self.plot_canvas)
                self.plot_canvas.deleteLater()
                self.plot_canvas = None
