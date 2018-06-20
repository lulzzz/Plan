import os
import sys

import numpy as np
import pandas as pd
import openpyxl

from django.conf import settings as cp

from workflows.core import os_utils


def extract(source_path):
    r"""
    Convert a source file into a df.
    Works for XLSX and XLS.

    input:
        source_path: the source path of the file.

    output:
        output_df: newly created df containing the source data.

    raises:
    """
    sheet_name = cp.TEMP_SHEET_NAME

    # if sheet_name is not provided
    if not sheet_name:
        # Get spreadsheet names
        wb = openpyxl.load_workbook(filename=source_path, read_only=True)
        spreadsheet_list = wb.sheetnames

        # if only 1 spreadsheet
        if len(spreadsheet_list) == 1:
            cp.TEMP_SHEET_NAME = spreadsheet_list[0]
            return pd.read_excel(source_path)

        # if multiple spreadsheets
        elif len(spreadsheet_list) > 1:
            print('Available spreadsheets:')

            spreadsheet_index = 0
            for idx, spreadsheet in enumerate(spreadsheet_list):
                print(idx, '"' + spreadsheet + '"')

            while True:
                spreadsheet_index = input('Select spreadsheet index: ')
                try:
                    spreadsheet_index_int = int(spreadsheet_index)
                except ValueError:
                    spreadsheet_index_int = -1

                if spreadsheet_index_int >= 0 and spreadsheet_index_int <= len(spreadsheet_list):
                    sheet_name = spreadsheet_index_int
                    cp.TEMP_SHEET_NAME = spreadsheet_list[spreadsheet_index_int]
                    break

    print('Selected spreadsheet', '"' + cp.TEMP_SHEET_NAME + '"')
    output_df = pd.read_excel(source_path, sheet_name=sheet_name)
    return output_df
