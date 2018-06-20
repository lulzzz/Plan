from django.conf import settings as cp


def apply_rule_list(input_df, rule_list):
    r"""
    Transformation rules controller
    """

    # Cleansing empty columns
    # Cleansing duplicated headers
    # Cleansing empty rows
    # Cleansing rows with less than treshhold available data

    df = input_df
    for rule in rule_list:
        df_metadata = find_df_metadata(df)

        if rule is 1:
            df = rule_001(df, df_metadata)
        if rule is 2:
            df = rule_002(df, df_metadata)
        if rule is 3:
            df = rule_003(df, df_metadata)
        if rule is 4:
            df = rule_004(df, df_metadata)

    return df


def find_df_metadata(df):
    r"""
    Find the metadata needed for the rules (generic)
    """
    return None


def rule_001(df, df_metadata):
    r"""
    Pivot cell values in first non empty row into column on left side of df
    """
    return df


def rule_002(df, df_metadata):
    r"""
    Define first non empty row as header
    """
    return df


def rule_003(df, df_metadata):
    r"""
    Remove all empty rows in dataframe
    """
    return df

def rule_004(df, df_metadata):
    r"""
    Removes remarks aside tables and returns table without them
    """
    print('Rule', cp.AVAILABLE_RULE_LIST[3].get(4))

    # Define variables
    null_threshold = 0.9

    # right left
    n_col = df.shape[1]
    n_row = df.shape[0]
    for col_left in range(n_col-1, 0, -1):
        edge_column = df.iloc[:, col_left]
        null_ratio = edge_column.isnull().sum() / n_row
        if null_ratio < null_threshold:
            break

    # left right
    for col_right in range(n_col-1):
        edge_column = df.iloc[:, col_right]
        null_ratio = edge_column.isnull().sum() / n_row
        if null_ratio < null_threshold:
            break

    # down up
    for row_number in range(n_row-1, 0, -1):
        edge_row = df.iloc[row_number]
        null_ratio = edge_row.isnull().sum() / n_col
        if null_ratio < null_threshold:
            break

    return df.iloc[:row_number+1, col_right:col_left+1]
