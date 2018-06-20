import zipfile
from workflows.extractions.standards.zip.zip_utils import create_zip_folder

def extract(source_path):

    zfile = zipfile.ZipFile(source_path)

    folderpath = create_zip_folder(source_path)

    for name in zfile.namelist():
        zfile.extract(name, folderpath)

    return folderpath
