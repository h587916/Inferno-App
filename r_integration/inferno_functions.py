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
        print(f"An error occurred while building the metadata: {str(e)}")
        return None

    finally:
        pandas2ri.deactivate()


def run_learn(metadatafile: str, datafile: str, outputdir: str, nsamples: int = 3600, nchains: int = 60, maxhours: float = float('inf'), parallel: int = None, seed: int = None):
    try:
       # Convert file paths to R string vectors
        metadatafile_r = StrVector([metadatafile])
        datafile_r = StrVector([datafile])

        learn_args = {
            "data": datafile_r,
            "metadata": metadatafile_r,
            "outputdir": outputdir,
            "nsamples": nsamples,
            "nchains": nchains,
            "maxhours": maxhours,
            "appendtimestamp": False,
            "appendinfo": False,
            "plottraces": False
        }

        if parallel is not None:
            learn_args["parallel"] = parallel
        if seed is not None:
            learn_args["seed"] = seed

        result = inferno.learn(**learn_args)
        return result

    except Exception as e:
        print(f"An error occurred while running the 'run_learn' function in r_integration/inferno_functions.py: {str(e)}")
        
        # Clean up: Delete the output folder if it was created
        if os.path.exists(outputdir):
            try:
                shutil.rmtree(outputdir)
            except OSError as delete_error:
                print(f"Failed to delete directory {outputdir}: {delete_error}")

        return None


def run_Pr(Y: pd.DataFrame, learnt_dir: str, X: pd.DataFrame = None, quantiles = [0.055, 0.25, 0.75, 0.945], nsamples: int = 100, parallel: int = 12):
    try:
        pandas2ri.activate()

        # Convert the DataFrames to R objects
        r_Y = pandas2ri.py2rpy(Y)
        r_X = pandas2ri.py2rpy(X) if X is not None and not X.empty else rinterface.NULL
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
            print("The Pr function did not return any results.")
            return None

    except Exception as e:
        print(f"An error occurred while running the 'run_Pr' function: {str(e)}")
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
        print(f"An error occurred while running the 'run_tailPr' function: {str(e)}")
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
        print(f"An error occurred while running the 'run_mutualinfo' function: {str(e)}")
        return None

    finally:
        pandas2ri.deactivate()
