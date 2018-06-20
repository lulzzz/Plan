

##########################
#### Pandas - related ####
##########################


def str_join(df, sep, cols):
    r"""
    Returns column concatenated from list of columns
    """
    return reduce(lambda x, y: x.astype(str).str.cat(y.astype(str), sep=sep),
                  [df[col] for col in cols])


def format_dataframe_numeric_values(df, dict_formatting):
    r"""
    Returns dataframe with applied formatting
    """
    for col, formatting in dict_formatting.items():
        if formatting is None:
            continue
        if '%' in formatting:
            df[col] = np.where(pd.isnull(df[col]), formatting.format(0), df[col].apply(lambda x: formatting.format(x*100)))
        else:
            df[col] = np.where(pd.isnull(df[col]), formatting.format(0), df[col].apply(lambda x: formatting.format(x)))
    return df


def unformat_dataframe_numeric_values(df, dict_dtypes):
    r"""
    Returns dataframe with raw formatting
    """
    for col, dtype in dict_dtypes.items():
        if col in df.columns:
            if 'int' in str(dtype) or 'float' in str(dtype):
                df[col] = df[col].fillna(np.nan)
                if any('%' in str(x) for x in df[col]):
                    df[col] = df[col].apply(lambda x: x.replace(',', '.'))
                    df[col] = df[col].apply(lambda x: convert_string_to_float(x) / 100 if '.' in x else convert_string_to_int(x) / 100)
                    df[col] = df[col].astype('float64')
                else:
                    df[col] = df[col].apply(lambda x: convert_string_to_float(x) if '.' in x else convert_string_to_int(x))
                    df[col] = df[col].apply(pd.to_numeric, errors='coerce')
    return df


def drop_cols_y(table):
    r"""
    Drop overlapped cols from merge, and rename the ones we keep (get rid of the _x suffix)
    """
    to_drop = [x for x in table if x.endswith('_y')]
    to_rename = [x for x in table if x.endswith('_x')]
    dict_cols_to_rename = {x: re.sub(r'''_x$''', '', x) for x in to_rename}
    table = table.rename(columns=dict_cols_to_rename)
    return table.drop(to_drop, axis=1)


def drop_cols_null(df):
    r"""
    Drop columns with only None values
    """
    for col in df.columns:
        if (all(pd.isnull(x) for x in df[col].unique())):
            df = df.drop(col, 1)
    return df


def change_column_order(df, col_name, index):
    r"""
    Switch column position using its index
    """
    cols = df.columns.tolist()
    if not(isinstance(col_name, list)):
        col_name = [col_name]
    for col in col_name:
        cols.remove(col)
        cols.insert(index, col)
        index += 1
    return df[cols]


def transcode_col_using_dict(df, list_col, dict_transco):
    r"""
    Take an input dataframe and mapping dictionary and transcode cols to dictionary value looking up on dictionary keys
    """
    if dict_transco:
        if not(isinstance(list_col, list)):
            list_col = [list_col]
        for col in list_col:
            if col in df.columns:
                df[col] = df[col].map(lambda x: dict_transco[x])
    return df


def display_table(table, nrows):
    r"""
    Display nrows number of rows of table table using to_string method of pandas
    """
    print(table.to_string(max_rows=nrows))


def remove_header_from_df(table):
    r"""
    Iterate over dataframe rows and remove duplicated header
    """
    df = pd.DataFrame(
        [row for row in table.values.tolist() if not(compare_two_lists([str(x).lower() for x in row], table.columns))],
        columns=table.columns
    )
    return df


def chunker(seq, size):
    # from http://stackoverflow.com/a/434328
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def load_df_into_db(engine, table, name, dict_types=None, mode='append', index=False):
    r"""
    Load the dataframe into a database ...
    """
    # Check if dataframe is empty
    if table.empty:
        return 0
    chunksize = int(len(table) / 10) if len(table) > 10 else len(table)   # 10%
    try:
        for i, cdf in enumerate(chunker(table, chunksize)):
            if mode == 'replace' and i > 0:
                mode = 'append'
            cdf.to_sql(con=engine, name=name, if_exists=mode, index=index, dtype=dict_types)
    except SQLAlchemyError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for line in lines:
            functions.write_to_file(cp.LOG_FILE_PATH + 'cluster_process.log', line)
        return 0
    else:
        return 1


