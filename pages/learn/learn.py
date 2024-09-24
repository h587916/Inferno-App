import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import StrVector

# Import the 'inferno' R package
inferno = importr('inferno')

def run_learn(metadatafile: str, datafile: str, outputdir: str, seed: int, parallel: int):
    try:
        # Convert file paths to R string vectors
        metadatafile_r = StrVector([metadatafile])
        datafile_r = StrVector([datafile])

        # Call the 'learn' function from the Inferno package
        result = inferno.learn(data=datafile_r, metadata=metadatafile_r, outputdir=outputdir, seed=seed, parallel=parallel, appendtimestamp=False, appendinfo=False)

        print(f"Learning completed successfully. Results saved to {outputdir}.")
        return result

    except Exception as e:
        print(f"An error occurred while running the 'learn' function: {str(e)}")
        return None
