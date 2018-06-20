import os
import sys
import traceback
import numpy as np
import pandas as pd
from datetime import datetime

from sqlalchemy import Table, Column, ForeignKey, create_engine, UniqueConstraint, schema, types, update, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.engine import reflection
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool
from sqlalchemy.types import Integer, VARCHAR, Float, Date, DateTime
from sqlalchemy.sql import func, text
from urllib.parse import quote_plus

from django.conf import settings as cp


function_translator = {
    'sum': func.sum,
    '':lambda x: x,
}
operator_translator = {
    'equal':'__eq__',
    'greater_than':'__gt__',
    'greater_equal':'__ge__',
    'less_than':'__lt__',
    'less_equal':'__le__'
}

def _AND(a,b):
    return (a and b)

def _OR(a,b):
    return (a or b)

def init_op(engine):
    Base = automap_base()
    Base.prepare(engine=engine, reflect=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return Base, session


def db_connect(connection_name='default', encoding='latin-1'):
    r"""
    Performs database connection using database settings from configuration.py.
    Returns sqlalchemy engine instance
    """
    # MSSQL database
    if cp.DATABASES_ALCHEMY[connection_name]['drivername'] == 'mssql+pyodbc':
        params = quote_plus(
            "DRIVER={};SERVER={};DATABASE={};UID={};PWD={}".format(
                'SQL Server Native Client 11.0',
                cp.DATABASES_ALCHEMY[connection_name]['host'],
                cp.DATABASES_ALCHEMY[connection_name]['database'],
                cp.DATABASES_ALCHEMY[connection_name]['username'],
                cp.DATABASES_ALCHEMY[connection_name]['password'],
            )
        )
        return create_engine(cp.DATABASES_ALCHEMY[connection_name]['drivername'] + ':///?odbc_connect=%s' % params, encoding=encoding, poolclass=NullPool)

    # MySQL database
    else:
        return create_engine(URL(**cp.DATABASES_ALCHEMY[connection_name]), encoding=encoding, poolclass=NullPool)


def get_database_table_as_df(engine, table_name):
    r"""
    Load database table as df.
    """
    return pd.read_sql_table(table_name=table_name, con=engine)


def chunker(seq, size):
    r"""
    Iterate over a list of chunks.

    Reference: http://stackoverflow.com/a/434328
    """
    # from http://stackoverflow.com/a/434328
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def load_df_into_database(engine, input_df, table_name, dict_types=None, mode='append', index=False):
    r"""
    Load the df into a database table.
    """
    # Check if dataframe is empty
    if input_df.empty:
        return False
    chunksize = int(len(input_df) / 10) if len(input_df) > 10 else len(input_df)   # 10%
    try:
        for i, cdf in enumerate(chunker(input_df, chunksize)):
            if mode == 'replace' and i > 0:
                mode = 'append'
            cdf.to_sql(con=engine, name=table_name, if_exists=mode, index=index, dtype=dict_types)
    except SQLAlchemyError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        return False
    else:
        return True


def insert_update_database(
    input_select=None,
    input_from=None,
    input_join=None,
    input_where=None,
    input_groupby=None,
    input_update_condition=None,
    input_update=None,
    input_insert=None,
    engine=None
    ):
    '''
    Except for input_update_condition & input_update, others parameters are optional.
    '''
    # print('init')
    Base, session = init_op(engine=engine)

    ################ create the all_table_objects dict to store all the classes ################
    # print('preparing')
    all_tables = []
    for k in ['table', 'left_table', 'right_table']:
        for l in [input_select,input_from,input_join,input_where,input_groupby,input_update_condition]:
            try:
                for d in l:
                    try:
                        all_tables.append(d[k])
                    except:
                        pass
            except:
                pass
    all_tables = list(set(all_tables))
    all_table_objects = {}
    for table in all_tables:
        all_table_objects[table] = getattr(getattr(Base, 'classes'),table)

    ################ select clause ################
    if input_select == None:
        tablename = input_update_condition[0]['table']
        colname = [attr for attr in dir(all_table_objects[tablename]) if ((attr[0] != '_') and (attr not in ['classes', 'metadata', 'prepare']))]
        input_select = [
            {
                'function': '',
                'table': tablename,
                'column': col,
                'new_name': ''
            }
            for col in colname
                                        ]
    output_select = tuple()
    for d in input_select:
        col = getattr(all_table_objects[d['table']],d['column'])
        transform = function_translator[d['function']](col)
        if d['new_name'] != '':
            new_name = d['new_name']
        else:
            new_name = d['column']
        select = transform.label(new_name)
        output_select += (select,)

    ################ where clause #################
    if input_where == None:
        pass
    else:
        output_where = and_() # list alike
        for d in input_where:
            col = getattr(all_table_objects[d['table']],d['column'])
            value = d['value']
            where = getattr(col, operator_translator[d['operator']])(value)
            output_where.append(where)
    if input_join == None:
        pass
    else:
        for d in input_join:
            if d['join_method'] == 'inner':
                left = getattr(all_table_objects[d['left_table']],d['left_key_0'])
                right = getattr(all_table_objects[d['right_table']],d['right_key_0'])
                join = getattr(left, operator_translator['equal'])(right)
                output_where.append(join)

    ################ groupby clause ################
    if input_groupby == None:
        pass
    else:
        output_groupby = tuple()
        for d in input_groupby:
            col = getattr(all_table_objects[d['table']],d['column'])
            output_groupby += (col,)

    ################ query ################
    # print('querying')
    query2 = session.query(all_table_objects[tablename])
#     query2 = session.query(*output_select)
    if input_where is not None:
        query2 = query2.filter(output_where)
    if input_groupby is not None:
        query2 = query2.group_by(*output_groupby)
    ################ insert/update ################
    # print('updating')
    new_row_list = []
    update = 0
    for row_2 in query2.all():
        left = getattr(row_2, input_update_condition[0]['column'])
        operator = operator_translator[input_update_condition[0]['operator']]
        right = input_update_condition[0]['value_value']
        condition = getattr(left,operator)(right)
        if condition:
            for c,v in input_update.items():
                setattr(row_2, c, v)
            update = 1
    if update == 0:
        # print("inserting")
        input_update_objects = {}
        for key, value in input_update.items():
            input_update_objects[key] = value
        if input_update_condition[0]['operator'] == 'equal':
            input_update_objects[input_update_condition[0]['column']] = input_update_condition[0]['value_value']
        new_row = all_table_objects[input_update_condition[0]['table']](**{**input_update_objects})
        new_row_list.append(new_row)
        session.add(new_row)
        session.commit()
    session.flush()
    # print('finished')
