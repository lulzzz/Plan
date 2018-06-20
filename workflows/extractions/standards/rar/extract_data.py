import os
from pyunpack import Archive
import pandas as pd
from workflows.extractions.standards.zip.zip_utils import create_zip_folder

def extract(source_path):
    folderpath = create_zip_folder(source_path)
    os.chdir(folderpath)
    Archive(source_path).extractall(folderpath)
    return folderpath
