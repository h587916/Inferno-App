import numpy as np
from PySide6.QtWidgets import QMessageBox, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.interpolate import make_interp_spline

def plot_pr_probabilities(self):
    """Plot the probabilities and uncertainty for multiple variables."""
    clear_plot(self)

    figure = Figure()
    ax = figure.add_subplot(111)
    self.plot_canvas = FigureCanvas(figure)
    self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.plot_layout.insertWidget(1, self.plot_canvas)
    
    probabilities_values = np.array(self.probabilities_values)
    probabilities_quantiles = np.array(self.probabilities_quantiles)

    probabilities_values = fix_prob_shape(probabilities_values)
    probabilities_quantiles = fix_quantiles_shape(probabilities_quantiles)

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

        # If 3D => (nPoints, nVars, nQuantiles):
        if probabilities_quantiles.ndim == 3:
            lower_quantiles = probabilities_quantiles[:, i, 0]
            upper_quantiles = probabilities_quantiles[:, i, -1]
        # If 2D => (nPoints, nQuantiles):
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

def fix_prob_shape(probs):
    """Ensure shape is (nPoints, nVars)."""
    if probs.ndim == 1:
        # e.g. shape (nPoints,); reshape to (nPoints, 1)
        return probs.reshape(-1, 1)
    elif probs.ndim == 2:
        n0, n1 = probs.shape
        # If n0 < n1 but x_values has length n1, transpose:
        if n0 < n1:
            return probs.T
        else:
            return probs
    # If higher dims, assume already correct or raise error if needed
    return probs

def fix_quantiles_shape(q):
    """Ensure shape is (nPoints, nVars, nQuantiles). For instance, if shape is (nVars, nPoints, 2) -> we need (nPoints, nVars, 2)."""
    if q.ndim == 2:
        # e.g. shape (nPoints, 2) => (nPoints, 1, 2)
        n0, n1 = q.shape
        return q.reshape(n0, 1, n1)
    elif q.ndim == 3:
        n0, n1, n2 = q.shape
        # If n0 < n1 but matches x_values length => transpose first two axes
        if n0 < n1:
            return np.transpose(q, (1, 0, 2))
        else:
            return q
    return q

def plot_tailpr_probabilities(self):
    """Plot cumulative probabilities and quantiles for tailPr."""
    clear_plot(self)

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
    clear_plot(self)

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

def clear_plot(self):
    """Clear the plot from the canvas."""
    try:
        if self.plot_canvas is not None:
            self.plot_layout.removeWidget(self.plot_canvas)
            self.plot_canvas.deleteLater()
            self.plot_canvas = None
    except Exception:
        pass