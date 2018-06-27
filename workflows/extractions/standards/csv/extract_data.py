import pandas as pd
from workflows.core import os_utils
import csv

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

def extract_long(source_path):
    chunksize = 10 ** 6
    for chunk in pd.read_csv(source_path, chunksize=chunksize):
        yield chunk

# def extract_long(source_path):
#     delimiter = os_utils.find_delimiter(source_path)
#     return pd.DataFrame(csv_reader(source_path, delimiter))
#
# def csv_reader(source_path, delimiter=','):
#     with open(source_path, "r") as csvfile:
#         datareader = csv.reader(csvfile, delimiter=delimiter)
#         for row in datareader:
#             yield row
