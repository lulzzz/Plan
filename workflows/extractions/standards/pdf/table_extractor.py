from tqdm import tqdm
from tabula import read_pdf, convert_into
import os
from datetime import datetime
from stat import * # ST_SIZE etc
import pandas as pd
import numpy as np
from collections import Counter
from pprint import pprint
from slugify import slugify
from difflib import SequenceMatcher

TOP_TABLE_VALID_LABELS = [
     'Agent',
     'C/O',
     'Collection',
     'Create Date',
     'Description',
     'Designer',
     'Division',
     'Fabric',
     'Fabrication',
     'Gender',
     'In-Store Date',
     'Merchandiser',
     'Modified By',
     'P.O.#',
     'PDM No.',
     'Pattern',
     'Prod. Type',
     'Product Line',
     'Production Mgr',
     'Reference',
     'Revise Date',
     'Sample Due Date',
     'Sample Size',
     'Season',
     'Status',
     'Sz. Category',
     'Sz. Range',
     'Tech Designer',
     'Vendor',
]

MEASUREMENT_SPEC_KEY_LABELS = [
    '*',
    'Ref',
    'Measurement Point',
    'Tol -',
    'Tol +'
]

def read_all_pdf(filenames, pages='all'):
    r"""Transfer pdf data for a list of filenames into a dictionary with pandas Data Frame.

    Arguments:
    filenames -- list of pdf file_dict to read data from

    Keyword arguments:
    pages -- (str, int, list of int, optional)
    An optional values specifying pages to extract from. It allows str, int, list of int.
    Example: 1, '1-2,3', 'all' or [1,2]. Default is 'all'
    """
    all_pdf_data = filenames.copy()
    for pdf_data in tqdm(all_pdf_data):
        pdf_data['data'] = read_pdf(pdf_data['abs_path'], pages=pages, multiple_tables=True, encoding='ISO-8859-1', lattice=True, silent=True)

    return all_pdf_data

