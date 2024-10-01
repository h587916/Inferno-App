import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri, StrVector
from rpy2 import rinterface
import os
import shutil
import logging

inferno = importr('inferno')

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


def run_Pr(Y: pd.DataFrame, learnt_dir: str, X: pd.DataFrame = None, quantiles=[0.055, 0.25, 0.75, 0.945], nsamples=100):
    try:
        pandas2ri.activate()

        # Convert the DataFrames to R objects
        r_Y = pandas2ri.py2rpy(Y)
        r_X = pandas2ri.py2rpy(X) if X is not None else None
        learnt_r = StrVector([learnt_dir])

        # Call the Pr() function from Inferno with default parallelism and memory handling
        result = inferno.Pr(
            Y=r_Y,
            X=r_X,
            learnt=learnt_r,
            quantiles=quantiles,
            nsamples=nsamples,
            parallel=True, 
            silent=True, 
            usememory=True,
            keepYX=True  
        )

        return result

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

        # Call the tailPr() function from Inferno with default parallelism and memory handling
        result = inferno.tailPr(
            Y=r_Y,
            X=r_X,
            learnt=learnt_r,
            quantiles=quantiles,
            nsamples=nsamples,
            parallel=True,
            lower_tail=True,
            silent=True,
            usememory=True,
            keepYX=True
        )

        return result

    except Exception as e:
        logging.error(f"An error occurred while running the 'run_tailPr' function: {str(e)}")
        return None

    finally:
        pandas2ri.deactivate()



def run_mutualinfo(Y1names: list, learnt_dir: str, Y2names: list = None, X: pd.DataFrame = None, nsamples: int = 3600, unit: str = "Sh"):
    try:
        pandas2ri.activate()

        # Convert inputs to R objects
        Y1names_r = StrVector(Y1names)
        Y2names_r = StrVector(Y2names) if Y2names else rinterface.NULL
        r_X = pandas2ri.py2rpy(X) if X else rinterface.NULL
        learnt_r = StrVector([learnt_dir])

        # Call the mutualinfo() function from Inferno with default parallelism and memory handling
        result = inferno.mutualinfo(
            Y1names=Y1names_r,
            Y2names=Y2names_r,
            X=r_X,
            learnt=learnt_r,
            nsamples=nsamples,
            unit=unit,
            parallel=True, 
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


def run_flexiplot():
    return


def run_plotquantiles():
    return


def run_plotFsamples():
    return

