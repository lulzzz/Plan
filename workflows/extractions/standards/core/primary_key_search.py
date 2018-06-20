import itertools
import pandas as pd

def suggest_primary_key(df):
    r"""Returns a tuple of selected columns"""

    found_unique = False
    suggestions = list()
    for col in df.columns:
        if len(df[col].unique()) / df.shape[0] == 1:
            found_unique = True
            suggestions.append((col))

    if not found_unique:
        for r in range(2, df.columns.shape[0]):
            groupings = itertools.combinations(df.columns, r)
            for grouping in groupings:
                sum_max_count = df.groupby(grouping).count().max().sum()
                remaining_columns = df.columns.shape[0]-r
                if sum_max_count == remaining_columns:
                    suggestions.append(grouping)

    selections = dict()
    for idx, suggestion in enumerate(suggestions):
        selections[idx] = suggestion

    print('Please select among:', selections)
    choice = -1
    while int(choice) not in selections:
        choice = input('Input ID:')
        if int(choice) not in selections:
            print('Wrong choice, please select among:', selections)

    selected = suggestions[int(choice)]

    print('Selected:', selected)

    return selected
