import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri


inferno = importr('inferno')

def build_metadata(csv_file_path, output_file_name):
    pandas2ri.activate()
    
    data = pd.read_csv(csv_file_path)
    r_data = pandas2ri.py2rpy(data)
    inferno.metadatatemplate(data=r_data, file=output_file_name)

    pandas2ri.deactivate()

    return output_file_name