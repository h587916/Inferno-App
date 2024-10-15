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
        content_layout.setContentsMargins(50, 5, 50, 5)  # Reduce margins for a more compact look

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
        self.Y_label_widget = QLabel("Select target variable(s):")
        self.Y_label_widget.hide()
        content_layout.addWidget(self.Y_label_widget)
        content_layout.addWidget(self.Y_listwidget)

        # X conditions selection (multi-select list widget)
        self.X_listwidget = QListWidget()
        self.X_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.X_listwidget.itemSelectionChanged.connect(self.on_X_label_selected)
        self.X_listwidget.setMinimumHeight(self.X_listwidget.sizeHintForRow(0) * self.X_listwidget.count() + 150)
        self.X_label_widget = QLabel("Select conditional variable(s):")
        self.X_label_widget.hide()
        content_layout.addWidget(self.X_label_widget)
        content_layout.addWidget(self.X_listwidget)

        # Combobox for selecting which variate should have a ranged value
        self.ranged_value_label = QLabel("Which of the variate(s) should have a ranged value?")
        self.ranged_value_combobox = QComboBox()
        self.ranged_value_combobox.currentIndexChanged.connect(self.on_ranged_value_selected)
        content_layout.addWidget(self.ranged_value_label)
        content_layout.addWidget(self.ranged_value_combobox)
        self.ranged_value_label.hide()
        self.ranged_value_combobox.hide()

        # Input fields for Y and X values
        self.Y_inputs_layout = QFormLayout()
        self.X_inputs_layout = QFormLayout()

        # Add the input layouts to the scroll area's content layout (initially hidden)
        self.Y_inputs_widget = QLabel()
        self.X_inputs_widget = QLabel()
        content_layout.addWidget(self.Y_inputs_widget)
        content_layout.addLayout(self.Y_inputs_layout)
        content_layout.addWidget(self.X_inputs_widget)
        content_layout.addLayout(self.X_inputs_layout)

        self.Y_inputs_widget.hide()
        self.X_inputs_widget.hide()
        self.Y_inputs_layout_widget = self.Y_inputs_layout
        self.X_inputs_layout_widget = self.X_inputs_layout

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
        run_button = QPushButton("Run Pr Function")
        run_button.clicked.connect(lambda: run_pr_function(self.results_display))
        main_layout.addWidget(run_button)

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
        scroll_area_width = int(current_size.width() * 0.5)  # Full width
        scroll_area_height = int(current_size.height() * 0.35)  # 80% of the height

        # Update the size of the scroll area
        self.scroll_area.setFixedSize(scroll_area_width, scroll_area_height)

        # Call the base class's resizeEvent to ensure normal behavior
        super().resizeEvent(event)

    def update_title(self):
        y_labels = [item.text() for item in self.Y_listwidget.selectedItems()]
        x_labels = [item.text() for item in self.X_listwidget.selectedItems()]

        y_values = [self.Y_inputs[label].text() if self.Y_inputs[label].text() else "y" for label in y_labels]
        x_values = [self.X_inputs[label].text() if self.X_inputs[label].text() else "x" for label in x_labels]

        y_part = ", ".join([f"<span style='font-size: 30px;'>{label}</span><span style='font-size: 25px;'>=</span><span style='font-size: 25px;'>{value}</span>" for label, value in zip(y_labels, y_values)]) if y_labels else "<span style='font-size: 30px;'>Y</span><span style='font-size: 25px;'>=</span><span style='font-size: 25px;'>y</span>"
        x_part = ", ".join([f"<span style='font-size: 30px;'>{label}</span><span style='font-size: 25px;'>=</span><span style='font-size: 25px;'>{value}</span>" for label, value in zip(x_labels, x_values)]) if x_labels else "<span style='font-size: 30px;'>X</span><span style='font-size: 25px;'>=</span><span style='font-size: 25px;'>x</span>"

        title_html = f"""
        <span style="font-size: 40px;">P(</span>{y_part}<span style="font-size: 30px;"> | </span>{x_part}, <span style='font-size: 30px;'>{self.data}</span><span style="font-size: 40px;">)</span>
        """
        self.title_label.setText(title_html)


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
        """Update the Y value when a target variable is selected."""
        self.create_input_fields(self.Y_listwidget, self.Y_inputs_layout, "y")
        self.update_ranged_value_combobox()

    def on_X_label_selected(self):
        """Update the X value when a conditional variable is selected."""
        self.create_input_fields(self.X_listwidget, self.X_inputs_layout, "x")
        self.update_ranged_value_combobox()

    def update_ranged_value_combobox(self):
        """Update the ranged value combobox based on selected Y and X values."""
        selected_items = self.Y_listwidget.selectedItems() + self.X_listwidget.selectedItems()
        self.ranged_value_combobox.clear()
        if selected_items:
            self.ranged_value_label.show()
            self.ranged_value_combobox.show()
            self.ranged_value_combobox.addItem("Select a variate")
            for item in selected_items:
                self.ranged_value_combobox.addItem(item.text())
        else:
            self.ranged_value_label.hide()
            self.ranged_value_combobox.hide()

    def on_ranged_value_selected(self, index):
        """Show the input fields once a ranged value is selected."""
        if index > 0:  # Ensure a valid variate is selected
            self.Y_inputs_widget.show()
            self.X_inputs_widget.show()
            self.Y_inputs_layout_widget.setEnabled(True)
            self.X_inputs_layout_widget.setEnabled(True)
        else:
            self.Y_inputs_widget.hide()
            self.X_inputs_widget.hide()

    def create_input_fields(self, list_widget, layout, prefix):
        """Create input fields for the selected labels."""
        # Clear existing input fields
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

        # Create new input fields for selected labels
        selected_items = list_widget.selectedItems()
        inputs = {}
        for i, item in enumerate(selected_items):
            label = item.text()
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"{prefix}")
            input_field.textChanged.connect(self.update_title)
            layout.addRow(QLabel(label), input_field)
            inputs[label] = input_field

        # Store the inputs in the appropriate attribute
        if prefix == "y":
            self.Y_inputs = inputs
        else:
            self.X_inputs = inputs

        self.update_title()