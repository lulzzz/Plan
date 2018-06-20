import pandas as pd
import ezodf

def extract(source_path, sheet_no=0, header=0):
    tab = ezodf.opendoc(filename=source_path).sheets[sheet_no]
    return pd.DataFrame({col[header].value:[x.value for x in col[header+1:]]
                         for col in tab.columns()})
