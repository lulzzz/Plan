import sys
import time
import copy
from dateutil import parser
from datetime import datetime
from django.conf import settings as cp
from django.utils import timezone

import django
django.setup()

from apps.standards.app_pipeline import models

from workflows.core import os_utils
from workflows.core import database_utils
from workflows.core import df_utils

from workflows.transformations.standards import df_transformation_rules


def s01_load_extracts(
    file_dict,
    add_rules=False,
    delete_rules=False,
    add_keys=False,
    reload=False
):
    r"""
    Extract and load Input Files in Staging Area
    """

    print('Scanning directory {}'.format(cp.INPUT_DIRECTORY))

    # Establish connection to database
    engine = database_utils.db_connect()

    # Time keeper
    start_time = time.time()
    current_time = start_time

    # Load models
    pipeline_metadata_queryset = models.Metadata.objects
    pipeline_metadatarule_queryset = models.MetadataRule.objects

    pipeline_metadata_rule_df = database_utils.get_database_table_as_df(
        engine=engine,
        table_name='app_pipeline_metadatarule',
    )

    # Iterate through files
    for filename, properties in file_dict.items():

        # Desactivate timezone support
        print('\nScanning file', '"' + filename + '.' + properties.get('extension') + '"')

        # Defining variables
        metadata_id = None
        cp.TEMP_SHEET_NAME = None
        database_table_name = os_utils.rewrite_with_technical_convention('sa01_' + filename + '_' + properties.get('extension'))
        has_rule = add_rules
        last_modified_dt = parser.parse(properties.get('last_modified_dt'))
        creation_dt = parser.parse(properties.get('creation_dt'))
        metadata_row = pipeline_metadata_queryset.filter(filename=filename).first()

        # Check if file was loaded into database before
        if metadata_row:
            print('Metadata found')

            # Check if modified_dt changed
            metadata_last_modified_dt = metadata_row.last_modified_dt
            if not reload and str(metadata_last_modified_dt) == str(last_modified_dt):
                continue

            print('Reload updated version of file')
            # Store sheet_name in case of Excel source file
            cp.TEMP_SHEET_NAME = metadata_row.sheet_name
            metadata_id = metadata_row.id
            has_rule = True if metadata_row.has_rule else False

        else:
            print('Load new file')

        # Convert source file into df
        print('Convert source file into df')
        output_df = df_utils.create_df_from_source_file(properties.get('abs_path'))

        # Apply transformation rules
        rule_list = list()

        # Use existing rules from database
        if metadata_id:
            rule_list = list(pipeline_metadatarule_queryset.filter(
                metadata_id=metadata_id
            ).order_by('position').values_list('rule', flat=True))

        # Adding new rules
        if has_rule or add_rules:
            rule_list_new, has_rule = add_rule_process(rule_list)
            rule_list += rule_list_new

        # Delete existing rules
        if delete_rules:
            delete_rule_process(rule_list)

        # Apply rules
        print('Apply transformation rules')
        output_df = df_transformation_rules.apply_rule_list(output_df, rule_list)

        # Convert all columns into object type
        output_df = df_utils.convert_object_col(output_df)
        output_df = df_utils.convert_datetime_col(output_df)
        df_utils.convert_numeric_col(output_df)

        # Add filename column
        # output_df.insert(0, 'filename', os.path.basename(source_path))

        # Standardize header
        output_df.columns = [os_utils.rewrite_with_technical_convention(x) for x in output_df.columns]

        # Get column types
        db_dicttypes = df_utils.gen_types_from_pandas_to_sql(output_df)

        r"""
        Database part
        """
        # Load df into database
        print('Load df into database')
        database_utils.load_df_into_database(
            engine=engine,
            input_df=output_df,
            table_name=database_table_name,
            dict_types=db_dicttypes,
            mode='replace',
            index=False,
        )

        # Insert/update metadata record
        print('Save metadata')
        item, created = pipeline_metadata_queryset.update_or_create(
            filename=filename, defaults={
                'database_table': database_table_name,
                'rel_path': properties.get('rel_path'),
                'abs_path': properties.get('abs_path'),
                'extension': properties.get('extension'),
                'size': properties.get('size'),
                'last_modified_dt': last_modified_dt,
                'creation_dt': creation_dt,
                'sheet_name': cp.TEMP_SHEET_NAME,
                'has_rule': has_rule,
                'col_number': output_df.shape[1],
                'row_number': output_df.shape[0],
            }
        )

        # Save transformation rules
        if len(rule_list) > 0:
            print('Save transformation rules')

            # Get metadata id if not existing
            if not metadata_id:
                metadata_row = pipeline_metadata_queryset.filter(filename=filename).first()
                metadata_id = metadata_row.id

            pipeline_metadatarule_queryset.filter(
                metadata_id=metadata_id
            ).delete()

            for idx, rule in enumerate(rule_list, 1):
                print(rule_list)
                item, created = pipeline_metadatarule_queryset.update_or_create(
                    metadata_id=metadata_id, rule=rule, defaults={
                        'metadata_id': int(metadata_id),
                        'position': int(idx),
                        'rule': int(rule),
                    }
                )

        # Get keys
        if add_keys:
            pass

        print('Total lapsed time:', round((time.time() - start_time) % 60), 'seconds')
        print('Elapsed time:', round((time.time() - current_time) % 60), 'seconds')
        current_time = time.time()


