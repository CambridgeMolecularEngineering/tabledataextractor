# -*- coding: utf-8 -*-
"""
Functions for printing to screen in a nice format.
"""

import logging
import numpy as np
from prettytable import PrettyTable

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


def print_table(table):
    """
    Prints a table to screen.

    :param table: input numpy array for printing
    :type table: ndarray
    """
    n_columns = table.shape[1]
    cell_width = np.zeros(n_columns, dtype=int)

    # find the maximum cell width for each column i
    for i, column in enumerate(table.T):
        for cell in column:
            if len(cell) > cell_width[i]:
                cell_width[i] = len(cell)

    # print each row
    for row in table:
        for i, cell in enumerate(row):
            print("{:{cell_width}} ".format(cell,cell_width=cell_width[i]+1), end='', flush=True)
        print("\n", end='', flush=True)
    print("\n", flush=True)


def as_string(table):
    """
    Returns table as string for printing.

    :param table: input numpy array
    :type table: ndarray
    :return: string
    """
    n_columns = table.shape[1]
    cell_width = np.zeros(n_columns, dtype=int)
    output = ''

    # find the maximum cell width for each column i
    for i, column in enumerate(table.T):
        for cell in column:
            if len(cell) > cell_width[i]:
                cell_width[i] = len(cell)

    # print each row
    for row in table:
        for i, cell in enumerate(row):
            output += "{:{cell_width}} ".format(cell, cell_width=cell_width[i]+1)
        output += "\n"
    output += "\n"
    return output


def list_as_PrettyTable(table_list):
    """
    Turns list into :class:`PrettyTable` object, ready for printing.

    :param table_list: list to be printed
    :return: table as `PrettyTable <https://pypi.org/project/PrettyTable/>`_

    """
    t = PrettyTable()
    t.field_names = ["Data", "Row Categories", "Column Categories"]
    for row in table_list:
        t.add_row(row)
    return t

