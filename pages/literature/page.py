from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFormLayout, QFrame, QHBoxLayout
from PySide6.QtWidgets import QTextBrowser
from PySide6.QtCore import Qt


class LiteraturePage(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout for the Literature page
        main_layout = QVBoxLayout()

        # Add a title
        title_label = QLabel("Relevant Literature")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Scroll area for the literature list (for long content)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout()

        ### Literature Explaining the Method ###
        method_label = QLabel("Literature Explaining the Method")
        method_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        content_layout.addWidget(method_label)

        # Add method literature references
        self.add_literature_reference(content_layout, "McElreath: Statistical Rethinking", "mcelreath2016_r2020-Statistical_rethinking")
        self.add_literature_reference(content_layout, 
                                      "Center for Devices and Radiological Health (USA Dept of Health): Guidance for the Use of Bayesian Statistics in Medical Device Clinical Trials",
                                      "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/guidance-use-bayesian-statistics-medical-device-clinical-trials")
        self.add_literature_reference(content_layout, "Goodman: Toward Evidence-Based Medical Statistics", "goodman1999")
        self.add_literature_reference(content_layout, "Charlesworth & Pandit: Negative outcomes in critical care trials", "doi.org/10.1111/anae.15028")
        self.add_literature_reference(content_layout, "Manski: Treatment Choice With Trial Data", "doi.org/10.1080/00031305.2018.1513377")
        self.add_literature_reference(content_layout, "Rossi: Bayesian Non- and Semi-parametric Methods and Applications", "rossi2014-Bayesian_non-_and_semi-parametric_methods_and_applications")

        ### Literature Using the Method ###
        method_usage_label = QLabel("Literature Using the Method")
        method_usage_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        content_layout.addWidget(method_usage_label)

        self.add_literature_reference(content_layout, "Sox & al: Medical Decision Making", "soxetal1988_r2013-Medical_decision_making")
        self.add_literature_reference(content_layout, 
                                      "Temp & al: How Bayesian statistics may help answer some of the controversial questions in clinical research on Alzheimer's disease", 
                                      "tempetal2021")
        self.add_literature_reference(content_layout, 
                                      "Antoniano-Villalobos & al: A Bayesian Nonparametric Regression Model With Normalized Weights", 
                                      "antonianovillalobosetal2014")
        self.add_literature_reference(content_layout, 
                                      "Andersson & Moser & Moser: Visual stimulus features that elicit activity in object-vector cells", 
                                      "doi.org/10.1038/s42003-021-02727-5")
        self.add_literature_reference(content_layout, 
                                      "Sidebotham: Are most randomised trials in anaesthesia and critical care wrong?", 
                                      "doi.org/10.1111/anae.15029")
        self.add_literature_reference(content_layout, 
                                      "Ruberg & al: Inference and Decision Making for 21st-Century Drug Development and Approval", 
                                      "doi.org/10.1080/00031305.2019.1566091")
        self.add_literature_reference(content_layout, 
                                      "Porta Mana & al: Personalized prognosis & treatment using an optimal predictor machine", 
                                      "doi.org/10.31219/osf.io/8nr56")
        self.add_literature_reference(content_layout, 
                                      "Event Horizon Telescope Collaboration: First M87 Event Horizon Telescope Results", 
                                      "doi.org/10.3847/2041-8213/ab0ec7")
        self.add_literature_reference(content_layout, 
                                      "Event Horizon Telescope Collaboration: First Sagittarius-A Event Horizon Telescope Results", 
                                      "doi.org/10.3847/2041-8213/ac6674")

        # Add content to the scroll area
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Set the layout for the page
        self.setLayout(main_layout)

    def add_literature_reference(self, layout, title, link):
        """Helper method to add a literature reference with optional notes."""
        # Create a horizontal layout for the reference
        ref_layout = QHBoxLayout()

        # Create the reference title (linked or plain text)
        if link.startswith("http"):
            reference_label = QTextBrowser()
            reference_label.setHtml(f'<a href="{link}" style="color:blue;">{title}</a>')
            reference_label.setOpenExternalLinks(True)
        else:
            reference_label = QLabel(f"{title} [{link}]")

        # Add the reference to the layout
        ref_layout.addWidget(reference_label)

        # Add the reference layout to the main layout
        layout.addLayout(ref_layout)

