import pandas as pd

def extract(source_path):
    return pd.read_html(source_path)[0]

def df_to_html(df, source_path):
    df.to_html(source_path, index=False)
