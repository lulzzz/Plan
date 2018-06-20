import os
import time

from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine, and_
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func, text


from django.conf import settings as cp
import workflows.generic.database_utils as db

engine = db.db_connect()


function_translator = {
    'sum': func.sum,
    '':lambda x: x,
}
operator_translator = {'equal':'__eq__',
                      'greater_than':'__gt__',
                      'greater_equal':'__ge__',
                      'less_than':'__lt__',
                      'less_equal':'__le__',}

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


def insert_update(
    input_select,
    input_from,
    input_join,
    input_where,
    input_groupby,
    input_update_condition,
    input_update,
    input_insert,
    engine=engine
    ):
    '''
    For joinning, currently only support inner join(implement in where clause)
    For update condition,  currently only support 1 condition
    Update & insert algo could be improved - now complexity is n^2
    '''
    print('init')
    Base, session = init_op(engine=engine)

    ################ create the all_table_objects dict to store all the classes ################
    print('preparing')
    all_tables = []
    for k in ['table', 'left_table', 'right_table']:
        for d in input_select+input_from+input_join+input_where+input_groupby+input_update_condition:
            try:
                all_tables.append(d[k])
            except:
                pass
    all_tables = list(set(all_tables))
    all_table_objects = {}
    for table in all_tables:
        all_table_objects[table] = getattr(getattr(Base, 'classes'),table)

    ################ select clause ################
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
    output_where = and_() # list alike
    for d in input_where:
        col = getattr(all_table_objects[d['table']],d['column'])
        value = d['value']
        where = getattr(col, operator_translator[d['operator']])(value)
        output_where.append(where)
    for d in input_join:
        if d['join_method'] == 'inner':
            left = getattr(all_table_objects[d['left_table']],d['left_key_0'])
            right = getattr(all_table_objects[d['right_table']],d['right_key_0'])
            join = getattr(left, operator_translator['equal'])(right)
            output_where.append(join)

    ################ groupby clause ################
    output_groupby = tuple()
    for d in input_groupby:
        col = getattr(all_table_objects[d['table']],d['column'])
        output_groupby += (col,)

    ################ query ################
    print('querying')
    query1 = session.query(all_table_objects[input_update_condition[0]['table']])
    query2 = session.query(*output_select).filter(output_where).group_by(*output_groupby)
    ################ insert/update ################
    print('updating')
    new_row_list = []
    for row_2 in query2.all():
        update = 0
        for row_1 in query1.all():
            left = getattr(row_1, input_update_condition[0]['column'])
            right = getattr(row_2, input_update_condition[0]['value_column'])
            operator = operator_translator[input_update_condition[0]['operator']]
            condition = getattr(left,operator)(right)
            if condition:
                for left_col,right_col in input_update.items():
                    setattr(row_1, left_col, getattr(row_2, right_col))
                update = 1

        if update == 0:
            print("inserting")
            input_update_objects = {}
            for key, value in input_update.items():
                input_update_objects[key] = getattr(row_2, value)
            new_row = all_table_objects[input_update_condition[0]['table']](**{**input_update_objects,**input_insert})
            new_row_list.append(new_row)
            session.add(new_row)
            session.commit()
    session.flush()
    print('finished')
