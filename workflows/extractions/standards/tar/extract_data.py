import os
import tarfile
from workflows.extractions.standards.zip.zip_utils import create_zip_folder

def extract(source_path):
    tar = tarfile.open(source_path)
    folderpath = create_zip_folder(source_path)
    os.chdir(folderpath)
    tar.extractall()
    tar.close()
    return folderpath
