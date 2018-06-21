import os
from os import walk
import sys
import re
import copy

import numpy as np
import pandas as pd
from sqlalchemy import types

from django.conf import settings as cp

from workflows.core import os_utils
from workflows.core import df_utils

from workflows.extractions.standards.excel import extract_data as extract_from_excel
from workflows.extractions.standards.csv import extract_data as extract_from_csv
from workflows.extractions.standards.html import extract_data as extract_from_html
from workflows.extractions.standards.json import extract_data as extract_from_json
from workflows.extractions.standards.ods import extract_data as extract_from_ods
from workflows.extractions.standards.pdf import extract_data as extract_from_pdf
from workflows.extractions.standards.xml import extract_data as extract_from_xml

def create_df_from_source_file(
    source_path=None,
):
    r"""
    Convert a source file into a df.

    input:
        source_path: the source path of the file.

    output:
        output_df: newly created df containing the source data.

    raises:
    """

    # Extract file
    extension = os_utils.get_file_extension(source_path, keep_dot=False)

    if extension in ('xlsx', 'xls'):
        output_df = extract_from_excel.extract(source_path)

    elif extension in ('txt', 'dat', 'log'):
        output_df = extract_from_csv.extract(source_path)

    elif extension in ('csv'):
        output_df = pd.concat(extract_from_csv.extract_long(source_path))

    elif extension in ('html'):
        output_df = extract_from_html.extract(source_path)

    elif extension in ('json'):
        output_df = extract_from_json.extract(source_path)

    elif extension in ('ods'):
        output_df = extract_from_ods.extract(source_path)

    elif extension in ('pdf'):
        output_df = extract_from_pdf.extract(source_path)
        print(output_df.head())

    elif extension in ('xml'):
        output_df = extract_from_xml.extract(source_path)

    else:
        print('Could not proceed the file format')
        return

    return output_df


def append_two_df(input_df_base, input_df_new, minimum_points=0.5):
    r"""
    Append new df to base df.
    The columns of base df are considered valid.
    The columns of the new df have to be renamed to match the base df.
    Append only if both dfs mapping is similar enough.

    input:
        source_path: the source path of the file

    output:
        output_df: newly created df containing the source data

    raises:
    """
    # Prepare df
    base_metadata = get_df_metadata(input_df_base)
    new_metadata = get_df_metadata(input_df_new)

    # Do base df to new df field mapping
    col_mapping_dict = get_two_df_column_mapping(base_metadata, new_metadata)
    col_mapping_dict_swap = {y:x for x, y in col_mapping_dict.items()}

    # Rename new df fields
    input_df_new = input_df_new.rename(columns=col_mapping_dict_swap)

    # Keep only fields for which a base table mapping was found
    new_metadata = get_df_metadata(input_df_new)
    valid_fields = [x for x in list(base_metadata.keys()) if x in list(new_metadata.keys())]
    input_df_new = input_df_new[valid_fields]

    # Cleanse data
    # @ todo!!!

    # Check if enough fields match
    if input_df_new.shape[1]/input_df_base.shape[1] > minimum_points:
        # Append new df to base df
        print('Appending')
        return input_df_base.append(input_df_new)[input_df_base.columns.tolist()]
    # Or return base df
    else:
        print('Skipping')
        return input_df_base



def get_two_df_column_mapping(base_metadata, new_metadata):
    r"""
    Compare new df and base df to find which columns should be mapped
    input:
        base_metadata: the source path of the file
        new_metadata:

    output:
        output_df: newly created df containing the source data
        False if mapping not good enough

    raises:
    """

    base_col_dict = dict()
    target_list = list(new_metadata.keys())

    remaining_fields = copy.copy(target_list)
    for base_key in base_metadata:

        # For filename column
        if base_key == cp.COLUMN_FILENAME:
            matching_field = base_key

        # For other columns
        else:
            # Mapping tests
            test_dict = {
                'test01_field_name': os_utils.rank_field_by_name(base_key, target_list),
                'test02_dtype': os_utils.rank_field_by_dtype(base_metadata[base_key].get('dtype'), new_metadata),
                'test03_position': os_utils.rank_field_by_position(base_metadata[base_key].get('position'), new_metadata),
                'test04_distinct_values': os_utils.rank_field_by_distinct_values(base_metadata[base_key].get('distinct_values'), new_metadata),
            }

            # Get best matching field
            matching_field = get_two_df_column_mapping_count_points(test_dict, remaining_fields)

        # If field returned, add to base_col_dict and remove from remaining_fields
        if matching_field:
            base_col_dict[base_key] = matching_field
            remaining_fields.remove(matching_field)

    return base_col_dict