def add_rule_process(rule_list):
    r"""
    Add new rules
    """

    print('\nAvailable rules:')
    for rule_dict in cp.AVAILABLE_RULE_LIST:
        for k, v in rule_dict.items():
            if k not in rule_list:
                print('-', str(k) + ':', v)
                break

    rule_list = list()
    has_rule = True

    # Multiple rules
    while True:

        # One rule
        while True:
            rule_index = input('Select rule index (or enter to break): ')

            # Break
            if rule_index is '':
                break

            # Concert into int
            try:
                rule_index_int = int(rule_index)
            except ValueError:
                rule_index_int = -1

            # Check if exists in cp.AVAILABLE_RULE_LIST
            print(rule_index_int, rule_list)
            if rule_index_int in [k for d in cp.AVAILABLE_RULE_LIST for k in d.keys()] and rule_index_int not in rule_list:
                rule_list.append(rule_index_int)
                break

        # Check if more rules are needed
        additional_rule = input('Additional rule ("Y" to continue, "N" or enter to break): ')
        additional_rule = str(additional_rule[:1].upper())

        if additional_rule == 'Y':
            continue
        elif additional_rule == 'N':
            has_rule = False
        break

    return rule_list, has_rule


def delete_rule_process(rule_list):
    r"""
    Delete existing rules
    """

    print('\nApplied rules:')
    for rule in rule_list:
        for rule_dict in cp.AVAILABLE_RULE_LIST:
            for k, v in rule_dict.items():
                if k is rule:
                    print('-', str(k) + ':', v)
                break

    # Multiple rules
    while True:

        # One rule
        while True:
            rule_index = input('Select rule index (or enter to break): ')

            # Break
            if rule_index is '':
                break

            # Concert into int
            try:
                rule_index_int = int(rule_index)
            except ValueError:
                rule_index_int = -1

            # Check if exists in rule_list
            if rule_index_int in rule_list:
                rule_list.remove(rule_index_int)
                break

        # Check if more rules are needed
        additional_rule = input('Delete another rule? ("Y" to continue, enter to break): ')
        additional_rule = str(additional_rule[:1].upper())
        if additional_rule != 'Y':
            break

    return rule_list



from workflows.extractions.standards.rar import extract_data as extract_from_rar
from workflows.extractions.standards.tar import extract_data as extract_from_tar
from workflows.extractions.standards.zip import extract_data as extract_from_zip

def s01_extract_from_packaged_files(filename_dict):

    filename_dict_output = dict()
    for filename, properties in filename_dict.items():

        extension = properties['extension']
        source_path = properties['abs_path']

        if extension in ('rar'):
            folderpath = extract_from_rar.extract(source_path)

        elif extension in ('tar'):
            folderpath = extract_from_tar.extract(source_path)

        elif extension in ('zip'):
            folderpath = extract_from_zip.extract(source_path)

        filename_dict_output.update(
            os_utils.get_file_properties(
                folder=folderpath,
                result_format='file_property_dict',
                extension_list=['xlsx', 'csv', 'xls', 'json', 'xml', 'txt', 'pdf', 'ods', 'html', 'dat', 'zip', 'rar', 'tar', 'sql', 'log'],
            )
        )

    return filename_dict_output
