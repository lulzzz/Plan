"""
example of input_dict

input_dict = {
    'model': 'self.model._meta.db_table',
    'key_field': 'product_division', # product_category
    'levels': ['product_division', 'product_category'],
    'field_reference': {
        'unit_sales_py_index': 'unit_sales_py',
        'unit_sales_py_mix': 'unit_sales_py',
        'unit_sales_ly': 'unit_sales_py'
    },
    'data': {
        'product_division':[
            '101 LEGWEAR',
            '102 READY-TO-WEAR',
            '103 SWIMWEAR',
            '104 LINGERIE',
            '180 ACCESSORIES',
            '190 ADV.+PROMOTION'
        ],
        'unit_sales_py_mix':[
            '50%',
            '15.528928%',
            '1.999997%',
            '14.925680%',
            '1.992612%',
            '0.009897%'
        ],
        'unit_sales_py_index':[
            '2.0',
            '1.0',
            '1.0',
            '1.0',
            '1.0',
            '1.0'
        ]
    }
}
"""
import sys
import copy
import numpy as np
import pandas as pd
from slugify import slugify
from xml.etree.ElementTree import Element, SubElement
from sqlalchemy.orm import sessionmaker

from workflows.core.database_utils import db_connect
from workflows.core.hierarchy_class import PropagationTree

from sqlalchemy.ext.automap import automap_base

def update_mix_index(input_dict):
    r"""Finds differences and updates database accordingly

    >>> update_mix_index(input_dict)"""

    # Read input
    levels = input_dict['levels']
    table_name = input_dict['model']

    # Create connection to database, TODO: these needs to be put somehwere else
    engine = db_connect()
    Session = sessionmaker(bind=engine)

    Base = automap_base()
    Base.prepare(engine, reflect=True)

    classes = Base.classes
    session = Session()

    # Read data from Database (this part is not generic)
    data = pd.read_sql(session.query(classes[table_name]).statement, session.bind)

    # Get columns label mappings
    map_code, columns_mappings = get_mappings(input_dict)

    # Map columns label
    data = data.rename(columns = columns_mappings)

    # Slugify tags
    for level in levels:
        data[level] = data[level].apply(slugify)


    # == Step 1: Get original tree based on data

    original_tree = PropagationTree(data, levels)


    # == Step 2: Original Tree x [database mix, database index] = Database Tree

    database_tree = copy.deepcopy(original_tree)

    # Apply index
    if 'index' in data.columns:
        for i, entry in data.iterrows():
            database_tree.index(entry[levels], entry['index'])

    # Apply mix
    if 'mix' in data.columns:
        database_tree.mix(data[levels].values, data['mix'].values)


    # == Step 3: Database Tree (level n) - User Input Tree (level n) = [transfo mix, transfo index]

    # Get user input Data Frame
    df_input = get_df_from_user_input(input_dict)

    # Get level (in the tree) at which the comparison takes place
    comparison_level = input_dict['key_field']
    comparison_level_idx = levels.index(comparison_level) + 1
    comparasion_level_path = levels[:comparison_level_idx] # list of levels to get to comparison level

    # Get database Data Frame
    df_database = database_tree.get_df(comparison_level_idx)

    # Set comparasion_level_path as index for the join
    df_i = df_input.set_index(comparasion_level_path)
    df_d = df_database.set_index(comparasion_level_path)

    df_compare = df_d.join(df_i, rsuffix='_input', lsuffix='_db')

    # INDEX
    if 'index' in df_input.columns:
        # Create index_new (the index to input for the transformation)
        df_compare['index_new'] = df_compare['index_input']

        # Fill nan of index_new with index_db because we transform original_tree to new_database_tree
        df_compare.loc[df_compare['index_new'].isnull(),'index_new'] = df_compare.loc[df_compare['index_new'].isnull(),'index_db']

        # Create index_diff
        df_compare['index_diff'] = df_compare['index_input'] - df_compare['index_db']


    # MIX
    if 'mix' in df_input.columns:
        df_compare['mix_diff'] = df_compare['mix_input'] - df_compare['mix_db']
        df_compare['mix_new'] = df_compare['mix_diff'].apply(is_different).replace(0, np.nan)*df_compare['mix_input']

    # VALUE
    if 'value_input' in df_input:
        df_compare['value_diff'] = df_compare['value_input'] - df_compare['value']
        df_compare['value_new'] = df_compare['value_diff'].apply(is_different).replace(0, np.nan)*df_compare['value_input']


    # == Step 4: Original Tree (level n) x [transfo mix, transfo index] = New Database Tree
    new_database_tree = copy.deepcopy(original_tree)

    update = False

    # Apply value in priority
    if 'value_input' in df_input.columns:
        update = True
        for tags, value_new in df_compare['value_new'].dropna().items():
            new_database_tree.value(tags, value_new)

    else:
        # Apply index
        if 'index' in df_input.columns:
            update = True
            for tags, index_new in df_compare['index_new'].items():
                new_database_tree.index(tags, index_new)

        # Apply mix
        if 'mix' in df_input.columns:
            update = True
            if df_compare['mix_new'].sum() != 0:
                # if modification detected
                new_database_tree.mix(
                    df_compare['mix_new'].dropna().index,
                    df_compare['mix_new'].dropna().values
                )
            else:
                # otherwise, apply old mix
                new_database_tree.mix(
                    df_compare['mix_db'].dropna().index,
                    df_compare['mix_db'].dropna().values
                )

    # == Step 5: New Database Table -> Save to DB
    if update:
        database_items = session.query(classes[table_name]).all()

        df_update = pd.merge(data[['id']+levels], new_database_tree.get_df(), on=levels)
        df_update.rename(columns={'value':'value_input'}, inplace=True)

        attribude_codes = list(set(['mix', 'index', 'value_input']) & set(map_code.keys()))

        # Loop over new data
        for i, entry in df_update.iterrows():

            # Get matched database item
            for database_item in database_items:
                if database_item.id == entry['id']:

                    # Update values
                    for attribute_code in attribude_codes:
                        setattr(database_item, map_code[attribute_code], entry[attribute_code])

        session.commit()