def cud_save(engine, df, db_table):
    r"""
    Insert new rows
    Update matching rows
    Delete remove rows
    """
    # Check if dataframe is empty
    if df.empty:
        return False




def get_table_to_df(engine, table, dictfilter=None, output_cols=None):
    r"""
    Extract data from table and return a dataframe
    """
    alchemy_table = Table(table, metadata, autoload=True, autoload_with=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    queryset = session.query(alchemy_table)
    if dictfilter:
        for key, values in dictfilter.items():
            if isinstance(values, dict):

                if not(isinstance(values['values'], list)):
                    values['values'] = [values['values']]
                # Lookup parameters from settings.py
                values['values'] = map_parameters(values['values'])
                # Transform string None in Python None
                values['values'] = [None if l == 'None' else l for l in values['values']]
                # convert the values in date or numeric
                if all(is_integer(l) for l in values['values']):
                    values['values'] = [convert_string_to_int(l) for l in values['values']]
                elif all(is_float(l) for l in values['values']):
                    values['values'] = [convert_string_to_float(l) for l in values['values']]
                elif all(is_datetime(l) for l in values['values']):
                    values['values'] = [convert_string_to_datetime(l) for l in values['values']]

                # Apply the various kind of filters
                if values['type'] == 'between':
                    queryset = queryset.filter(and_(getattr(alchemy_table.c, key) >= values['values'][0], getattr(alchemy_table.c, key) <= values['values'][-1]))
                if values['type'] == 'between open':
                    queryset = queryset.filter(and_(getattr(alchemy_table.c, key) > values['values'][0], getattr(alchemy_table.c, key) < values['values'][-1]))
                if values['type'] == '==':
                    queryset = queryset.filter(getattr(alchemy_table.c, key) == values['values'])
                if values['type'] == '>=':
                    queryset = queryset.filter(getattr(alchemy_table.c, key) >= values['values'])
                if values['type'] == '>':
                    queryset = queryset.filter(getattr(alchemy_table.c, key) > values['values'])
                if values['type'] == '<':
                    queryset = queryset.filter(getattr(alchemy_table.c, key) < values['values'])
                if values['type'] == '<=':
                    queryset = queryset.filter(getattr(alchemy_table.c, key) <= values['values'])
                if values['type'] == 'in':
                    if None in values['values']:
                        queryset_none = queryset.filter(getattr(alchemy_table.c, key).is_(None))
                        values['values'] = [v for v in values['values'] if v]
                        queryset_others = queryset.filter(getattr(alchemy_table.c, key).in_(values['values']))
                        queryset = queryset_none.union(queryset_others)
                    else:
                        queryset = queryset.filter(getattr(alchemy_table.c, key).in_(values['values']))
                if values['type'] == 'not in':
                        if None in values['values']:
                            queryset_none = queryset.filter(getattr(alchemy_table.c, key).isnot(None))
                            values['values'] = [v for v in values['values'] if v]
                            queryset = queryset_none.filter(getattr(alchemy_table.c, key).notin_(values['values']))
                        else:
                            queryset = queryset.filter(getattr(alchemy_table.c, key).notin_(values['values']))
                if values['type'] == 'like':
                    for pattern in values['values']:
                        queryset = queryset.filter(getattr(alchemy_table.c, key).ilike('%' + pattern + '%'))

            else:
                queryset = queryset.filter(getattr(alchemy_table.c, key).in_(values))
        result = pd.read_sql_query(queryset.statement, engine)
        result = result.rename(columns={col: col.replace(table + '_', '') for col in result.columns})
    else:
        result = pd.read_sql_table(table, engine)
    session.close()
    # Convert dtypes to match with table types
    result = set_pandas_dtypes_with_db_table_types(result, get_column_types(engine, table))
    # output columns
    if output_cols:
        result = result[output_cols]
    return result


def merge_dfs(ldf, rdf):
    r"""
    Generic merging using dict structure like following:
    ldf/rdf = {'table': <table_name>, 'frame_data': dataframe, 'frame_rel': df_keys}
    """
    # Assign variables
    df_left = ldf['frame_data']
    df_right = rdf['frame_data']

    left_on = rdf['frame_rel']['l_field'].values[0]
    right_on = rdf['frame_rel']['r_field'].values[0]
    how = rdf['frame_rel']['how'].values[0]

    partition_fields = rdf['frame_rel']['partition_fields'].tolist()[0]
    if partition_fields and ',' in partition_fields:
        partition_fields = [x.strip() for x in partition_fields.split(',')]
    aggregation_fields = None
    if rdf['frame_rel']['aggregation_fields'].tolist()[0]:
        aggregation_fields = json.loads(rdf['frame_rel']['aggregation_fields'].tolist()[0])
    rename_fields = None
    if rdf['frame_rel']['rename_fields'].tolist()[0]:
        rename_fields = json.loads(rdf['frame_rel']['rename_fields'].tolist()[0])
    pivot_arguments = None
    if rdf['frame_rel']['pivot_arguments'].tolist()[0]:
        pivot_arguments = json.loads(rdf['frame_rel']['pivot_arguments'].tolist()[0])

    # check for pre-join aggregation
    if rdf['frame_rel']['agg_before_after_join'].values[0] and rdf['frame_rel']['agg_before_after_join'].values[0] == 'before':
        df_right = aggregate_df(df_right, partition_fields, aggregation_fields, rename_fields)
    # check for pre-join pivot
    if rdf['frame_rel']['pivot_before_after_join'].values[0] and rdf['frame_rel']['pivot_before_after_join'].values[0] == 'before':
        df_right = pivot_df(df_right, **pivot_arguments)
    # check if composite key
    if ',' in left_on:
        left_on = [x.strip() for x in left_on.split(',')]
    if ',' in right_on:
        right_on = [x.strip() for x in right_on.split(',')]
    # cross join case
    if how == 'cross':
        df_left['fake'] = 1
        df_right['fake'] = 1
        df_result = pd.merge(df_left, df_right, left_on=left_on, right_on=right_on, how='inner')
    # apply the merge for different cases
    else:
        df_result = pd.merge(df_left, df_right, left_on=left_on, right_on=right_on, how=how)
    # check for post-join aggregation
    if rdf['frame_rel']['agg_before_after_join'].values[0] and rdf['frame_rel']['agg_before_after_join'].values[0] == 'after':
        df_result = aggregate_df(df_result, partition_fields, aggregation_fields, rename_fields)
    # check for post-join pivot
    if rdf['frame_rel']['pivot_before_after_join'].values[0] and rdf['frame_rel']['pivot_before_after_join'].values[0] == 'after':
        df_result = pivot_df(df_result, **pivot_arguments)
    # Drop the duplicated columns
    df_result = drop_cols_y(df_result)
    return {'table': rdf['table'], 'frame_data': df_result, 'frame_rel': rdf['frame_rel']}


def combine_multiple_df(list_df, how='H'):
    r"""
    Combine multiple dataframes and return the resulting dataframe
    Parameters:
        - list_df: list of dictionnaries in this format {'frame': dataframe, 'key': <key_value>, 'how': <how>}
        - how: (default='H') how to combine
                H = horizontal (JOIN)
                V = vertical (UNION)
    """
    # if Join-Style
    if how == 'H':
        result = reduce(merge_dfs, list_df)['frame_data']
    else:
        if compare_two_lists(sorted(common_key), sorted(listdf_headers[0])):
            result = pd.concat(listdf)

    return result


def aggregate_df(df, partition_fields, aggregation_fields, rename_fields=None, as_index=False):
    r"""
    Aggregate a dataframe using partition_fields.
    The aggregated fields are calculated using the aggregation_fields.
    Returns a dataframe.
    """
    if partition_fields and aggregation_fields:
        for key, values in aggregation_fields.items():
            if not(isinstance(values, list)):
                values = [values]
            output = []
            for agg in values:
                output.append(cp.AGGREGATION_TYPE[agg])
            if len(output) == 1:
                output = output[0]
            aggregation_fields.update({key: output})
        df = df.groupby(partition_fields, as_index=as_index, sort=False).agg(aggregation_fields)
        #rename post-aggregation
    if rename_fields:
        if df.columns.nlevels > 1:
            df.columns = ['_'.join(col).strip('_') for col in df.columns.values]
        df = df.rename(columns=rename_fields)
    return df


def sort_df(df, sort_fields):
    r"""
    Sort a dataframe using sort_fields.
    Returns a dataframe.
    """
    if sort_fields:
        sort_columns = list(sort_fields.keys())
        sort_options = [True if sort_fields[k] == 'asc' else False for k in sort_columns if k in sort_fields]
        df = df.sort_values(sort_columns, ascending=sort_options)
    return df


def pivot_df(df, index_cols, pivot_field, value_field, aggregation_function=None, dict_rename=None):
    r"""
    Pivot a dataframe using pivot_field.
    Returns a dataframe.
    """
    if pivot_field and index_cols:
        # aggregate the dataframe to avoid duplicate index
        index_df = None
        if aggregation_function:
            dict_agg_value_field = {value_field: aggregation_function}
            partition_fields = [l for l in df.columns if l != value_field]
            df = aggregate_df(df, partition_fields, dict_agg_value_field, as_index=index_cols)
            if not(isinstance(index_cols, list)):
                index_df = df.index.get_level_values(index_cols).unique()
            df = df.reset_index()
        # do the pivot
        if 'object' in str(df[value_field].dtype):
            aggfunc = np.max
        else:
            aggfunc = np.sum
        df_result = df.pivot_table(index=index_cols, columns=pivot_field, values=value_field, aggfunc=aggfunc)
        # rename if necessary
        if dict_rename:
            df_result = df_result.rename(columns=dict_rename)
        # reindex because pivot pandas breaks the index ordering
        if index_df is not None:
            df_result = df_result.reindex(index_df)
        df_result = df_result.reset_index()
    return df_result


def unpivot_df(df, unpivoting_cols, non_moving_cols=None, output_var_name='type', output_value_col='value', pattern_to_remove_from_var_col=None):
    r"""
    Unpivots a dataframe using the parameters:
        - unpivoting_cols: the list of columns to move to row axis
        - non_moving_cols: the columns which should remain unchanged after unpivoting
        - output_var_name: the name for the created column containing the names of unpivoting_cols as values
        - output_value_col: the name of the column to receive the values contained in the unpivoting_cols
        - pattern_to_remove_from_var_col: A string pattern to remove from output_var_name values
    Returns a dataframe.
    """
    # Give default values
    if not(non_moving_cols):
        non_moving_cols = [l for l in df.columns if l not in unpivoting_cols]
    if unpivoting_cols:
        # Use melt function from Pandas
        df = pd.melt(
            df, id_vars=non_moving_cols, value_vars=unpivoting_cols, var_name=output_var_name, value_name=output_value_col
        )
        # Remove prefix from unpivoting_cols to
    if pattern_to_remove_from_var_col:
        df[output_var_name] = df[output_var_name].apply(lambda x: x.replace(pattern_to_remove_from_var_col, ''))
    return df


def compare_df_columns(df_tgt, df_src, sort_fields):
    r"""
    Takes two dataframes df_tgt and df_src and compare them row by row provided their headers are identical.
    Returns a list of dictionaries list_comparison:
        - if one cell's value is different then the whole row is flagged to has_changed and
        dict_comparison = {'index': 1, 'status': 'has_changed', 'log_changes': [{...}]}
        - if nothing has changed dict_flag = {'index': 1, 'status': 'is_identical', 'log_changes': }
    """
    # sort the dfs on pk and set index
    df_src = sort_df(df_src, sort_fields).set_index(list(sort_fields.keys()))
    df_tgt = sort_df(df_tgt, sort_fields).set_index(list(sort_fields.keys()))

    # check has same headers
    if all(x == y for x, y in zip(df_tgt.columns, df_src.columns)):
        list_comparison = []
        # if float columns then need to be rounded
        for col in df_tgt.columns:
            if 'float' in str(df_tgt[col].dtype):
                df_src[col] = df_src[col].apply(lambda x: round(x, 4))
                df_tgt[col] = df_tgt[col].apply(lambda x: round(x, 4))
        for (idx_tgt, row_tgt), (idx_src, row_src) in zip(df_tgt.iterrows(), df_src.iterrows()):
            if idx_tgt == idx_src:
                status = 'is_identical'
                changed_cols = []
                for col in df_tgt.columns:
                    if row_tgt[col] != row_src[col]:
                        status = 'has_changed'
                        changed_cols.append({'col': col, 'from': row_src[col], 'to': row_tgt[col]})
                list_comparison.append({'index': idx_tgt, 'status': status, 'log_changes': changed_cols})
        return list_comparison


def apply_dict_mapping_to_df(df, dict_mapping, optional_index=None, list_comparison=None):
    r"""
    Takes a dataframe table and apply operation to each column described in the dict_mapping
    """
    # Loop through each ouput col of dict_mapping
    if dict_mapping:
        for output_col, subdict in dict_mapping.items():
            # check for rules if it is from one source col
            if 'source_col' in subdict:
                #Check for any type of calculation
                if 'calculation' in subdict:
                    if subdict['calculation'] == 'percentage':
                        df[output_col] = df[subdict['source_col']] / df[subdict['source_col']].sum()
                    if subdict['calculation'] == 'normalization':
                        df[output_col] = normalize_df_col_with_fixed_elements(df, subdict['source_col'], optional_index, list_comparison=list_comparison)
                    if subdict['calculation'] == 'date_add_year':
                        dateformat = identify_date_format(df, subdict['source_col'])
                        df[output_col] = df[subdict['source_col']].apply(lambda x: normalize_date_format(x))
                        if dateformat == 'DATE_US':
                            df[output_col] = df[output_col].apply(pd.to_datetime, format="%m%d%Y", errors='coerce')
                            df[output_col] = df[output_col].apply(lambda x: x + pd.DateOffset(years=1))
                            df[output_col] = df[output_col].apply(lambda x: x.strftime('%m-%d-%Y'))
                        elif dateformat == 'DATE_EU':
                            df[output_col] = df[output_col].apply(pd.to_datetime, format="%d%m%Y", errors='coerce')
                            df[output_col] = df[output_col].apply(lambda x: x + pd.DateOffset(years=1))
                            df[output_col] = df[output_col].apply(lambda x: x.strftime('%d-%m-%Y'))
                        elif dateformat == 'DATE_ISO':
                            df[output_col] = df[output_col].apply(pd.to_datetime, format="%Y%m%d", errors='coerce')
                            df[output_col] = df[output_col].apply(lambda x: x + pd.DateOffset(years=1))
                            df[output_col] = df[output_col].apply(lambda x: x.strftime('%Y-%m-%d'))
                        elif dateformat == 'MONTH_DATE':
                            df[output_col] = df[output_col].apply(pd.to_datetime, format="%d%m%Y", errors='coerce')
                            df[output_col] = df[output_col].apply(lambda x: x + pd.DateOffset(years=1))
                            df[output_col] = df[output_col].apply(lambda x: x.strftime('%m-%Y'))
                        else:
                            df[output_col] = df[output_col].apply(pd.to_datetime, format="%Y%m%d", errors='coerce')
                            df[output_col] = df[output_col].apply(lambda x: x + pd.DateOffset(years=1))
                            df[output_col] = df[output_col].apply(lambda x: x.strftime('%Y-%m'))

                # Otherwise we just map directly
                else:
                    # print(list(df)) ['index']
                    df[output_col] = df[subdict['source_col']]

                if 'default_value' in subdict:
                    if subdict['default_value'] in df.columns:
                        default_value = df[subdict['default_value']]
                    else:
                        default_value = subdict['default_value']
                    df[output_col] = np.where(
                        pd.isnull(df[subdict['source_col']]), default_value,
                        df[subdict['source_col']]
                    )

            else:
                # check for rules without source_col
                if 'default_value' in subdict:
                    df[output_col] = subdict['default_value']
                elif 'calculation' in subdict:
                    if subdict['calculation'] == 'multiplication':
                        df[output_col] = apply_operation_to_df_col(df, subdict['elements'])
                else:
                    df[output_col] = np.NaN
        # keep only output_cols
        df = df[list(dict_mapping.keys())]
    return df


def convert_datetime_col(table):
    r"""
    Takes a dataframe table and convert every column with dtype object in datetime
    if the column values are in a DATETIME format like specified in cluster_params
    """
    table_test = table.head(1000)
    for col in table_test.columns:
        if all(pd.isnull(table_test[col])):
            table_test = table_test.drop(col, 1)
    list_col_candidates = [col for col in table_test.columns if table_test[col].dtype == 'object' and
                           all(is_datetime(str(l)) for l in table_test[col] if not pd.isnull(l))]
    dict_col_datetime = {col: 'datetime_{}'.format(identify_date_format(table, col)) for col in list_col_candidates}
    list_col_datetimedateUS = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_DATE_US']
    list_col_datetimedateEU = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_DATE_EU']
    list_col_datetimedateISO = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_DATE_ISO']
    list_col_datetimemonthdate = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_MONTH_DATE']
    list_col_datetimemonthdateISO = [e for e in dict_col_datetime.keys() if dict_col_datetime[e] == 'datetime_MONTH_DATE_ISO']
    # 2) apply conversion
    if list_col_datetimedateUS:
        table[list_col_datetimedateUS] = table[list_col_datetimedateUS].applymap(lambda x: normalize_date_format(x))
        table[list_col_datetimedateUS] = table[list_col_datetimedateUS].apply(pd.to_datetime, format="%m%d%Y", errors='coerce')
    if list_col_datetimedateEU:
        table[list_col_datetimedateEU] = table[list_col_datetimedateEU].applymap(lambda x: normalize_date_format(x))
        table[list_col_datetimedateEU] = table[list_col_datetimedateEU].apply(pd.to_datetime, format="%d%m%Y", errors='coerce')
    if list_col_datetimedateISO:
        table[list_col_datetimedateISO] = table[list_col_datetimedateISO].applymap(lambda x: normalize_date_format(x))
        table[list_col_datetimedateISO] = table[list_col_datetimedateISO].apply(pd.to_datetime, format="%Y%m%d", errors='coerce')
    if list_col_datetimemonthdate:
        table[list_col_datetimemonthdate] = table[list_col_datetimemonthdate].applymap(lambda x: normalize_date_format(x))
        table[list_col_datetimemonthdate] = table[list_col_datetimemonthdate].apply(pd.to_datetime, format="%d%m%Y", errors='coerce')
    if list_col_datetimemonthdateISO:
        table[list_col_datetimemonthdateISO] = table[list_col_datetimemonthdateISO].applymap(lambda x: normalize_date_format(x))
        table[list_col_datetimemonthdateISO] = table[list_col_datetimemonthdateISO].apply(pd.to_datetime, format="%Y%m%d", errors='coerce')


def convert_numeric_col(table):
    r"""
    Takes a dataframe table and convert every column with dtype object in either float or integer
    if the column values are in a FORMAT_FLOAT or FORMAT_INT format like specified in cluster_params
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
            dict_count_format['integer'] = sum([1 if is_integer(l) else 0 for l in table_test[col] if not pd.isnull(l)]) / total_count
            dict_count_format['float'] = sum([1 if is_float(l) else 0 for l in table_test[col] if not pd.isnull(l)]) / total_count
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
        table[list_col_int] = table[list_col_int].applymap(lambda x: normalize_numeric_format(x))  # Decision to separate INT and FLOAT although same functions applied
        table[list_col_int] = table[list_col_int].apply(pd.to_numeric, errors='coerce')
    if list_col_float:
        table[list_col_float] = table[list_col_float].replace('-', np.NaN)
        table[list_col_float] = table[list_col_float].applymap(lambda x: normalize_numeric_format(x))
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


def convert_dict_values_to_related_df_dtype(dataframe, inputdict):
    r"""
    First try to match the dictionnary keys to the dataframe column names.
    Returns the dict argument with values converted to the respective dtypes
    """
    dict_converted = {}
    for key, values in inputdict.items():
        if key in dataframe.columns:
            if 'datetime' in str(dataframe[key].dtype):
                dict_converted[key] = [convert_string_to_datetime(l) for l in values]
            if 'float' in str(dataframe[key].dtype):
                dict_converted[key] = [convert_string_to_float(l) for l in values]
            if 'int' in str(dataframe[key].dtype):
                dict_converted[key] = [convert_string_to_int(l) for l in values]
            else:
                dict_converted[key] = values
        else:
            continue
    return dict_converted


def normalize_df_col_with_fixed_elements(df, col, index=None, list_comparison=None):
    r"""
    This function normalizes the float col of df so that total equals to 1
    """
    # set index if necessary
    if index:
        df = df.set_index(index)
    # with list_comparison
    if list_comparison:
        # build dataframe based on list_comparison
        list_values = []
        for d in list_comparison:
            for dict_changes in d['log_changes']:
                if dict_changes['col'] == col:
                    list_values.append({'index': d['index'], 'from': dict_changes['from'], 'to': dict_changes['to']})
        df_info = pd.DataFrame(list_values, columns=['index', 'from', 'to'])
        # check whether we are still in this case
        if df_info.empty or df_info.shape[0] == df.shape[0]:
            # apply simple normalization
            # reset index
            df = df.reset_index()
            df[col] = df[col] / df[col].sum()
        else:
            # updates have to remain fix
            total_remain_before = 0
            for idx, row in df.iterrows():
                if idx not in df_info['index'].values.tolist():
                    total_remain_before += row[col]
            total_remain_after = total_remain_before - sum(df_info['to'] - df_info['from'])
            list_tmp = []
            for idx, row in df.iterrows():
                if idx not in df_info['index'].values.tolist():
                    row[col] = row[col] * total_remain_after / total_remain_before
                list_tmp.append(row[col])
            df[col] = pd.Series(list_tmp, index=df.index)
            # reset index
            df = df.reset_index()
    else:
        # apply simple normalization
        df[col] = df[col] / df[col].sum()
    return df[col]


def apply_operation_to_df_col(df, list_operands, external_filters=None):
    r"""
    Generic Function which apply operation on a list of dataframe columns
    """
    list_multiplication = []
    for obj in list_operands:
        if isinstance(obj, dict):
            engine = db_connect()
            filter_fields = adapt_filter_to_table(engine, obj['from_table'], external_filters)
            df_elt = get_table_to_df(engine, obj['from_table'], filter_fields)
            col = obj['from_col']
        else:
            df_elt = df
            col = obj
        match = re.match(r'sum\((.*)\)', col)
        if match and match.group(1) in df_elt.columns:
            df_elt['tmp'] = df_elt[match.group(1)].sum()
            list_multiplication.append(df_elt['tmp'])
        elif col in df_elt.columns:
            list_multiplication.append(df_elt[col])
    return reduce(lambda x, y: x * y, list_multiplication)


def append_total_row(df, dict_formatting, is_total_top_row=False):
    r"""
    This function aggregates the dataframe to calculate the total for each numeric column
    If the is_total_top_row is True then the row will be appended at the top of the dataframe, by default
    it's appended at the bottom.
    """
    cols = df.columns.tolist()
    # Build the total row
    df['fake'] = 'fake'
    aggregation_fields = {}
    for col, formatting in dict_formatting.items():
        if formatting == '{:,.2f}':
            aggregation_fields[col] = 'max'
        else:
            aggregation_fields[col] = 'sum'
    df_total = aggregate_df(df, partition_fields=['fake'], aggregation_fields=aggregation_fields)
    total_is_written = False
    for col in df.columns:
        if col not in list(dict_formatting.keys()):
            df_total[col] = ''
        if not(total_is_written):
            df_total[col] = 'TOTAL'
            total_is_written = True

    # Append the total row
    if is_total_top_row:
        df_result = df_total.append(df, ignore_index=True)
    else:
        df_result = df.append(df_total, ignore_index=True)
    return df_result[cols]


def generic_split_to_target_level(df_src, dict_param):
    r'''
    This function breaks the numerical data from a source aggregation level
    down to a target aggregation level.

    Args:
        df_src: DataFrame containing the values to break down to target level
        dict_param: a dictionnary of useful parameters
            - table_name: backend table storing the data at lowest level possible
            - aggregation_level_src: column or list of columns used for aggregating the input data
            - aggregation_level_tgt: column or list of columns used for splitting the data to
            - filter_fields: if any
            - [OPTIONAL] dict_aggregation: specfies how the columns must be aggregated

    Returns:
        DataFrame with values broken down to target level
    '''
    # extract table_name to dataframe
    engine = db_connect()
    aggregation_global = dict_param['aggregation_level_src'] + list(set(dict_param['aggregation_level_tgt']) - set(dict_param['aggregation_level_src']))
    df_tgt = get_table_to_df(engine, dict_param['table_name'], dictfilter=dict_param['filter_fields'])
    if 'dict_aggregation' in dict_param:
        aggregation_fields = dict_param['dict_aggregation']
    else:
        aggregation_fields = {
            col: 'sum' for col in df_src.columns if col not in dict_param['aggregation_level_src'] and ('int' in str(df_src[col].dtype) or 'float' in str(df_src[col].dtype))
        }
    df_src_before = aggregate_df(df_tgt, partition_fields=dict_param['aggregation_level_src'], aggregation_fields=aggregation_fields)
    # compare before and after UI modification and normalize accordingly
    compare_cols = [col for col in dict_param['aggregation_level_src'] + list(aggregation_fields.keys())]
    sort_cols = dict_param['aggregation_level_src'] if isinstance(dict_param['aggregation_level_src'], list) else [dict_param['aggregation_level_src']]
    sort_dict = {col: 'asc' for col in sort_cols}
    list_comparison = compare_df_columns(df_src[compare_cols], df_src_before[compare_cols], sort_dict)
    for col in list(aggregation_fields.keys()):
        df_src[col] = normalize_df_col_with_fixed_elements(df_src, col, dict_param['aggregation_level_src'], list_comparison=list_comparison)
    # prepare target dataframe
    #df_tgt = aggregate_df(df_tgt, partition_fields=aggregation_global, aggregation_fields=aggregation_fields)

    # initialize list of frames
    list_frames = []
    for idx, row in df_src.iterrows():
        df_tgt_tmp = df_tgt
        # filter the target level based on source level
        for col in dict_param['aggregation_level_src']:
            df_tgt_tmp = df_tgt_tmp[df_tgt_tmp[col] == row[col]]

        for col in list(aggregation_fields.keys()):
            # calculate the percentages
            percent_col = col + 'percent'
            index = dict_param['aggregation_level_tgt'][0] if len(dict_param['aggregation_level_tgt']) == 1 else dict_param['aggregation_level_tgt']
            df_tgt_tmp[percent_col] = normalize_df_col_with_fixed_elements(df_tgt_tmp, col)
            df_tgt_tmp[col] = df_tgt_tmp[percent_col] * row[col]
            df_tgt_tmp = df_tgt_tmp.drop(percent_col, 1)

        # append to list_frames
        list_frames.append(df_tgt_tmp)
    # concatenate
    df = pd.concat(list_frames)
    return df
