import pandas as pd

def extract(source_path):
    return pd.read_json(source_path, orient='records')

def df_to_json(df, target_path):
    df.to_json(target_path, orient='records') # Create file
