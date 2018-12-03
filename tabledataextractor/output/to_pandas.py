# -*- coding: utf-8 -*-
"""
Outputs the table to a Pandas DataFrame.
"""

import pandas as pd
import numpy as np

def to_pandas (table):
    """
    Creates a Pandas DataFrame from a Table object

    :param table: Table object
    :return:
    """
    index_row = pd.MultiIndex.from_arrays(table.row_header.T)
    index_col = pd.MultiIndex.from_arrays(table.col_header)
    df = pd.DataFrame(columns=index_col, index=index_row, data=table.data)
    return df

def find_multiindex_level(row_number,column_number,df):
    result_index = []
    if hasattr(df.index,'labels'):
        for i,labels in enumerate(df.index.labels):
            result_index.append(df.index.levels[i][labels[row_number]])
    else:
        result_index.append(df.index[row_number])
    result_column = []
    if hasattr(df.columns,'labels'):
        for i,labels in enumerate(df.columns.labels):
            result_column.append(df.columns.levels[i][labels[column_number]])
    else:
        result_column.append(df.columns[column_number])
    return result_index,result_column

def print_category_table(df):
    values = df.values  # data is converted to numpy array
    print("{:11s} {:10s} {:36s} {:20s}".format("Cell_ID", "Data", "Row Categories", "Column Categories"))
    for i, row in enumerate(values):
        for j, cell in enumerate(row):
            categories = find_multiindex_level(i, j, df)
            print("{:3} {:3} {:15}   {:35}  {:40}".format(i, j, str(cell), ''.join(str(categories[0])), ''.join(str(categories[1]))))

def build_category_table(df):
    values = df.values  # data is converted to numpy array

    n_rows = np.size(values)

    category_table = np.full((n_rows, 3), r"/", dtype="<U60")

    counter = 0
    for i, row in enumerate(values):
        for j, cell in enumerate(row):

            categories = find_multiindex_level(i, j, df)
            category_table[counter, 0] = cell

            # TODO Play with this, I want the categories to be nested arrays
            category_table[counter, 1] = str(categories[0])
            category_table[counter, 2] = str(categories[1])

            counter += 1

    return category_table
