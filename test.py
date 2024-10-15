import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import logging
from rpy2.robjects import r, pandas2ri, rinterface
from rpy2.robjects.vectors import StrVector, FloatVector
from rpy2.robjects.packages import importr

# Load the learnt model output (assuming this is some saved probabilistic model)
learnt = 'files/learnt/toydata'

# Load inferno
inferno = importr('inferno')

# Function to run Pr using the provided run_Pr function
def run_Pr(Y: pd.DataFrame, learnt_dir: str, X: pd.DataFrame = None, quantiles=[0.055, 0.25, 0.75, 0.945], nsamples: int = 100, parallel: int = 12):
    try:
        pandas2ri.activate()

        # Convert the DataFrames to R objects
        r_Y = pandas2ri.py2rpy(Y)
        r_X = pandas2ri.py2rpy(X) if X is not None and not X.empty else rinterface.NUL
        learnt_r = StrVector([learnt_dir])
        quantiles_r = FloatVector(quantiles)

        # Call the Pr() function from Inferno with default parallelism and memory handling
        probabilities = inferno.Pr(
            Y=r_Y,
            X=r_X,
            learnt=learnt_r,
            nsamples=nsamples,
            parallel=parallel,
            quantiles=quantiles_r
        )
        if probabilities:
            values = probabilities.rx2('values')
            quantiles = probabilities.rx2('quantiles')
            return values, quantiles
        else:
            logging.error("The Pr function did not return any results.")
            return None

    except Exception as e:
        logging.error(f"An error occurred while running the 'run_Pr' function: {str(e)}")
        return None

    finally:
        pandas2ri.deactivate()


# Function to plot the probabilities and quantiles
def plot_probabilities(Y_values, probabilities_values, probabilities_quantiles):
    # Convert R objects back to numpy arrays for plotting
    probabilities_values = np.array(probabilities_values).flatten()
    probabilities_quantiles = np.array(probabilities_quantiles)

    # Ensure quantiles array is correctly shaped for plotting
    if probabilities_quantiles.ndim == 3:
        lower_quantiles = probabilities_quantiles[:, 0, 0]
        upper_quantiles = probabilities_quantiles[:, 0, -1]
    elif probabilities_quantiles.ndim == 2 and probabilities_quantiles.shape[1] >= 2:
        lower_quantiles = probabilities_quantiles[:, 0]
        upper_quantiles = probabilities_quantiles[:, -1]
    else:
        logging.error("Unexpected shape of quantiles array.")
        lower_quantiles = np.zeros(Y_values.shape[0])
        upper_quantiles = np.zeros(Y_values.shape[0])

    # Personalized plot
    # Plot the quantiles with a customized appearance
    plt.fill_between(
        Y_values['diff.MDS.UPRS.III'], 
        lower_quantiles, 
        upper_quantiles,
        color='skyblue', 
        alpha=0.5, 
        edgecolor='darkblue', 
        linewidth=2,
        label='Uncertainty (Quantiles)'
    )

    plt.ylim(0, None)
    plt.xlabel('MDS-UPDRS-III difference')
    plt.ylabel('Probability')

    # Overlay the probability distribution curve
    # Interpolate to make the plot look smoother
    spl = make_interp_spline(Y_values['diff.MDS.UPRS.III'], probabilities_values, k=3)
    Y_smooth = np.linspace(Y_values['diff.MDS.UPRS.III'].min(), Y_values['diff.MDS.UPRS.III'].max(), 500)
    prob_smooth = spl(Y_smooth)

    plt.plot(Y_smooth, prob_smooth, color='red', linewidth=2, linestyle='-', label='Probability')

    # Add the 0-change line
    plt.axvline(x=0, color='blue', linestyle='--', linewidth=2, label='0-change Line')

    # Add legend to explain the components of the plot
    plt.legend()

    plt.show()

# OPTION 1

# Using the run_Pr function where the Y variate has a range of values
Y_values = pd.DataFrame({'diff.MDS.UPRS.III': np.arange(-30, 31)})
X_values = pd.DataFrame({'Sex': ['Female'], 'TreatmentGroup': ['NR']})
probabilities_values, probabilities_quantiles = run_Pr(Y=Y_values, X=X_values, learnt_dir=learnt)

if probabilities_values is not None and probabilities_quantiles is not None:
    plot_probabilities(Y_values, probabilities_values, probabilities_quantiles)
else:
    logging.error("Failed to obtain probabilities from the run_Pr function.")