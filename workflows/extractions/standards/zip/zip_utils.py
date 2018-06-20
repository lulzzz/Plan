import zipfile
import os

def zip_files(file_list, output_file, mode='a'):
    # Prepare zip file
    zip = zipfile.ZipFile(output_file, mode)

    # Check existing content
    existing_file_list = list()
    if os.path.isfile(output_file):
        existing_file_list = zip.namelist()

    # Append to zip file
    for f in file_list:
        base_file = os.path.basename(f)
        if base_file not in existing_file_list:
            zip.write(f, base_file, compress_type=zipfile.ZIP_DEFLATED)

    zip.close()

def create_zip_folder(filename):
    # Create new folder to unzip file
    dirname = os.path.dirname(filename)
    foldername = os.path.splitext(os.path.basename(filename))[0]
    folderpath = os.path.join(dirname, foldername)

    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

    return folderpath