def get_two_df_column_mapping_count_points(test_dict, remaining_fields, minimum_points=135):
    if len(remaining_fields) > 0:
        counter_dict = dict()

        for field in remaining_fields:
            counter_dict.setdefault(field, 0)

            # Iterate through tests
            for test_k, test_v in test_dict.items():
                # Iterate through test results
                for field_k, field_v in test_v.items():
                    if field_k == field:
                        counter_dict[field] += field_v

        counter_dict_max_key = max(counter_dict, key=counter_dict.get)
        if counter_dict[counter_dict_max_key] > minimum_points:
            return counter_dict_max_key

    return None


def convert_datetime_col(input_df):
    r"""
    Takes a dataframe input_df and converts every column with dtype object in datetime
    if the column values are in a DATETIME format like specified in cluster_params
    """
    output_df = input_df
    table_test = input_df.head(1000)
    for col in table_test.columns:
        if all(pd.isnull(table_test[col])):
            table_test = table_test.drop(col, 1)
    list_col_candidates = [col for col in table_test.columns if table_test[col].dtype == 'object' and
                           all(os_utils.is_datetime(str(l)) for l in table_test[col] if not pd.isnull(l))]
    dict_col_datetime = {col: 'datetime_{}'.format(os_utils.identify_date_format(input_df, col)) for col in list_col_candidates}
    list_col_datetimedateUS = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_DATE_US']
    list_col_datetimedateEU = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_DATE_EU']
    list_col_datetimedateISO = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_DATE_ISO']
    list_col_datetimemonthdate = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_MONTH_DATE']
    list_col_datetimemonthdateISO = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_MONTH_DATE_ISO']

    # apply conversion
    if list_col_datetimedateUS:
        output_df[list_col_datetimedateUS] = output_df[list_col_datetimedateUS].applymap(lambda x: os_utils.normalize_date_format(x))
        output_df[list_col_datetimedateUS] = output_df[list_col_datetimedateUS].apply(pd.to_datetime, format="%m%d%Y", errors='coerce')
    if list_col_datetimedateEU:
        output_df[list_col_datetimedateEU] = output_df[list_col_datetimedateEU].applymap(lambda x: os_utils.normalize_date_format(x))
        output_df[list_col_datetimedateEU] = output_df[list_col_datetimedateEU].apply(pd.to_datetime, format="%d%m%Y", errors='coerce')
    if list_col_datetimedateISO:
        output_df[list_col_datetimedateISO] = output_df[list_col_datetimedateISO].applymap(lambda x: os_utils.normalize_date_format(x))
        output_df[list_col_datetimedateISO] = output_df[list_col_datetimedateISO].apply(pd.to_datetime, format="%Y%m%d", errors='coerce')
    if list_col_datetimemonthdate:
        output_df[list_col_datetimemonthdate] = output_df[list_col_datetimemonthdate].applymap(lambda x: os_utils.normalize_date_format(x))
        output_df[list_col_datetimemonthdate] = output_df[list_col_datetimemonthdate].apply(pd.to_datetime, format="%d%m%Y", errors='coerce')
    if list_col_datetimemonthdateISO:
        output_df[list_col_datetimemonthdateISO] = output_df[list_col_datetimemonthdateISO].applymap(lambda x: os_utils.normalize_date_format(x))
        output_df[list_col_datetimemonthdateISO] = output_df[list_col_datetimemonthdateISO].apply(pd.to_datetime, format="%Y%m%d", errors='coerce')

    return output_df


def convert_object_col(input_df):
    r"""
    Takes a dataframe table and converts every column into object format.
    """
    table_test = input_df.head(1000)
    output_df = copy.deepcopy(input_df)
    for col in table_test.columns:
        if all(pd.isnull(table_test[col])):
            # table_test = table_test.drop(col, 1)
            del output_df[col]
    # Convert first to str (to avoid datetime64 database conversion issue)
    # for col in table_test.columns:

    # output_df = table_test.astype(str)
    # return output_df.astype(object)
    return output_df


