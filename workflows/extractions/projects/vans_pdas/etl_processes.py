import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from workflows.extractions.projects.vans_pdas import magic

def get_data_from_extracts(source_file_path):
    r"""
    =======================================================
        Extract and load Input Files in Staging Area
    =======================================================
    """

    log_file = source_file_path + '\Log\\' + datetime.now().strftime('%Y-%m-%d') + '.log'

    magic.write_to_file(log_file, '''\n\n\n#### ETL BEGIN ####\n''', with_time_stamp=False)
    magic.write_to_file(log_file, '''## FILES ##\n''', with_time_stamp=False)

    # Display progress logs on stdout
    magic.write_to_file(log_file, r'''Scanning directory {}'''.format(source_file_path))
    engine = magic.db_connect(connection_name='default')

    pdas_metadata = pd.read_sql_table('pdas_metadata', engine)

    df_metadata_before = magic.get_table_to_df(engine, 'pdas_metadata')
    # Scan folder and sub-folders
    for f in df_metadata_before[df_metadata_before['etl_type'] == 'file']['src_name'].values.tolist():

        # Work with files defined in metadata table only
        if not(os.path.isfile(source_file_path + '\\' + f)):
            continue

        # Log the timestamp of the file
        magic.write_to_file(log_file, r'''Processing ETL for file {} started'''.format(f))
        timestamp_old = magic.get_table_column_values_as_list(engine, 'pdas_metadata', 'timestamp_file', {'src_name': [f]})[0].strftime("%Y-%m-%d %H:%M:%S")
        timestamp_new = magic.get_modified_date(os.path.join(source_file_path, f))
        if timestamp_old == timestamp_new:
            magic.write_to_file(log_file, r'''File {} already loaded for this modified date {}'''.format(f, timestamp_new))
            continue

        magic.set_table_column_value(engine, 'pdas_metadata', 'state', 'TBL', 'src_name', f)

        # Read Excel file
        if os.path.splitext(os.path.join(source_file_path, f))[1] in ('.xlsx', '.xls'):
            xl = pd.ExcelFile(os.path.join(source_file_path, f))
            if 'PDAS' in xl.sheet_names:
                df = pd.read_excel(os.path.join(source_file_path, f), sheetname='PDAS')
                converters = dict()
                for column in df.columns:
                    converters[column] = str
                df = pd.read_excel(os.path.join(source_file_path, f), sheetname='PDAS', converters=converters) #, converters = {"Purch.req.": str, "Sales Doc.": str, "SO# (only for directs)": str})
                magic.write_to_file(log_file, r'''File {} has {} rows and {} columns'''.format(f, df.shape[0], df.shape[1]))
            else:
                magic.write_to_file(log_file, r'''Couldn't process the file {} (reason: No sheet named "PDAS")'''.format(f))
                sys.exit(1)

        # Read CSV file
        elif os.path.splitext(os.path.join(source_file_path, f))[1] in ('.csv'):
            sep = magic.find_delimiter(os.path.join(source_file_path, f))
            df = pd.read_csv(os.path.join(source_file_path, f), sep=sep, error_bad_lines=False, encoding='latin-1', low_memory=False, warn_bad_lines=False)

        # Error message
        else:
            magic.write_to_file(log_file, r'''Couldn't process the file {} (reason: File not found)'''.format(f))
            continue

        # From Pandas to staging area
        #magic.convert_numeric_col(df)
        #df.columns = [magic.rewrite_with_technical_convention(col) for col in df.columns]

        # load the staging table
        tablename = magic.get_table_column_values_as_list(engine, 'pdas_metadata', 'table_name', {'src_name': [f]})[0]
        magic.write_to_file(log_file, r'''Loading table {} in staging area'''.format(tablename))
        magic.delete_from_table(engine, tablename)
        new_names = magic.get_column_names(engine, tablename)
        df = df.rename(columns={old_col: new_col for old_col, new_col in zip(df.columns, new_names)})
        df = magic.set_pandas_dtypes_with_db_table_types(df, magic.get_column_types(engine, tablename))
        db_dicttypes = magic.gen_types_from_pandas_to_sql(df)
        if len(df) > 0:
            flag = magic.load_df_into_db(engine, df, tablename, dict_types=db_dicttypes, mode='append')
        else:
            flag = 1

        if flag == 0:
            magic.write_to_file(log_file, r'''FAIL Loading table {}'''.format(f))
            magic.write_to_file(log_file, r'''Processing ETL for file {} ended in error'''.format(f))
            sys.exit(1)
        else:
            magic.write_to_file(log_file, r'''Processing ETL for file {} ended successfully'''.format(f))

            # Update timestamp column
            magic.set_table_column_value(engine, 'pdas_metadata', 'timestamp_file', timestamp_new, 'src_name', f)
            magic.set_table_column_value(engine, 'pdas_metadata', 'state', 'OK', 'src_name', f)

        magic.write_to_file(log_file, '''\n\n''', with_time_stamp=False)
