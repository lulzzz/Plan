import sys
import os

# Navigate to Django root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.path[0]))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.projects.settings_ess.project")
from django.conf import settings as cp

from workflows.core import os_utils
from workflows.core import df_utils


# Perform series of tests using generic data workflow functions
filename_dict = os_utils.get_file_properties(
    folder=cp.INPUT_DIRECTORY,
    result_format='abs_path_dict',
    startswith='sales',
    extension_list=['xlsx'],
)

base_filename = 'sales-jan-2014'
sales_df_base = df_utils.create_df_from_source_file(filename_dict[base_filename])
del filename_dict[base_filename]

for k, v in filename_dict.items():
    print('\nAnalyzing', k)
    sales_df_new = df_utils.create_df_from_source_file(v)
    sales_df_base = df_utils.append_two_df(sales_df_base, sales_df_new)

tgt_excel = os.path.join(cp.OUTPUT_DIRECTORY, 'sales.xlsx')
df_utils.export_df_to_excel(sales_df_base, tgt_excel)
