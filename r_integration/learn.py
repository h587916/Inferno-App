import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import StrVector

# Import the 'inferno' R package
inferno = importr('inferno')

def run_learn(metadatafile: str, datafile: str, outputdir: str, seed: int, parallel: int):
    """
    Runs the 'learn' function from the Inferno R package with the provided metadata and data files.

    Args:
        metadatafile (str): Path to the metadata CSV file.
        datafile (str): Path to the data CSV file.
        outputdir (str): The directory where the results should be saved.
        seed (int): Random seed for reproducibility.
        parallel (int): Number of parallel processes to use.

    Returns:
        result: The result object returned by the 'learn' function in Inferno.
    """
    
    try:
        # Convert file paths to R string vectors
        metadatafile_r = StrVector([metadatafile])
        datafile_r = StrVector([datafile])

        # Call the 'learn' function from the Inferno package
        result = inferno.learn(data=datafile_r, metadata=metadatafile_r, outputdir=outputdir, seed=seed, parallel=parallel)

        print(f"Learning completed successfully. Results saved to {outputdir}.")
        return result

    except Exception as e:
        print(f"An error occurred while running the 'learn' function: {str(e)}")
        return None
