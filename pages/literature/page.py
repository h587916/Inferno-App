import importlib.resources
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTextBrowser, QFrame, QSizePolicy
from PySide6.QtCore import Qt

class LiteraturePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Main title
        title_label = QLabel("Literature - Bayesian Methods")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title_label)

        # Horizontal layout for the two sections; reduced top margin here
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(40, 40, 40, 100)  # left, top, right, bottom
        content_layout.setAlignment(Qt.AlignHCenter)

        # --- Section 1: Literature Explaining the Method ---
        method_layout = QVBoxLayout()
        method_layout.setAlignment(Qt.AlignHCenter)
        method_layout.setContentsMargins(0, 0, 20, 0)  # left, top, right, bottom

        # Title outside the box (bigger)
        method_title = QLabel("Literature Explaining the Method")
        method_title.setObjectName("litTitle")
        method_title.setAlignment(Qt.AlignCenter)
        method_layout.addWidget(method_title)

        # Colored box for the text; size policy set to minimum so it fits the text
        method_frame = QFrame()
        method_frame.setObjectName("litBox")
        method_frame.setFrameShape(QFrame.StyledPanel)
        method_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        method_frame_layout = QVBoxLayout(method_frame)
        method_frame_layout.setContentsMargins(10, 10, 10, 10)  # smaller internal margins
        method_frame_layout.setSpacing(5)
        method_frame_layout.setAlignment(Qt.AlignTop)

        method_browser = QTextBrowser()
        method_browser.setOpenExternalLinks(True)
        method_browser.setHtml(self.generate_literature_list([
            ("McElreath: Statistical Rethinking", None),
            ("Center for Devices and Radiological Health (USA Dept of Health): Guidance for the Use of Bayesian Statistics in Medical Device Clinical Trials", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/guidance-use-bayesian-statistics-medical-device-clinical-trials"),
            ("Goodman: Toward Evidence-Based Medical Statistics", None),
            ("Charlesworth & Pandit: Negative outcomes in critical care trials", "http://doi.org/10.1111/anae.15028"),
            ("Manski: Treatment Choice With Trial Data", "http://doi.org/10.1080/00031305.2018.1513377"),
            ("Rossi: Bayesian Non- and Semi-parametric Methods and Applications", None)
        ]))
        method_frame_layout.addWidget(method_browser)
        method_layout.addWidget(method_frame)
        content_layout.addLayout(method_layout)

        # --- Section 2: Literature Using the Method ---
        usage_layout = QVBoxLayout()
        usage_layout.setAlignment(Qt.AlignHCenter)
        usage_layout.setContentsMargins(20, 0, 0, 0)  # left, top, right, bottom

        usage_title = QLabel("Literature Using the Method")
        usage_title.setObjectName("litTitle")
        usage_title.setAlignment(Qt.AlignCenter)
        usage_layout.addWidget(usage_title)

        usage_frame = QFrame()
        usage_frame.setObjectName("litBox")
        usage_frame.setFrameShape(QFrame.StyledPanel)
        usage_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        usage_frame_layout = QVBoxLayout(usage_frame)
        usage_frame_layout.setContentsMargins(10, 10, 10, 10)  # smaller internal margins
        usage_frame_layout.setSpacing(5)
        usage_frame_layout.setAlignment(Qt.AlignTop)

        usage_browser = QTextBrowser()
        usage_browser.setOpenExternalLinks(True)
        usage_browser.setHtml(self.generate_literature_list([
            ("Sox & al: Medical Decision Making", None),
            ("Temp & al: How Bayesian statistics may help answer some of the controversial questions in clinical research on Alzheimer's disease", None),
            ("Antoniano-Villalobos & al: A Bayesian Nonparametric Regression Model With Normalized Weights", None),
            ("Andersson & Moser & Moser: Visual stimulus features that elicit activity in object-vector cells", "http://doi.org/10.1038/s42003-021-02727-5"),
            ("Sidebotham: Are most randomised trials in anaesthesia and critical care wrong?", "http://doi.org/10.1111/anae.15029"),
            ("Ruberg & al: Inference and Decision Making for 21st-Century Drug Development and Approval", "http://doi.org/10.1080/00031305.2019.1566091"),
            ("Porta Mana & al: Personalized prognosis & treatment using an optimal predictor machine", "http://doi.org/10.31219/osf.io/8nr56"),
            ("Event Horizon Telescope Collaboration: First M87 Event Horizon Telescope Results", "http://doi.org/10.3847/2041-8213/ab0ec7"),
            ("Event Horizon Telescope Collaboration: First Sagittarius-A Event Horizon Telescope Results", "http://doi.org/10.3847/2041-8213/ac6674")
        ]))
        usage_frame_layout.addWidget(usage_browser)
        usage_layout.addWidget(usage_frame)
        content_layout.addLayout(usage_layout)

        layout.addLayout(content_layout)
        self.setLayout(layout)

        # Apply the stylesheet
        with importlib.resources.open_text('pages.shared', 'styles.qss') as f:
            common_style = f.read()

        with importlib.resources.open_text('pages.literature', 'styles.qss') as f:
            page_style = f.read()
            
        self.setStyleSheet(common_style + page_style)


    def generate_literature_list(self, references):
        """Generate HTML for a numbered list of literature references."""
        html = "<ol>"
        for title, link in references:
            if link:
                html += f'<li style="margin-bottom: 10px;">{title} <a href="{link}" style="color:blue;">(link)</a></li>'
            else:
                html += f'<li style="margin-bottom: 10px;">{title}</li>'
        html += "</ol>"
        return html
