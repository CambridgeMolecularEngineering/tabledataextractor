# -*- coding: utf-8 -*-
"""
tabledataextractor.input.from_html.py

Reads an html formatted table.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""


import numpy as np
from bs4 import BeautifulSoup
import copy
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def makearray(html_table):
    """
    Creates a numpy array from an html file, taking rowspan and colspan into account.
    Modified from:  John Ricco, https://johnricco.github.io/2017/04/04/python-html/
        'Using Python to scrape HTML tables with merged cells'
    Added functionality for duplicating cell content for cells with rowspan/colspan.
    """
    n_cols = 0
    n_rows = 0

    for row in html_table.findAll("tr"):
        col_tags = row.find_all(["td", "th"])
        if len(col_tags) > 0:
            n_rows += 1
            if len(col_tags) > n_cols:
                n_cols = len(col_tags)

    # according to numpy documentation fill_value should be of type Union[int, float, complex]
    # however, 'str' works just fine
    array = np.full((n_rows,n_cols), fill_value="", dtype='<U30')

    # list to store rowspan values
    skip_index = [0 for i in range(0, n_cols)]

    # iterating over each row in the table
    row_counter = 0
    for row in html_table.findAll("tr"):

        # skip row if it's empty
        if len(row.find_all(["td", "th"])) == 0:
            continue

        else:

            # get all the cells containing data in this row
            columns = row.find_all(["td", "th"])
            col_dim = []
            row_dim = []
            col_dim_counter = -1
            row_dim_counter = -1
            col_counter = -1
            this_skip_index = copy.deepcopy(skip_index)

            for col in columns:

                # determine all cell dimensions
                colspan = col.get("colspan")
                if not colspan:
                    col_dim.append(1)
                else:
                    col_dim.append(int(colspan))
                col_dim_counter += 1

                rowspan = col.get("rowspan")
                if not rowspan:
                    row_dim.append(1)
                else:
                    row_dim.append(int(rowspan))
                row_dim_counter += 1

                # adjust column counter
                if col_counter == -1:
                    col_counter = 0
                else:
                    col_counter = col_counter + col_dim[col_dim_counter - 1]

                while skip_index[col_counter] > 0:
                    col_counter += 1

                # get cell contents
                cell_data = col.get_text()

                # insert data into cell
                array[row_counter, col_counter] = cell_data

                # TODO Insert data into neighbouring rowspan/colspan cells
                # DO I STILL NEED THE UPPER ROW THEN?, JUST ABOVE?
                for spanned_col in col_dim:
                    array[row_counter, col_counter + spanned_col-1] = cell_data
                for spanned_row in row_dim:
                    array[row_counter + spanned_row-1, col_counter] = cell_data

                #record column skipping index
                if row_dim[row_dim_counter] > 1:
                    this_skip_index[col_counter] = row_dim[row_dim_counter]

        # adjust row counter
        row_counter += 1

        # adjust column skipping index
        skip_index = [i - 1 if i > 0 else i for i in this_skip_index]

    return array


def read(file_path):
    """Method used to read an .html file and return a numpy array"""
    file = open(file_path, encoding='UTF-8')
    html_table = BeautifulSoup(file, features='lxml')
    file.close()
    #list = makelist(html_table)
    array = makearray(html_table)
    return array

