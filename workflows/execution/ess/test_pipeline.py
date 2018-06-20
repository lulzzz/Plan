import sys
import os

# Navigate to Django root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.path[0]))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.projects.settings_ess.project")
from django.conf import settings as cp

from workflows.core import os_utils
from workflows.core import df_utils
from workflows.extractions.standards.core import pipeline


r"""
Module 1: scan any file located in a defined folder.
i. The system will create a list of all files that are located in a specified folder
ii. The supported file formats will be CSV, XLSX, XLS, JSON, XML, TXT, PDF, ODS, HTML, DAT, ZIP, RAR, TAR, SQL and LOG.
iii. The system will list a maximum of 100 files and will be able to tell which files have already been integrated and which ones are new.
"""

# Scan for RAR, ZIP and TAR files for extracting the content
filename_dict = os_utils.get_file_properties(
    folder=cp.INPUT_DIRECTORY,
    result_format='file_property_dict',
    extension_list=['zip', 'rar', 'tar'],
)

filename_dict = pipeline.s01_extract_from_packaged_files(filename_dict)

# Scan for source files that are in the allowed extraction formats
filename_dict.update(
    os_utils.get_file_properties(
        folder=cp.INPUT_DIRECTORY,
        result_format='file_property_dict',
        # startswith='PDAS_FTW_VANS_BULK_CASA_NTB',
        extension_list=['xlsx', 'csv', 'xls', 'json', 'xml', 'txt', 'pdf', 'ods', 'html', 'dat', 'sql', 'log'],
    )
)

# Load extracts into the database and record metadata
pipeline.s01_load_extracts(
    filename_dict,
    add_rules=True,
    delete_rules=True,
    add_keys=True,
    reload=True,
)
