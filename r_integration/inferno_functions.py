import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri, StrVector, FloatVector
from rpy2 import rinterface
import os
import shutil
import logging
import numpy as np
from rpy2.robjects import r

inferno = importr('inferno')
grdevices = importr('grDevices')

logging.basicConfig(
    level=logging.ERROR,
    filename='logs/inferno.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def build_metadata(csv_file_path, output_file_name, includevrt=None, excludevrt=None):
    try:
        pandas2ri.activate()

        # Read the CSV data
        data = pd.read_csv(csv_file_path)
        r_data = pandas2ri.py2rpy(data)

        # Convert variables to R vectors if provided
        includevrt_r = StrVector(includevrt) if includevrt is not None else rinterface.NULL
        excludevrt_r = StrVector(excludevrt) if excludevrt is not None else rinterface.NULL

        # Call the metadatatemplate function from inferno package
        inferno.metadatatemplate(
            data=r_data,
            file=output_file_name,
            includevrt=includevrt_r,
            excludevrt=excludevrt_r,
            addsummary2metadata=False,
            backupfiles=False,
            verbose=False
        )

        return output_file_name

    except Exception as e:
        logging.error(f"An error occurred while building the metadata: {str(e)}")
        return None

    finally:
        pandas2ri.deactivate()


def run_learn(metadatafile: str, datafile: str, outputdir: str, nsamples: int = 3600, nchains: int = 60, maxhours: float = float('inf'), parallel: int = 4):
    try:
       # Convert file paths to R string vectors
        metadatafile_r = StrVector([metadatafile])
        datafile_r = StrVector([datafile])

        # Call the 'learn' function from the inferno package with the selected parameters
        result = inferno.learn(
            data=datafile_r,
            metadata=metadatafile_r,
            outputdir=outputdir,
            nsamples=nsamples,
            nchains=nchains,
            maxhours=maxhours,
            parallel=parallel,
            seed=16,
            appendtimestamp=False,  
            appendinfo=False,  
            plottraces=False 
        )
        return result

    except Exception as e:
        logging.error(f"An error occurred while running the 'run_learn' function in r_integration/inferno_functions.py: {str(e)}")
        
        # Clean up: Delete the output folder if it was created
        if os.path.exists(outputdir):
            try:
                shutil.rmtree(outputdir)
            except OSError as delete_error:
                logging.error(f"Failed to delete directory {outputdir}: {delete_error}")

        return None


def run_Pr(Y: pd.DataFrame, learnt_dir: str, X: pd.DataFrame = None, quantiles = [0.055, 0.25, 0.75, 0.945], nsamples: int = 100, parallel: int = 12):
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


def run_tailPr(Y: pd.DataFrame, learnt_dir: str, X: pd.DataFrame = None, quantiles=[0.055, 0.25, 0.75, 0.945], nsamples=100):
    try:
        pandas2ri.activate()

        # Convert DataFrames to R objects
        r_Y = pandas2ri.py2rpy(Y)
        r_X = pandas2ri.py2rpy(X) if X else rinterface.NULL
        learnt_r = StrVector([learnt_dir])
        quantiles_r = FloatVector(quantiles)

        # Call the tailPr() function from Inferno with default parallelism and memory handling
        probabilities = inferno.tailPr(
            Y=r_Y,
            X=r_X,
            learnt=learnt_r,
            quantiles=quantiles_r,
            nsamples=nsamples,
            parallel=True,
            lower_tail=True,
            silent=True,
            usememory=True,
            keepYX=True
        )
        return probabilities

    except Exception as e:
        logging.error(f"An error occurred while running the 'run_tailPr' function: {str(e)}")
        return None

    finally:
        pandas2ri.deactivate()



def run_mutualinfo(predictor: list, learnt_dir: str, additional_predictor: list = None, predictand: pd.DataFrame = None, nsamples: int = 3600, unit: str = "Sh", paralell: int = 12):
    try:
        pandas2ri.activate()

        # Convert inputs to R objects
        Y1names_r = StrVector(predictor)
        Y2names_r = StrVector(additional_predictor) if additional_predictor else rinterface.NULL
        r_X = pandas2ri.py2rpy(predictand) if predictand is not None and not predictand.empty else rinterface.NULL
        learnt_r = StrVector([learnt_dir])

        # Call the mutualinfo() function from Inferno with default parallelism and memory handling
        result = inferno.mutualinfo(
            Y1names=Y1names_r,
            Y2names=Y2names_r,
            X=r_X,
            learnt=learnt_r,
            nsamples=nsamples,
            unit=unit,
            parallel=paralell, 
            silent=True
        )

        return result

    except Exception as e:
        logging.error(f"An error occurred while running the 'run_mutualinfo' function: {str(e)}")
        return None

    finally:
        pandas2ri.deactivate()



def run_E():
    return


def plot_probabilities_and_quantiles(Y, probabilities):
    """
    Use R's plotquantiles and flexiplot functions to plot quantiles and probabilities.
    """
    x_values = Y['diff.MDS.UPRS.III'].tolist()  # X-axis values

    # Extract quantiles and values from probabilities using rpy2
    quantiles_r = probabilities.rx2('quantiles')  # Extract R quantiles object
    prob_values_r = probabilities.rx2('values')  # Extract R probability values object

    # Convert R objects to NumPy arrays for checking and passing to R functions
    quantiles = np.array(quantiles_r)
    prob_values = np.array(prob_values_r)

    # Check if upper limit for ylim is None, and replace it with Inf for R
    y_max = None if quantiles is None else np.max(quantiles)
    y_max = y_max if y_max is not None else float('inf')  # Use infinity if None

    # Open an R graphics device (this will open a new window for plotting)
    grdevices.x11()  # or use windows() on Windows

    # Call R's plotquantiles function
    inferno.plotquantiles(
        x=FloatVector(x_values),
        y=quantiles,  # Pass quantiles as R object
        ylim=FloatVector([0, y_max]),  # Set y-axis limits with proper upper limit
        xlab='MDS-UPDRS-III difference',
        ylab='Probability',
        col=StrVector(['skyblue']),
        border=StrVector(['darkblue']),
        lwd=2,
        add=False  # Create a new plot
    )

    # Call R's flexiplot function to overlay the probability distribution curve
    inferno.flexiplot(
        x=FloatVector(x_values),
        y=prob_values,
        col=StrVector(['red']),
        lwd=2,
        lty=1,
        add=True  # Overlay on the existing plot
    )

    # Add 50%-probability line
    r('abline')(h=0.5, lwd=2, col="blue", lty=2)

    # Close the R device when done
    grdevices.dev_off()


def run_flexiplot(x: pd.Series, y: pd.Series, col='red', lwd=2, lty=1, add=True):
    try:
        # Activate rpy2 pandas support
        pandas2ri.activate()

        # Convert the x and y to R objects
        r_x = pandas2ri.py2rpy(x)
        r_y = pandas2ri.py2rpy(y)

        # Convert other parameters to R-compatible objects
        col_r = StrVector([col])
        add_r = rinterface.BoolSexpVector([add])

        # Call the flexiplot function
        inferno.flexiplot(
            x=r_x,
            y=r_y,
            col=col_r,
            lwd=lwd,
            lty=lty,
            add=add_r
        )

    except Exception as e:
        logging.error(f"An error occurred while running the 'run_flexiplot' function: {str(e)}")
        return None

    finally:
        pandas2ri.deactivate()


def run_plotquantiles(x: pd.Series, y: pd.DataFrame, ylim=(0, None), xlab='X-axis', ylab='Y-axis', col='skyblue', border='darkblue', lwd=2, add=False):
    try:
        # Activate rpy2 pandas support
        pandas2ri.activate()

        # Convert the x and y to R objects
        r_x = pandas2ri.py2rpy(x)
        r_y = pandas2ri.py2rpy(y)

        # Convert additional parameters to R-compatible types
        ylim_r = FloatVector(ylim)
        col_r = StrVector([col])
        border_r = StrVector([border])
        add_r = rinterface.BoolSexpVector([add])

        # Call the plotquantiles function
        inferno.plotquantiles(
            x=r_x,
            y=r_y,
            ylim=ylim_r,
            xlab=xlab,
            ylab=ylab,
            col=col_r,
            border=border_r,
            lwd=lwd,
            add=add_r
        )

    except Exception as e:
        logging.error(f"An error occurred while running the 'run_plotquantiles' function: {str(e)}")
        return None

    finally:
        pandas2ri.deactivate()


def run_plotFsamples():
    return