def convert_numeric_col(table):
    r"""
    Takes a dataframe table and converts every column with dtype object in either float or integer
    if the column values are in a FORMAT_FLOAT or FORMAT_INT format like specified in parameters.
    """
    table_test = table.head(1000)
    for col in table_test.columns:
        if all(pd.isnull(table_test[col])):
            table_test = table_test.drop(col, 1)
    # look if majority is convertible
    list_col_float = []
    list_col_int = []
    for col in table_test.columns:
        if table_test[col].dtype == 'object':
            total_count = len([l for l in table_test[col] if not pd.isnull(l)])
            dict_count_format = {}
            dict_count_format['integer'] = sum([1 if os_utils.is_integer(l) else 0 for l in table_test[col] if not pd.isnull(l)]) / total_count
            dict_count_format['float'] = sum([1 if os_utils.is_float(l) else 0 for l in table_test[col] if not pd.isnull(l)]) / total_count
            max_format = max(dict_count_format, key=dict_count_format.get)
            if dict_count_format[max_format] < 0.80:
                continue
            else:
                if max_format == 'float':
                    list_col_float.append(col)
                else:
                    list_col_int.append(col)

    if list_col_int:
        table[list_col_int] = table[list_col_int].replace('-', np.NaN)
        table[list_col_int] = table[list_col_int].applymap(lambda x: os_utils.normalize_numeric_format(x))  # Decision to separate INT and FLOAT although same functions applied
        table[list_col_int] = table[list_col_int].apply(pd.to_numeric, errors='coerce')
    if list_col_float:
        table[list_col_float] = table[list_col_float].replace('-', np.NaN)
        table[list_col_float] = table[list_col_float].applymap(lambda x: os_utils.normalize_numeric_format(x))
        table[list_col_float] = table[list_col_float].apply(pd.to_numeric, errors='coerce')


def gen_types_from_pandas_to_sql(table):
    r"""
    Generate a dictionnary with the database types related to the dataframe dtypes
    """
    dtypedict = {}
    for i, j in zip(table.columns, table.dtypes):
        if 'object' in str(j):
            dtypedict.update({i: types.NVARCHAR(length=500)})
        if 'datetime' in str(j):
            dtypedict.update({i: types.DateTime()})
        if 'float' in str(j):
            dtypedict.update({i: types.Float(precision=3, asdecimal=True)})
            dtypedict.update({i: types.NVARCHAR(length=500)}) # Overwrite FG to avoid Out of range value for column issue
        if 'int' in str(j):
            if max(
                [l for l in table[i].tolist() if not pd.isnull(l)]
            ) > cp.INT_LIMIT:
                dtypedict.update({i: types.BIGINT()})
            else:
                dtypedict.update({i: types.INT()})
    return dtypedict


def get_df_metadata(input_df, distinct_values_limit=100):
    metadata_dict = dict()
    column_list = input_df.columns.values.tolist()
    for idx, col in enumerate(column_list):
        if isinstance(input_df[col], pd.Series):
            metadata_dict[col] = {
                'position': idx,
                'dtype': input_df[col].dtype.name,
                'distinct_values': input_df[col].unique().tolist()[:distinct_values_limit],
            }

    return metadata_dict


def check_if_df_column_contains_value(input_df, column, value, return_index=False):
    row = input_df[input_df[column]==value]
    if len(row) > 0:
        return row.iloc[0].to_dict()
    return False


def export_df_to_excel(input_df, output_path, replace=True, sheet='Sheet1'):
    writer = pd.ExcelWriter(output_path)
    input_df.to_excel(writer, sheet, index=False)
    writer.save()


def export_df_to_csv(input_df, output_path, replace=True):
    input_df.to_csv(output_path, sep=',', index=False)


def convert_column_to_list(input_df, column, condition_column, condition_value, order_by=None, unique=False):
    output_df = input_df

    # Check if order
    if order_by:
        output_df = output_df.sort_values([order_by])

    # Returns values
    output_df = output_df.loc[input_df[condition_column] == condition_value, column]

    return output_df.tolist()
