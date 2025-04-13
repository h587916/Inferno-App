import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri, StrVector, FloatVector
from rpy2 import rinterface
import os
import shutil
import subprocess
import platform


inferno = importr('inferno')

def run_learn_in_terminal(data_path, metadata_path, output_dir, nsamples=3600, nchains=60, maxhours="Inf", parallel="No", seed=None):
    os.makedirs(output_dir, exist_ok=True)
    r_script_path = os.path.join(output_dir, "run_learn_script.R")

    data_path_r = os.path.normpath(data_path).replace("\\", "/")
    metadata_path_r = os.path.normpath(metadata_path).replace("\\", "/")
    output_dir_r = os.path.normpath(output_dir).replace("\\", "/")

    if maxhours == float("inf") or str(maxhours).lower() == "inf":
        maxhours_r = "Inf"
    else:
        maxhours_r = str(maxhours)

    if parallel == "No":
        parallel_r = "FALSE"
    else:
        parallel_r = int(parallel)
  
    r_lines = [
        "library(inferno)",
        f"set.seed({seed})" if seed else "",
        "",
        'cat("Running the learn() function:\\n\\n")',
        'cat("inferno::learn(\\n")',
        f'cat("  data = \\"{data_path_r}\\",\\n")',
        f'cat("  metadata = \\"{metadata_path_r}\\",\\n")',
        f'cat("  outputdir = \\"{output_dir_r}\\",\\n")',
        f'cat("  nsamples = {nsamples},\\n")',
        f'cat("  nchains = {nchains},\\n")',
        f'cat("  maxhours = {maxhours_r},\\n")',
        f'cat("  parallel = {parallel_r},\\n")',
        f'cat("  seed = {seed},\\n")' if seed else "None",
        'cat("  appendtimestamp = FALSE,\\n")',
        'cat("  appendinfo = FALSE,\\n")',
        'cat("  output = \\"directory\\",\\n")',
        'cat("  plottraces = FALSE\\n")',
        'cat(")\\n\\n")',
        '',
        'inferno::learn(',
        f'  data = "{data_path_r}",',
        f'  metadata = "{metadata_path_r}",',
        f'  outputdir = "{output_dir_r}",',
        f'  nsamples = {nsamples},',
        f'  nchains = {nchains},',
        f'  maxhours = {maxhours_r},',
        f'  seed = {seed},' if seed else "",
        f'  parallel = {parallel_r},',
        f'  appendtimestamp = FALSE,',
        f'  appendinfo = FALSE,',
        f'  output = "directory",',
        f'  plottraces = FALSE',
        ')',
        'cat("\\n-----------------------------------------\\n\\n")',
        'cat("Monte Carlo Computation ran successfully!\\n")',
        'cat("You can now close the terminal and return to the app.\\n")',
        'cat("\\n-----------------------------------------\\n")'
    ]
    r_script = "\n".join([line for line in r_lines if line.strip() != ""])

    with open(r_script_path, 'w') as f:
        f.write(r_script)

    command = f'Rscript "{r_script_path}"'

    try:
        current_platform = platform.system()

        if current_platform == "Windows":
            command = f'Rscript "{r_script_path}"'
            subprocess.Popen(f'start cmd.exe /k "{command}"', shell=True)

        elif current_platform == "Darwin":
            apple_script = f'''tell application "Terminal"
                activate
                do script "Rscript \\"{r_script_path}\\""
            end tell'''
            subprocess.Popen(["osascript", "-e", apple_script])

        elif current_platform == "Linux":
            subprocess.Popen(["gnome-terminal", "--", "Rscript", r_script_path])

        else:
            return False, f"Unsupported platform: {current_platform}"
        
        return True, f"Launched R script in terminal."
    except Exception as e:
        return False, str(e)

