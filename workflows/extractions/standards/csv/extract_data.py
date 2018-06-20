import pandas as pd
from workflows.core import os_utils

def extract(source_path):
    delimiter = os_utils.find_delimiter(source_path)
    return pd.read_csv(
        source_path,
        sep=delimiter,
        error_bad_lines=False,
        encoding='latin-1',
        low_memory=False,
        warn_bad_lines=False
    )