def get_mappings(input_dict):
    r"""Create mappings between input fields and """
    map_code = dict()
    for key, label in input_dict['field_reference'].items():
        if key.find('index') > -1:
            map_code['index'] = key
        elif key.find('mix') > -1:
            map_code['mix'] = key
        else:
            map_code['value'] = key
            map_code['value_input'] = label

    columns_mappings = {v:k for k,v in map_code.items()}
    return map_code, columns_mappings

# Database Tree (level n) - User Input Tree (level n) = [transfo mix, transfo index]

def get_df_from_user_input(input_dict):
    r'''Transform user input dictionary into pandas Data Frame'''

    df = pd.DataFrame(input_dict['data'])

    # Rename columns
    map_code, columns_mappings = get_mappings(input_dict)
    df = df.rename(columns=columns_mappings)

    # Get tags
    levels = input_dict['levels']
    comparison_level = input_dict['key_field']
    comparison_level_idx = levels.index(comparison_level) + 1
    comparasion_level_path = levels[:comparison_level_idx]
    for level in comparasion_level_path:
        df[level] = df[level].apply(slugify)

    # Get clean INDEX and MIX
    if 'index' in df.columns:
        df['index'] = df['index'].apply(float)
    if 'mix' in df.columns:
        df['mix'] = df['mix'].apply(convert_percentage)
    if 'value' in df.columns:
        df['value'] = df['value'].apply(lambda s: s.replace(',','')).apply(float)
    if 'value_input' in df.columns:
        df['value_input'] = df['value_input'].apply(lambda s: s.replace(',','')).apply(float)

    return df

def convert_percentage(s):
    if s.find('%') > -1:
        return float(s.replace('%',''))/100
    return float(s)

def is_different(value):
    if -1e-4 < value < 1e-4:
        return 0
    return 1