def run_learn(metadatafile, datafile, outputdir, nsamples=3600, nchains=60, maxhours="Inf", seed=None, parallel="No"):
    try:
        metadatafile_r = StrVector([metadatafile])
        datafile_r = StrVector([datafile])

        if parallel == "No":
            parallel_r = False
        else:
            parallel_r = int(parallel)

        learn_args = {
            "data": datafile_r,
            "metadata": metadatafile_r,
            "outputdir": outputdir,
            "nsamples": nsamples,
            "nchains": nchains,
            "maxhours": maxhours,
            "appendtimestamp": False,
            "appendinfo": False,
            "plottraces": False,
            "parallel": parallel_r
        }

        if seed is not None:
            learn_args["seed"] = seed

        result = inferno.learn(**learn_args)
        return result

    except Exception as e:
        if os.path.exists(outputdir):
            try:
                shutil.rmtree(outputdir)
            except OSError as delete_error:
                raise delete_error
        raise e


def build_metadata(csv_file_path, output_file_name, includevrt=None, excludevrt=None):
    try:
        pandas2ri.activate()

        data = pd.read_csv(csv_file_path)
        r_data = pandas2ri.py2rpy(data)

        includevrt_r = StrVector(includevrt) if includevrt is not None else rinterface.NULL
        excludevrt_r = StrVector(excludevrt) if excludevrt is not None else rinterface.NULL

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
        raise e

    finally:
        pandas2ri.deactivate()


def run_Pr(Y: pd.DataFrame, learnt_dir: str, X: pd.DataFrame = None, quantiles = [0.055, 0.945], nsamples: int = 100, parallel: int = 12):
    try:
        pandas2ri.activate()

        r_Y = pandas2ri.py2rpy(Y)
        r_X = pandas2ri.py2rpy(X) if X is not None and not X.empty else rinterface.NULL
        learnt_r = StrVector([learnt_dir])
        quantiles_r = FloatVector(quantiles)

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
            return None

    except Exception as e:
        raise e

    finally:
        pandas2ri.deactivate()


def run_tailPr(Y: pd.DataFrame, learnt_dir: str, eq: bool, lower_tail: bool, X: pd.DataFrame = None, quantiles = [0.055, 0.945], nsamples: int = 100, parallel: int = 12):
    try:
        pandas2ri.activate()

        r_Y = pandas2ri.py2rpy(Y)
        r_X = pandas2ri.py2rpy(X) if X is not None and not X.empty else rinterface.NULL
        learnt_r = StrVector([learnt_dir])
        quantiles_r = FloatVector(quantiles)

        probabilities = inferno.tailPr(
            Y=r_Y,
            X=r_X,
            learnt=learnt_r,
            nsamples=nsamples,
            parallel=parallel,
            quantiles=quantiles_r,
            eq=eq,
            **{'lower.tail': lower_tail}
        )
        if probabilities:
            values = probabilities.rx2('values')
            quantiles = probabilities.rx2('quantiles')
            return values, quantiles
        else:
            return None

    except Exception as e:
        raise e 

    finally:
        pandas2ri.deactivate()



def run_mutualinfo(predictor: list, learnt_dir: str, additional_predictor: list = None, predictand: pd.DataFrame = None, nsamples: int = 3600, unit: str = "Sh", parallel: int = 1):
    try:
        pandas2ri.activate()

        Y1names_r = StrVector(predictor)
        Y2names_r = StrVector(additional_predictor) if additional_predictor else rinterface.NULL
        r_X = pandas2ri.py2rpy(predictand) if predictand is not None and not predictand.empty else rinterface.NULL
        learnt_r = StrVector([learnt_dir])

        result = inferno.mutualinfo(
            Y1names=Y1names_r,
            Y2names=Y2names_r,
            X=r_X,
            learnt=learnt_r,
            nsamples=nsamples,
            unit=unit,
            parallel=parallel, 
            silent=True
        )

        return result

    except Exception as e:
        raise e

    finally:
        pandas2ri.deactivate()