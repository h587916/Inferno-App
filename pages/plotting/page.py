from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QStackedWidget, QComboBox, QListWidget, QTextEdit, QAbstractItemView, QFormLayout, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from pages.plotting.mutualinfo import load_mutual_variables, run_mutual_information
from pages.plotting.probability import load_pr_variables, run_pr_function


class PlottingPage(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager

        # Main layout for the Plotting page
        main_layout = QVBoxLayout()

        # Create a horizontal layout for the top navigation buttons (MutualInfo, Pr, tailPr)
        button_layout = QHBoxLayout()

        # Create buttons for each function
        self.info_button = QPushButton("Info")
        self.mutual_info_button = QPushButton("MutualInfo")
        self.pr_button = QPushButton("Pr")
        self.tailpr_button = QPushButton("TailPr")

        # Add buttons to the layout
        button_layout.addWidget(self.info_button)
        button_layout.addWidget(self.mutual_info_button)
        button_layout.addWidget(self.pr_button)
        button_layout.addWidget(self.tailpr_button)

        # Add button layout to the main layout
        main_layout.addLayout(button_layout)

        # Create a stacked widget to switch between different function input panels
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Set layout
        self.setLayout(main_layout)

        # Load and apply styles from the QSS file
        with open('pages/plotting/styles.qss', 'r') as f:
            style = f.read()
            self.setStyleSheet(style)

        # Create individual panels for each function
        self.create_info_panel()
        self.create_mutualinfo_panel()
        self.create_pr_panel()

        # Set default panel to info panel
        self.stacked_widget.setCurrentIndex(0)

        # Connect to file manager signals
        self.file_manager.files_updated.connect(self.load_files_mutualinfo)
        self.file_manager.files_updated.connect(self.load_files_pr)
        self.file_manager.learnt_folders_updated.connect(self.load_result_folders_mutualinfo)
        self.file_manager.learnt_folders_updated.connect(self.load_result_folders_pr)

        # Refresh the list of files and learnt folders
        self.file_manager.refresh()


    def create_info_panel(self):
        """Create the panel for the general info page."""
        info_panel = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is the general info page."))
        info_panel.setLayout(layout)

        # Add the info_panel to the stacked widget
        self.stacked_widget.addWidget(info_panel)

        # Connect button to display the Info panel
        self.info_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(info_panel))


    def create_mutualinfo_panel(self):
        """Create the panel for the MutualInfo function."""
        mutual_info_panel = QWidget()
        layout = QVBoxLayout()

        # Dataset selection
        self.mi_dataset_combobox = QComboBox()
        layout.addWidget(QLabel("Select a Dataset:"))
        layout.addWidget(self.mi_dataset_combobox)

        # Learnt folder selection
        self.mi_learnt_combobox = QComboBox()
        layout.addWidget(QLabel("Select a Learnt Folder:"))
        layout.addWidget(self.mi_learnt_combobox)

        # Rest of the mutual info setup
        self.predictand_combobox = QComboBox()
        self.predictor_listwidget = QListWidget()
        self.predictor_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.additional_predictor_listwidget = QListWidget()
        self.additional_predictor_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)

        layout.addWidget(QLabel("Select Predictand:"))
        layout.addWidget(self.predictand_combobox)

        layout.addWidget(QLabel("Select Predictor(s):"))
        layout.addWidget(self.predictor_listwidget)

        layout.addWidget(QLabel("Select Additional Predictor(s) (Optional):"))
        layout.addWidget(self.additional_predictor_listwidget)

        # Connect signal after setting up the layout but do not run it before an actual selection
        self.mi_dataset_combobox.currentIndexChanged.connect(self.on_dataset_selected)

        # Button to run mutual info
        run_button = QPushButton("Run Mutual Information")
        run_button.clicked.connect(lambda: run_mutual_information(
            self.predictand_combobox,
            self.predictor_listwidget,
            self.additional_predictor_listwidget,
            self.mi_learnt_combobox,
            self.results_display,
            self.mi_dataset_combobox
        ))
        layout.addWidget(run_button)

        # Area to display results
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(self.results_display)

        mutual_info_panel.setLayout(layout)

        # Add the mutual_info_panel to the stacked widget
        self.stacked_widget.addWidget(mutual_info_panel)

        # Connect button to display the MutualInfo panel
        self.mutual_info_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(mutual_info_panel))


    def create_pr_panel(self):
        """Create the panel for the Pr function."""
        pr_panel = QWidget()
        layout = QVBoxLayout()

        # Set title
        self.Y_label = "Y"
        self.X_label = "X"
        self.y_value = "y"
        self.x_value = "x"
        self.data = "data"
        self.title_label = QLabel()
        font = QFont()
        font.setPointSize(30)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # Learnt folder selection
        self.pr_learnt_combobox = QComboBox()
        layout.addWidget(QLabel("Select a Learnt Folder:"))
        layout.addWidget(self.pr_learnt_combobox)
        self.pr_learnt_combobox.currentIndexChanged.connect(self.on_learnt_folder_selected)

        # Dataset selection
        self.pr_dataset_combobox = QComboBox()
        layout.addWidget(QLabel("Select a Dataset:"))
        layout.addWidget(self.pr_dataset_combobox)
        self.pr_dataset_combobox.currentIndexChanged.connect(self.on_dataset_selected_pr)

        # Target (Y) selection - multi-select list widget for selecting the target variables
        self.Y_listwidget = QListWidget()
        self.Y_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(QLabel("Select the Target Variables (Y):"))
        layout.addWidget(self.Y_listwidget)
        self.Y_listwidget.itemSelectionChanged.connect(self.on_Y_label_selected)

        # X conditions selection (multi-select list widget)
        self.X_listwidget = QListWidget()
        self.X_listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(QLabel("Select the Conditional Variables (X):"))
        layout.addWidget(self.X_listwidget)
        self.X_listwidget.itemSelectionChanged.connect(self.on_X_label_selected)

        # Input fields for Y and X values
        self.Y_inputs_layout = QFormLayout()
        layout.addLayout(self.Y_inputs_layout)

        self.X_inputs_layout = QFormLayout()
        layout.addLayout(self.X_inputs_layout)

        # Area to display results
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(self.results_display)

        # Button to run the Pr function
        run_button = QPushButton("Run Pr Function")
        run_button.clicked.connect(lambda: run_pr_function(self.results_display))
        layout.addWidget(run_button)

        # Set the layout for the panel
        pr_panel.setLayout(layout)

        # Add the pr_panel to the stacked widget
        self.stacked_widget.addWidget(pr_panel)

        # Connect button to display the Pr panel
        self.pr_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(pr_panel))

        # Update the title after initializing all widgets
        self.update_title()


    ### HELPER FUNCTIONS ###

    def update_title(self):
        y_labels = [item.text() for item in self.Y_listwidget.selectedItems()]
        x_labels = [item.text() for item in self.X_listwidget.selectedItems()]

        y_values = [self.Y_inputs[label].text() if self.Y_inputs[label].text() else "y" for label in y_labels]
        x_values = [self.X_inputs[label].text() if self.X_inputs[label].text() else "x" for label in x_labels]

        y_part = ", ".join([f"<span style='font-size: 30px;'>{label}</span><span style='font-size: 25px;'>=</span><span style='font-size: 25px;'>{value}</span>" for label, value in zip(y_labels, y_values)]) if y_labels else "<span style='font-size: 30px;'>Y</span><span style='font-size: 25px;'>=</span><span style='font-size: 25px;'>y</span>"
        x_part = ", ".join([f"<span style='font-size: 30px;'>{label}</span><span style='font-size: 25px;'>=</span><span style='font-size: 25px;'>{value}</span>" for label, value in zip(x_labels, x_values)]) if x_labels else "<span style='font-size: 30px;'>X</span><span style='font-size: 25px;'>=</span><span style='font-size: 25px;'>x</span>"

        title_html = f"""
        <span style="font-size: 40px;">P(</span>{y_part}<span style="font-size: 30px;"> | </span>{x_part}, <span style='font-size: 30px;'>{self.data}</span><span style="font-size: 40px;">) = ?</span>
        """
        self.title_label.setText(title_html)

    def load_files_mutualinfo(self):
        """Load dataset files into the MI dataset combobox from the FileManager."""
        self.mi_dataset_combobox.clear()

        # Disconnect the signal temporarily while loading items
        self.mi_dataset_combobox.currentIndexChanged.disconnect(self.on_dataset_selected)

        if self.file_manager.uploaded_files:
            self.mi_dataset_combobox.addItems(self.file_manager.uploaded_files)
            self.mi_dataset_combobox.setCurrentIndex(-1)
        else:
            self.mi_dataset_combobox.addItem("No datasets available")
            self.mi_dataset_combobox.setItemData(1, Qt.NoItemFlags)

        # Reconnect the signal after the combobox is populated
        self.mi_dataset_combobox.currentIndexChanged.connect(self.on_dataset_selected)

    def on_dataset_selected(self, index):
        """Load variables only when a dataset is selected by the user."""
        # Ensure an item is selected (index >= 0)
        if index >= 0:
            load_mutual_variables(self.mi_dataset_combobox, self.predictand_combobox, self.predictor_listwidget, self.additional_predictor_listwidget)

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

    def load_result_folders_mutualinfo(self):
        """Load learnt folders into the MI learnt combobox from the FileManager."""
        self.mi_learnt_combobox.clear()

        if self.file_manager.learnt_folders:
            self.mi_learnt_combobox.addItems(self.file_manager.learnt_folders)
            self.mi_learnt_combobox.setCurrentIndex(-1)
        else:
            self.mi_learnt_combobox.addItem("No learnt folders available")
            self.mi_learnt_combobox.setItemData(1, Qt.NoItemFlags)

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

    def on_X_label_selected(self):
        """Update the X value when a conditional variable is selected."""
        self.create_input_fields(self.X_listwidget, self.X_inputs_layout, "x")

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