def extract_top_table(file_property, table_dataframes, valid_labels=TOP_TABLE_VALID_LABELS):
    """Extracts top table from data read by tabula
    Associates a tech_pack_id and file_name for each extracted tuple

    file_property -- dictionary with various filenames of a given file
    table_dataframes -- a list of Pandas Data Frames read by tabula
    valid_labels -- a dictionary containing the labels' variations associated to
                    a correct label, not used if None.
    """
    database_atoms = []

    # Check if tabula import succeeded, when PDF are images only it doesn't import anything
    if len(table_dataframes) == 0:
        entry = {
            'has_data': 0,
            'source_master_name': slugify(file_property['name'], separator='_'),
            'source_master_label': file_property['name'],
            'source_master_reference': file_property['name'] + file_property['extension'],
            'source_master_pattern': file_property['name'] + file_property['extension'],
            'source_master_component_category': 'tuple',
            'source_master_component_reference': 'document',
            'source_master_component_name': 'top_table',
            'source_master_component_label': 'Basic Information',
            'source_metadata_field_format': file_property['extension'][1:],
            'source_metadata_last_modified_dt': datetime.fromtimestamp(os.path.getmtime(file_property['abs_path'])),
            'source_metadata_last_modified_by': 'TBD',
            'source_metadata_file_relative_path': file_property['rel_path'],
            'source_metadata_file_absolute_path': file_property['abs_path'],
            'source_metadata_file_size': os.path.getsize(file_property['abs_path']),
            'source_metadata_file_creation_dt': datetime.fromtimestamp(os.path.getctime(file_property['abs_path'])),
            'source_metadata_file_company': 'Li & Fung Limited',
        }
        database_atoms.append(entry)
        return database_atoms

    # Drop NaN columns
    df_table = table_dataframes[0]
    df_table = df_table.dropna(axis=1, how='all')

    # Truncate data if two tables are merged,
    # the second table is the Measurment Spec which we don't need here
    if len(df_table) > 10:
        i = len(df_table)
        for idx, row in df_table.iterrows():
            if 'Measurement Point' in set(row):
                i = idx

        df_table = df_table.truncate(after=(i-1))

    if not valid_labels:
        # This part is for the first pass:
        # here we look at even columns and assume they are all labels
        # and assume the odd columns are the corresponding values
        labels = []
        values = []
        for x in df_table.iloc[:,::2]:
            labels.extend(list(df_table[x]))
        for x in df_table.iloc[:,1::2]:
            values.extend(list(df_table[x]))

        for label, value in zip(labels, values):

            # Ignore NaN values
            if label is np.nan:
                continue

            # field_format and store data
            value_to_db = value
            if value is np.nan:
                value_to_db = None

            entry = {
                'has_data': 1,
                'source_master_name': slugify(file_property['name'], separator='_'),
                'source_master_label': file_property['name'],
                'source_master_reference': file_property['name'] + file_property['extension'],
                'source_master_pattern': file_property['name'] + file_property['extension'],
                'source_master_component_category': 'tuple',
                'source_master_component_reference': 'document',
                'source_master_component_name': 'top_table',
                'source_master_component_label': 'Basic Information',
                'source_metadata_field_format': file_property['extension'][1:],
                'source_metadata_last_modified_dt': datetime.fromtimestamp(os.path.getmtime(file_property['abs_path'])),
                'source_metadata_last_modified_by': 'TBD',
                'source_metadata_file_relative_path': file_property['rel_path'],
                'source_metadata_file_absolute_path': file_property['abs_path'],
                'source_metadata_file_size': os.path.getsize(file_property['abs_path']),
                'source_metadata_file_creation_dt': datetime.fromtimestamp(os.path.getctime(file_property['abs_path'])),
                'source_metadata_file_company': 'Li & Fung Limited',
                'source_header_name': slugify(label.replace(" ", "").replace("Tol-", "tol_min").replace("Tol+", "tol_max"), separator='_'),
                'source_header_label': label,
                'source_header_data_type': 'TBD',
                'source_data_category': 'tuple',
                'source_data_row_number': 1,
                'source_data_value': value_to_db,
            }

            database_atoms.append(entry)

    else:
        # This part is for the second pass, i.e.: with a list of valid labels
        # We now loop over each tuple (x,y) of df_table
        # with x being at the direct left of y
        # and find valid pairs based on left item x,
        # a pair is considered valid if its left item x is matching in VALID_LABELS

        for idx in range(len(df_table.columns)-1):
            for x,y in zip(list(df_table[idx]),list(df_table[idx+1])):
                valid_label = verify_label(x, valid_labels=valid_labels)
                if valid_label:
                    label = x
                    value = y

                    value_to_db = value
                    if value is np.nan:
                        value_to_db = None

                    entry = {
                        'has_data': 1,
                        'source_master_name': slugify(file_property['name'], separator='_'),
                        'source_master_label': file_property['name'],
                        'source_master_reference': file_property['name'] + file_property['extension'],
                        'source_master_pattern': file_property['name'] + file_property['extension'],
                        'source_master_component_category': 'tuple',
                        'source_master_component_reference': 'document',
                        'source_master_component_name': 'top_table',
                        'source_master_component_label': 'Basic Information',
                        'source_metadata_field_format': file_property['extension'][1:],
                        'source_metadata_last_modified_dt': datetime.fromtimestamp(os.path.getmtime(file_property['abs_path'])),
                        'source_metadata_last_modified_by': 'TBD',
                        'source_metadata_file_relative_path': file_property['rel_path'],
                        'source_metadata_file_absolute_path': file_property['abs_path'],
                        'source_metadata_file_size': os.path.getsize(file_property['abs_path']),
                        'source_metadata_file_creation_dt': datetime.fromtimestamp(os.path.getctime(file_property['abs_path'])),
                        'source_metadata_file_company': 'Li & Fung Limited',
                        'source_header_name': slugify(label.replace(" ", "").replace("Tol-", "tol_min").replace("Tol+", "tol_max"), separator='_'),
                        'source_header_label': label,
                        'source_header_data_type': 'TBD',
                        'source_data_category': 'tuple',
                        'source_data_row_number': 1,
                        'source_data_value': value_to_db,
                    }

                    database_atoms.append(entry)

    return database_atoms

def verify_label(label, valid_labels=None, valid_ratio_threshold=0.8):
    ''' Returns a clean version of a given label
        if match is found within VALID_LABELS
        - label: label string to verify
        - valid_labels: list of valid labels to compare with
        - valid_ratio_threshold: int defining the ratio above which we consider a match
                                 it seems 0.8 works well against examples we've got so far

        Returns 0 if no match. Returns clean label if match.
    '''

    clean_label = 0

    if label is np.nan:
        return 0

    if valid_labels:

        max_ratio = 0

        for valid_label in valid_labels:
            ratio = similar(label, valid_label)

            # Values such as 'S' as is 'size S' should not be considered as candidate labels
            if len(label) > 2:
                # If label is contained in valid_label and vice versa
                # Compare the first 10 characters (avoid cases like Vendor (label) included in Undefined Vendor (value))
                if label[:10] in valid_label[:10] or valid_label[:10] in label[:10]:
                    max_ratio = 1
                    clean_label = valid_label

            # We want to get the valid label with the highest ressemblance ratio
            if ratio > max_ratio:
                max_ratio = ratio
                clean_label = valid_label

        # We filter out labels which do not have a ressemblance ratio high enough
        # i.e.: labels which do not look like any valid label
        if max_ratio < valid_ratio_threshold:
            return 0

    return clean_label

def similar(a, b):
    ''' Returns the ressemblance ratio between the first
        10 characters of two strings
    '''
    return SequenceMatcher(None, a[:10], b[:10]).ratio()


