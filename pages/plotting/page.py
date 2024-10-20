from PySide6.QtWidgets import QWidget, QSizePolicy, QSpacerItem, QVBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, QHBoxLayout, QComboBox, QListWidget, QTextEdit, QAbstractItemView, QFormLayout, QLineEdit
from PySide6.QtCore import Qt
from pages.plotting.probability import load_pr_variables, run_pr_function


class PlottingPage(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager

        # Main layout for the Plotting page
        main_layout = QVBoxLayout()

        # Set title
        self.Y_label = "Y"
        self.X_label = "X"
        self.y_value = "y"
        self.x_value = "x"
        self.data = "data"
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 30px;")
        main_layout.addWidget(self.title_label)

        # Area to display results
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        main_layout.addWidget(QLabel("Results:"))
        main_layout.addWidget(self.results_display)

        # Create the QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Make sure the widget inside resizes appropriately
        self.scroll_area.setMinimumWidth(1000)  # Set a minimum width to ensure the scroll area is not too narrow

        # Set a frame around the scroll area
        self.scroll_area.setFrameShape(QFrame.Box)  # Set frame shape
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid black; }")  # Set black frame color
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create a content widget that will go inside the scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Set spacing and margin adjustments for compact appearance
        content_layout.setSpacing(5)  # Adjust this value for more or less space between rows
        content_layout.setContentsMargins(50, 20, 50, 20)  # Reduce margins for a more compact look

        # Learnt folder selection (with fixed label width)
        learnt_layout = QHBoxLayout()  # Create a horizontal layout for learnt folder selection
        learnt_label = QLabel("Select a learnt folder:")
        self.pr_learnt_combobox = QComboBox()
        self.pr_learnt_combobox.currentIndexChanged.connect(self.on_learnt_folder_selected)
        fixed_label_width = 120  # You can adjust this to ensure both labels end at the same point
        learnt_label.setFixedWidth(fixed_label_width)
        learnt_layout.addWidget(learnt_label)
        learnt_layout.addWidget(self.pr_learnt_combobox)
        learnt_layout.setSpacing(5)  # Adjust the spacing between label and combobox
        content_layout.addLayout(learnt_layout)

        # Dataset selection (with fixed label width)
        dataset_layout = QHBoxLayout()  # Create a horizontal layout for dataset selection
        dataset_label = QLabel("Select a dataset:")
        self.pr_dataset_combobox = QComboBox()
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
        self.ranged_value_combobox = QComboBox()
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
        intermediate_layout.addStretch(1.0)  # Add stretch at the top to push the scroll area down
        intermediate_layout.addWidget(self.scroll_area, alignment=Qt.AlignCenter)  # Center the scroll area
        intermediate_layout.addStretch()  # Add stretch at the bottom to push the scroll area up

        # Add the intermediate layout to the main layout
        main_layout.addLayout(intermediate_layout)

        # Button to run the Pr function
        create_plot_button = QPushButton("Create Plot")
        create_plot_button.clicked.connect(self.on_create_plot_button_clicked)
        main_layout.addWidget(create_plot_button)

        # Set layout
        self.setLayout(main_layout)

        # Load and apply styles from the QSS file
        with open('pages/plotting/styles.qss', 'r') as f:
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

        # Set a percentage of the available space for the scroll area, for example, 80% of the height and 100% of the width
        scroll_area_width = int(current_size.width() * 0.5)  # 50% of the width
        scroll_area_height = int(current_size.height() * 0.8)  # 35% of the height

        # Update the size of the scroll area
        self.scroll_area.setFixedSize(scroll_area_width, scroll_area_height)

        # Call the base class's resizeEvent to ensure normal behavior
        super().resizeEvent(event)

    def update_title(self):
        """Update the title based on the selected values and input values."""
        y_values = self.get_input_value(self.selected_y_values)
        x_values = self.get_input_value(self.selected_x_values)

        y_labels = ", ".join([f"{label}={y_values.get(label, '')}" for label in self.selected_y_values])
        x_labels = ", ".join([f"{label}={x_values.get(label, '')}" for label in self.selected_x_values])

        if y_labels and x_labels:
            title = f"P({y_labels} | {x_labels}, {self.data})"
        elif y_labels:
            title = f"P({y_labels} | {self.data})"
        elif x_labels:
            title = f"P({self.Y_label}={self.y_value} | {x_labels}, {self.data})"
        else:
            title = f"P({self.Y_label}={self.y_value} | {self.X_label}={self.x_value}, {self.data})"

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
            load_pr_variables(self.pr_dataset_combobox, self.Y_listwidget, self.X_listwidget)
            self.Y_label_widget.show()
            self.X_label_widget.show()


    def load_result_folders_pr(self):
        """Load learnt folders into the PR learnt combobox from the FileManager."""
        self.pr_learnt_combobox.clear()

        if self.file_manager.learnt_folders:
            self.pr_learnt_combobox.addItems(self.file_manager.learnt_folders)
            self.pr_learnt_combobox.setCurrentIndex(-1)
        else:
            self.pr_learnt_combobox.addItem("No learnt folders available")
            self.pr_learnt_combobox.setItemData(1, Qt.NoItemFlags)

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
        current_size = self.size()

        scroll_area_width = int(current_size.width() * 0.5)  # 50% of the width
        scroll_area_height = int(current_size.height() * 0.30) # 30% of the height

        self.scroll_area.setFixedSize(scroll_area_width, scroll_area_height)

        # run_pr_function(self.results_display)