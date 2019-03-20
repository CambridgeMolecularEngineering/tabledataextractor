# -*- coding: utf-8 -*-
"""
Outputs the table to a Pandas DataFrame.
"""

import pandas as pd


def to_pandas(table):
    """
    Creates a `Pandas <http://pandas.pydata.org/>`_ `DataFrame` object from a :class:`~tabledataextractor.table.table.Table` object.

    :param table: Input table
    :type table: ~tabledataextractor.table.table.Table
    :return: :class:`pandas.DataFrame`
    """
    index_row = pd.MultiIndex.from_arrays(table.row_header.T)
    index_col = pd.MultiIndex.from_arrays(table.col_header)
    df = pd.DataFrame(columns=index_col, index=index_row, data=table.data)
    return df


def find_multiindex_level(row_number, column_number, df):
    """
    Helping function for ``build_category_table()``.
    Finds the `Pandas` `MultiIndex level` in a given `Pandas` `DataFrame`, for a particular data value.
    """
    result_index = []
    if hasattr(df.index, 'labels'):
        for i,labels in enumerate(df.index.labels):
            result_index.append(df.index.levels[i][labels[row_number]])
    else:
        result_index.append(df.index[row_number])
    result_column = []
    if hasattr(df.columns, 'labels'):
        for i, labels in enumerate(df.columns.labels):
            result_column.append(df.columns.levels[i][labels[column_number]])
    else:
        result_column.append(df.columns[column_number])
    return result_index, result_column


def print_category_table(df):
    """
    Prints the category table to screen, from `Pandas DataFrame` input

    :param df: Pandas DataFrame input
    :type df: pandas.DataFrame
    """
    values = df.values  # data is converted to numpy array
    print("{:11s} {:10s} {:36s} {:20s}".format("Cell_ID", "Data", "Row Categories", "Column Categories"))
    for i, row in enumerate(values):
        for j, cell in enumerate(row):
            categories = find_multiindex_level(i, j, df)
            print("{:3} {:3} {:15}   {:35}  {:40}".format(i, j, str(cell), ''.join(str(categories[0])), ''.join(str(categories[1]))))


def build_category_table(df):
    """
    Builds the category table in form of a Python list, from `Pandas DataFrame` input

    :param df: Pandas DataFrame input
    :type df: pandas.DataFrame
    :return: category_table as Python list
    """
    values = df.values  # data is converted to numpy array
    category_table = []
    for i, row in enumerate(values):
        for j, cell in enumerate(row):
            data_point = []
            categories = find_multiindex_level(i, j, df)
            data_point.append(cell)
            data_point.append(categories[0])
            data_point.append(categories[1])
            category_table.append(data_point)
    return category_table