def extract_measurement_table(file_property, table_dataframes, key_labels=MEASUREMENT_SPEC_KEY_LABELS):
    r"""Extracts measurement tables from a list of Data Frames read by tabula

    file_property -- dictionary with various filenames of a given file
    table_dataframes -- a list of Pandas Data Frames read by tabula
    key_labels -- a list of labels common to each entry

    returns
    database_atoms -- list of dict with formatted data
    """
    database_atoms = []

    # Ignore pdf with only images
    if len(table_dataframes) == 0:
        entry = {
            'has_data': 0,
            'source_master_name': slugify(file_property['name'], separator='_'),
            'source_master_label': file_property['name'],
            'source_master_reference': file_property['name'] + file_property['extension'],
            'source_master_pattern': file_property['name'] + file_property['extension'],
            'source_master_component_category': 'tuple',
            'source_master_component_reference': 'document',
            'source_master_component_name': 'top_table',
            'source_master_component_label': 'Basic Information',
            'source_metadata_field_format': file_property['extension'][1:],
            'source_metadata_last_modified_dt': datetime.fromtimestamp(os.path.getmtime(file_property['abs_path'])),
            'source_metadata_last_modified_by': 'TBD',
            'source_metadata_file_relative_path': file_property['rel_path'],
            'source_metadata_file_absolute_path': file_property['abs_path'],
            'source_metadata_file_size': os.path.getsize(file_property['abs_path']),
            'source_metadata_file_creation_dt': datetime.fromtimestamp(os.path.getctime(file_property['abs_path'])),
            'source_metadata_file_company': 'Li & Fung Limited',
        }
        database_atoms.append(entry)
        return database_atoms

    columns = []

    # Loop over tables found by tabula
    for df_table in table_dataframes:

        # Check whether the table is a Measurement Spec
        if len(df_table) == 0:
            continue

        if len(df_table) > 7  and 'Measurement Point' in set(df_table.iloc[7]):
            # Truncate the table above the 7th row, where the measurement spec starts
            df_table = df_table.iloc[7:]

        elif not 'Measurement Point' in set(df_table.iloc[0]):
            continue

        # Clean column names (tabula inserts '\r' when detecting a new line)
        columns_found = [val.replace('\r', ' ') if isinstance(val, str) else val for val in df_table.iloc[0].values ]

        # Filter out tables which do not have the same column format (i.e.: tables after measurement spec have more columns)
        if len(columns) == 0:
            columns = columns_found
        elif columns != columns_found:
            continue

        # Assign column names with first scraped row
        df_table.columns = columns
        # Remove NAN columns and rows
        df_table = df_table.dropna(axis=1, how='all').dropna(axis=0, how='all')

        df_table = df_table.iloc[1:]

        comment = ''
        missing_ref_counter = 0
        prev_measurement_point = ''

        # Loop over cleaned table
        for idx, row in df_table.iterrows():

            measurements = set(row.index.values) - set(key_labels) - set([np.nan])

            # Ignore lines in measurement spec without measurements (i.e.: lines with title or no data)
            condition1 = sum([0 if row[size] in ['.', '0', np.nan] else 1 for size in measurements]) == 0
            condition2 = '.' in str(row['Ref'])
            if condition1 and condition2 :
                comment = row['Measurement Point']
                continue

            for label, value in row.iteritems():

                # sqlalchemy needs None to convert to SQL NULL and does not do the transformation for np.nan
                value_to_db = value
                if value is np.nan:
                    value_to_db = None

                entry = {
                    'has_data': 1,
                    'source_master_name': slugify(file_property['name'], separator='_'),
                    'source_master_label': file_property['name'],
                    'source_master_reference': file_property['name'] + file_property['extension'],
                    'source_master_pattern': file_property['name'] + file_property['extension'],
                    'source_master_component_category': 'table',
                    'source_master_component_reference': 'document',
                    'source_master_component_name': 'measurement_spec',
                    'source_master_component_label': 'Measurement Points',
                    'source_metadata_field_format': file_property['extension'][1:],
                    'source_metadata_last_modified_dt': datetime.fromtimestamp(os.path.getmtime(file_property['abs_path'])),
                    'source_metadata_last_modified_by': 'TBD',
                    'source_metadata_file_relative_path': file_property['rel_path'],
                    'source_metadata_file_absolute_path': file_property['abs_path'],
                    'source_metadata_file_size': os.path.getsize(file_property['abs_path']),
                    'source_metadata_file_creation_dt': datetime.fromtimestamp(os.path.getctime(file_property['abs_path'])),
                    'source_metadata_file_company': 'Li & Fung Limited',
                    'source_header_name': slugify(label.replace(" ", "").replace("Tol-", "tol_min").replace("Tol+", "tol_max"), separator='_'),
                    'source_header_label': label,
                    'source_header_data_type': 'TBD',
                    'source_data_category': 'table',
                    'source_data_row_number': idx,
                    'source_data_value': value_to_db,
                }

                database_atoms.append(entry)

    return database_atoms
