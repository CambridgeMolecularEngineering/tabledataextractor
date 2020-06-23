# -*- coding: utf-8 -*-
"""
Algorithms for TableDataExtractor.

.. codeauthor:: Juraj Mavračić <jm2111@cam.ac.uk>

"""

import logging
import numpy as np
from sympy import Symbol
from sympy import factor_list, factor

from tabledataextractor.exceptions import MIPSError
from tabledataextractor.table.parse import StringParser, CellParser


log = logging.getLogger(__name__)


def empty_string(string, regex=r'^([\s\-\–\—\"]+)?$'):
    """
    Returns `True` if a particular string is empty, which is defined with a regular expression.

    :param string: Input string for testing
    :type string: str
    :param regex: The regular expression which defines an empty cell (can be tweaked).
    :type regex: str
    :return: True/False
    """
    empty_parser = StringParser(regex)
    return empty_parser.parse(string, method='fullmatch')


def empty_cells(array, regex=r'^([\s\-\–\—\"]+)?$'):
    """
    Returns a mask with `True` for all empty cells in the original array and `False` for non-empty cells.

    :param regex: The regular expression which defines an empty cell (can be tweaked).
    :type regex: str
    :param array: Input array to return the mask for
    :type array: numpy array
    """
    empty = np.full_like(array, fill_value=False, dtype=bool)
    empty_parser = CellParser(regex)
    for empty_cell in empty_parser.parse(array, method='fullmatch'):
        if array.ndim == 2:
            empty[empty_cell[0], empty_cell[1]] = True
        elif array.ndim == 1:
            empty[empty_cell[0]] = True
    return empty


def standardize_empty(array):
    """
    Returns an array with the empty cells of the input array standardized to 'NoValue'.

    :param array: Input array
    :type array: numpy.array
    :return: Array with standardized empty cells
    """
    standardized = np.copy(array)
    for row_index, row in enumerate(standardized):
        for col_index, col in enumerate(row):
            if empty_string(col):
                standardized[row_index, col_index] = 'NoValue'
    return standardized


def pre_clean(array):
    """
    Removes empty and duplicate rows and columns that extend over the whole table.

    :param array: Input Table object
    :type array: Numpy array
    """

    pre_cleaned_table = np.copy(array)
    array_empty = empty_cells(array)

    # find empty rows and delete them
    empty_rows = []
    for row_index, row in enumerate(array_empty):
        if False not in row:
            empty_rows.append(row_index)
    log.debug("Empty rows {} deleted.".format(empty_rows))
    pre_cleaned_table = np.delete(pre_cleaned_table, empty_rows, axis=0)

    # find empty columns and delete them
    empty_columns = []
    for column_index, column in enumerate(array_empty.T):
        if False not in column:
            empty_columns.append(column_index)
    log.debug("Empty columns {} deleted.".format(empty_columns))
    pre_cleaned_table = np.delete(pre_cleaned_table, empty_columns, axis=1)

    # delete duplicate rows that extend over the whole table
    _, indices = np.unique(pre_cleaned_table, axis=0, return_index=True)
    # for logging only, which rows have been removed
    removed_rows = []
    for row_index in range(0, len(pre_cleaned_table)):
        if row_index not in indices:
            removed_rows.append(row_index)
    log.debug("Duplicate rows {} removed.".format(removed_rows))
    # deletion:
    pre_cleaned_table = pre_cleaned_table[np.sort(indices)]

    # delete duplicate columns that extend over the whole table
    _, indices = np.unique(pre_cleaned_table, axis=1, return_index=True)
    # for logging only, which rows have been removed
    removed_columns = []
    for column_index in range(0, len(pre_cleaned_table.T)):
        if column_index not in indices:
            removed_columns.append(column_index)
    log.debug("Duplicate columns {} removed.".format(removed_columns))
    # deletion:
    pre_cleaned_table = pre_cleaned_table[:, np.sort(indices)]

    # clean-up unicode characters
    pre_cleaned_table = clean_unicode(pre_cleaned_table)

    return pre_cleaned_table


def clean_unicode(array):
    """
    Replaces problematic unicode characters in a given numpy array.
    :param array: input array
    :type array: numpy.array
    :return: cleaned array
    """
    temp = np.copy(array)
    temp = np.core.defchararray.replace(temp, '\xa0', ' ')
    return temp


def find_cc4(table_object):
    """
    Searches for critical cell `CC4`.

    Searching from the bottom of the pre-cleaned table for the last row with a minority of empty cells.
    Rows with at most a few empty cells are assumed to be part of the data region rather than notes or footnotes rows
    (which usually only have one or two non-empty cells).

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    :return: cc4
    """
    # searching from the bottom of original table:
    n_rows = len(table_object.pre_cleaned_table)
    for row_index in range(n_rows - 1, -1, -1):
        # counting the number of full cells
        # if n_empty < n_full terminate, this is our goal row
        n_full = 0
        n_columns = len(table_object.pre_cleaned_table_empty[row_index])
        for empty in table_object.pre_cleaned_table_empty[row_index]:
            if not empty:
                n_full += 1
            if n_full > int(n_columns / 2):
                return row_index, n_columns - 1


def duplicate_rows(table):
    """
    Returns True if there are duplicate rows in the table and False if there are no duplicate rows
    :param table:
    :return: True or False
    """
    if table.ndim > 0 and table.size:
        _, indices = np.unique(table, axis=0, return_index=True)
        if len(table) > len(indices):
            return True
        else:
            return False
    else:
        return False


def duplicate_columns(table):
    """
    Returns True if there are duplicate columns in the table and False if there are no duplicate columns
    :param table:
    :return: True or False
    """
    if table.T.ndim > 0 and table.T.size:
        _, indices = np.unique(table.T, axis=0, return_index=True)
        if len(table.T) > len(indices):
            return True
        else:
            return False
    else:
        return False


def find_cc1_cc2(table_object, cc4, array):
    """
    Main MIPS (*Minimum Indexing Point Search*) algorithm. According to Embley et al., *DOI: 10.1007/s10032-016-0259-1*.
    Searches for critical cells `CC2` and `CC3`.
    MIPS locates the critical cells that define the minimum row and column headers needed to index
    every data cell.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    :param cc4: Position of `CC4` cell found with ``find_cc4()``
    :param array: table to search for `CC1` and `CC2`
    :type array: numpy array
    :type cc4: (int, int)
    :return: cc1, cc2
    """

    # Initialize
    cc2 = None
    c_max = cc4[1]
    r_max = cc4[0]
    r1 = 0
    c1 = 0
    r2 = r_max - 1
    c2 = 0
    max_area = 0

    def table_slice_cc2(table, r2, r_max, c1, c2):
        """
        Function to cut the correct slices out of array for `CC2 `in ``find_cc1_cc2()``.
        Cuts out the next row and column header candidates from the pre-cleaned table.

        :param table: pre-cleaned table
        :param r2: current r2 parameter in MIPS algorithm
        :param r_max: r_max parameter in MIPS algorithm
        :param c1: first column for MIPS algorithm
        :param c2: current c2 parameter for MIPS algorithm
        :return: (section_1, section_2)
        """

        # one more row and column index than in the published pseudocode is needed,
        # since the a:b notation in python doesn't include b
        if r2 + 1 == r_max and c1 == c2:
            section_1 = table[r2 + 1, c1]
        elif r2 + 1 == r_max and c1 != c2:
            section_1 = table[r2 + 1, c1:c2 + 1]
        elif r2 + 1 != r_max and c1 != c2:
            section_1 = table[r2 + 1:r_max + 1, c1:c2 + 1]
        elif r2 + 1 != r_max and c1 == c2:
            section_1 = table[r2 + 1:r_max + 1, c1]
        else:
            log.critical("Not defined section_1, r2+1= {}, r_max= {}, c1= {}, c2= {}".format(r2 + 1, r_max, c1, c2))
            section_1 = None

        # contrary to the published pseudocode the row maximum is r2, not r2-1
        # one more row and column index than in the published pseudocode is needed,
        # since the a:b notation in python doesn't include b
        if r1 == r2 and c2 + 1 == c_max:
            section_2 = table[r1, c2 + 1]
        elif r1 == r2 and c2 + 1 != c_max:
            section_2 = table[r1, c2 + 1: c_max + 1]
        elif r1 != r2 and c2 + 1 != c_max:
            section_2 = table[r1: r2 + 1, c2 + 1: c_max + 1]
        elif r1 != r2 and c2 + 1 == c_max:
            section_2 = table[r1: r2 + 1, c2 + 1]
        else:
            log.critical(
                "Not defined section_2, r2-1= {}, r1= {}, c2+1= {}, c_max= {}".format(r2 - 1, r1, c2 + 1, c_max))
            section_2 = None

        return section_1, section_2

    def table_slice_1_cc1(table, r1, r2, c2, c_max):
        """
        Function to cut a correct slice out of array for CC1 in _find_cc1_cc2().
        Cuts out the column header.
        """
        # one more row and column index than in the published pseudocode is needed,
        # since the a:b notation in python doesn't include b
        # contrary to the published pseudocode, the correct range is [r1:r2,c2+1:c_max] and not [r1+1:r2,c2+1:c_max]
        if r1 == r2 and c2 + 1 == c_max:
            section = table[r1, c2 + 1]
        elif r1 == r2 and c2 + 1 != c_max:
            section = table[r1, c2 + 1:c_max + 1]
        elif r1 != r2 and c2 + 1 != c_max:
            section = table[r1: r2 + 1, c2 + 1:c_max + 1]
        elif r1 != r2 and c2 + 1 == c_max:
            section = table[r1: r2 + 1, c2 + 1]
        else:
            log.critical(
                "Not defined section 1 for cc1, r1+1= {}, r2= {}, c2+1= {}, c_max= {}".format(r1 + 1, r2, c2 + 1,
                                                                                              c_max))
            section = None
        return section

    def table_slice_2_cc1(table, r2, r_max, c1, c2):
        """
        Function to cut a correct slice out of array for CC1 in _find_cc1_cc2().
        Cuts out the row header.
        """
        # one more row and column index than in the published pseudocode is needed,
        # since the a:b notation in python doesn't include b
        # contrary to the published pseudocode, the correct range is [r2:r_max,c1:c2] and not [r2+1:c2,c1+1:r_max]
        if r2 == r_max and c1 == c2:
            section = table[r2, c1]
        elif r2 == r_max and c1 != c2:
            section = table[r2, c1: c2 + 1]
        elif r2 != r_max and c1 != c2:
            section = table[r2: r_max + 1, c1: c2 + 1]
        elif r2 != r_max and c1 == c2:
            section = table[r2: r_max + 1, c1]
        else:
            log.critical(
                "Not defined section 2 for cc1, r2+1= {}, c2= {}, c1+1= {}, r_max= {}".format(r2 + 1, c2, c1 + 1,
                                                                                              r_max))
            section = None
        return section

    # MAIN MIPS algorithm
    # Locate candidate MIPs by finding the minimum indexing headers:
    # This is significantly altered compared to the published pseudocode, which is flawed.
    # The pseudocode clearly does not return cc2 if the column has not been changed and it doesn't
    # discriminate between duplicate rows in the row header vs duplicate columns in the column header
    while c2 < c_max and r2 >= r1:

        log.debug("Entering loop:  r_max= {}, c_max= {}, c1= {}, c2= {}, r1= {}, r2= {}, cc2= {}"
                  .format(r_max, c_max, c1, c2, r1, r2, cc2))

        temp_section_1, temp_section_2 = table_slice_cc2(array, r2, r_max, c1, c2)

        log.debug("temp_section_1:\n{}".format(temp_section_1))
        log.debug("temp_section_2:\n{}".format(temp_section_2))
        log.debug("duplicate_rows= {}, duplicate_columns= {}".
                  format(duplicate_rows(temp_section_1), duplicate_rows(temp_section_2)))

        if not duplicate_rows(temp_section_1) and not duplicate_columns(temp_section_2):
            if table_object.configs['use_max_data_area']:
                data_area = (r_max - r2) * (c_max - c2)
                log.debug("The data area of the new candidate C2= {} is *1: {}".format((r2, c2), data_area))
                log.debug("Data area:\n{}".format(array[r2 + 1:r_max + 1, c2 + 1:c_max + 1]))
                if data_area >= max_area:
                    max_area = data_area
                    cc2 = (r2, c2)
                    log.debug("CC2= {}".format(cc2))
                r2 = r2 - 1
            else:
                cc2 = (r2, c2)
                log.debug("CC2= {}".format(cc2))
                r2 = r2 - 1
        elif duplicate_rows(temp_section_1) and not duplicate_columns(temp_section_2):
            c2 = c2 + 1
            if table_object.configs['use_max_data_area']:
                data_area = (r_max - r2) * (c_max - c2)
                log.debug("The data area of the new candidate C2= {} is *2: {}".format((r2, c2), data_area))
                log.debug("Data area:\n{}".format(array[r2 + 1:r_max + 1, c2 + 1:c_max + 1]))
                if data_area >= max_area:
                    max_area = data_area
                    cc2 = (r2, c2)
                    log.debug("CC2= {}".format(cc2))
            else:
                cc2 = (r2, c2)
                log.debug("CC2= {}".format(cc2))
        elif duplicate_rows(temp_section_1) and duplicate_columns(temp_section_2):
            c2 = c2 + 1
            r2 = r2 + 1
            if table_object.configs['use_max_data_area']:
                data_area = (r_max - r2) * (c_max - c2)
                log.debug("The data area of the new candidate C2= {} is *3: {}".format((r2, c2), data_area))
                log.debug("Data area:\n{}".format(array[r2 + 1:r_max + 1, c2 + 1:c_max + 1]))
                if data_area >= max_area:
                    max_area = data_area
                    cc2 = (r2, c2)
                    log.debug("CC2= {}".format(cc2))
            else:
                cc2 = (r2, c2)
        # if none of those above is satisfied, just finish the loop
        else:
            r2 = r2 + 1
            if table_object.configs['use_max_data_area']:
                data_area = (r_max - r2) * (c_max - c2)
                log.debug("The data area of the new candidate C2= {} is *4: {}".format((r2, c2), data_area))
                log.debug("Data area:\n{}".format(array[r2 + 1:r_max + 1, c2 + 1:c_max + 1]))
                if data_area >= max_area:
                    max_area = data_area
                    cc2 = (r2, c2)
                    log.debug("CC2= {}".format(cc2))
                break
            else:
                cc2 = (r2, c2)
                break

    log.debug(
        "Ended loop with:  r_max= {}, c_max= {}, c1= {}, c2= {}, r1= {}, r2= {}, cc2= {}\n\n\n\n".format(r_max,
                                                                                                         c_max, c1,
                                                                                                         c2, r1, r2,
                                                                                                         cc2))

    # re-initialization of r2 and c2 from cc2; missing in the pseudocode
    r2 = cc2[0]
    c2 = cc2[1]

    # Locate CC1 at intersection of the top row and the leftmost column necessary for indexing:
    log.debug("Potentially duplicate columns:\n{}".format(table_slice_1_cc1(array, r1, r2, c2, c_max)))
    while not duplicate_columns(table_slice_1_cc1(array, r1, r2, c2, c_max)) and r1 <= r2:
        log.debug("Potentially duplicate columns:\n{}".format(table_slice_1_cc1(array, r1, r2, c2, c_max)))
        log.debug("Duplicate columns= {}".format(duplicate_columns(table_slice_1_cc1(array, r1, r2, c2, c_max))))
        r1 = r1 + 1
        log.debug("r1= {}".format(r1))

    log.debug("Potentially duplicate rows:\n{}".format(table_slice_2_cc1(array, r2, r_max, c1, c2)))
    while not duplicate_rows(table_slice_2_cc1(array, r2, r_max, c1, c2)) and c1 <= c2:
        log.debug("Potentially duplicate rows:\n{}".format(table_slice_2_cc1(array, r2, r_max, c1, c2)))
        log.debug("Duplicate rows= {}".format(duplicate_rows(table_slice_2_cc1(array, r2, r_max, c1, c2))))
        c1 = c1 + 1
        log.debug("c1= {}".format(c1))

    # final cc1 is (r1-1,c1-1), because the last run of the while loops doesn't count
    # a problem could arise if the code never stepped through the while loops,
    # returning a cc1 with a negative index.
    # however, this should never happen since the final headers CANNOT have duplicate rows/columns,
    # by definition of cc2.
    # hence, the assertions:
    try:
        assert not duplicate_columns(table_slice_1_cc1(array, r1=0, r2=cc2[0], c2=cc2[1], c_max=c_max))
        assert not duplicate_rows(table_slice_2_cc1(array, r2=cc2[0], r_max=r_max, c1=0, c2=cc2[1]))
        assert r1 >= 0 and c1 >= 0
        cc1 = (r1 - 1, c1 - 1)
    except AssertionError:
        raise MIPSError("Error in _find_cc1_cc2")

    # provision for using the uppermost row possible for cc1, if titles are turned of
    if not table_object.configs['use_title_row']:
        if cc1[0] != 0:
            log.debug("METHOD. Title row removed, cc1 was shifted from {} to {}".format(cc1, (0, cc1[1])))
            cc1 = (0, cc1[1])
            table_object.history._title_row_removed = True
    else:
        table_object.history._title_row_removed = False

    # provision for using only the first column of the table as row header
    if table_object.configs['row_header'] is not None:
        row_header = table_object.configs['row_header']
        assert isinstance(row_header, int)
        if table_object.history.prefixed_rows:
            row_header += 1
        left = min(cc1[1], row_header)
        cc1 = (cc1[0], left)
        cc2 = (cc2[0], row_header)

    # provision for using only the first row of the table as column header
    if table_object.configs['col_header'] is not None:
        col_header = table_object.configs['col_header']
        assert isinstance(col_header, int)
        if table_object.history.prefixing_performed and not table_object.history.prefixed_rows:
            col_header += 1
        top = min(cc1[0], col_header)
        cc1 = (top, cc1[1])
        cc2 = (col_header, cc2[1])

    return cc1, cc2


def find_cc3(table_object, cc2):
    """
    Searches for critical cell `CC3`, as the leftmost cell of the first filled row of the data region.

    .. rubric:: Comment on implementation

    There are two options on how to implement the search for `CC3`:

        1. With the possibility of `Notes` rows directly below the header (default):
            * the first half filled row below the header is considered as the start of the data region, just like for the `CC4` cell
            * implemented by Embley et. al.
        2. Without the possibility of `Notes` rows directly below the header:
            * the first row below the header is considered as the start of the data region
            * for scientific tables it might be more common that the first data row only has a single entry
            * this can be chosen my commenting/uncommenting the code within this function

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    :param cc2: Tuple, position of `CC2` cell found with find_cc1_cc2()
    :type cc2: (int,int)
    :return: cc3
    """

    # OPTION 1
    # searching from the top of table for first half-full row, starting with first row below the header:
    n_rows = len(table_object.pre_cleaned_table[cc2[0] + 1:])
    log.debug("n_rows= {}".format(n_rows))
    for row_index in range(cc2[0] + 1, cc2[0] + 1 + n_rows, 1):
        n_full = 0
        n_columns = len(table_object.pre_cleaned_table[row_index, cc2[1] + 1:])
        log.debug("n_columns= {}".format(n_columns))
        for column_index in range(cc2[1] + 1, cc2[1] + 1 + n_columns, 1):
            empty = table_object.pre_cleaned_table_empty[row_index, column_index]
            if not empty:
                n_full += 1
            if n_full >= int(n_columns / 2):
                return row_index, cc2[1] + 1
    raise MIPSError("No CC3 critical cell found! No data region defined.")
    # OPTION 2
    # return (cc2[0]+1,cc2[1]+1)


def find_title_row(table_object):
    """
    Searches for the topmost non-empty row.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    :return: int
    """
    for row_index, empty_row in enumerate(table_object.pre_cleaned_table_empty):
        if not empty_row.all():
            return row_index


def find_note_cells(table_object, labels_table):
    """
    Searches for all non-empty cells that have not been labelled differently.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    :param labels_table: table that holds all the labels
    :type labels_table: Numpy array
    :return: Tuple
    """
    for row_index, row in enumerate(labels_table):
        for column_index, cell in enumerate(row):
            if cell == '/' and not table_object.pre_cleaned_table_empty[row_index, column_index]:
                yield row_index, column_index


def prefix_duplicate_labels(table_object, array):
    """
    Prefixes duplicate labels in first row or column where this is possible,
    by adding a new row/column containing the preceding (to the left or above) unique labels, if available.

    Nested prefixing is not supported.

    The algorithm is not completely selective and there might be cases where it's application is undesirable.
    However, on standard datasets it significantly improves table-region classification.

    Algorithm for column headers:

    1. Run MIPS, to find the old header region, without prefixing.
    2. For row in table, can *meaningful* prefixing in this row been done?
        * yes --> do prefixing and go to 3, prefixing of only one row is possible; accept prefixing only if prefixed rows/cells are above the end of the header (not in the data region), the prefixed cells can still be above the header
        * no  --> go to 2, next row
    3. run MIPS to get the new header region
    4. accept prefixing only if the prefixing has not made the header region start lower than before and if it hasn't made the header region wider than before

    The algorithm has been modified from Embley et al., *DOI: 10.1007/s10032-016-0259-1*.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    :param array: Table to use as input and to do the prefixing on
    :type array: Numpy array
    :return: Table with added rows/columns with prefixes, or, input table, if no prefixing was done

    """

    def unique(data, row_or_column):
        """
        Returns True if data is unique in the given row/column or False if not unique or not present.

        :param data:
        :param row_or_column:
        :return:
        """
        count = 0
        for cell in row_or_column:
            if cell == data:
                count += 1
        if count == 1:
            return True
        else:
            return False

    def prefixed_row_or_column(table):
        """
        Main algorithm for creating prefixed column/row headers.
        If cell is not unique, it is prefixed with the first unique above (for row header) or to the left
        (for column header).

        Returns the row/column containing the prefixes and the position of the row/column where the new row/column
        has to be inserted into the original table.

        This function is getting ugly and could be rewritten with the use of a nice list of tuples,
        for every row/column in the table, we would have a list of distinct elements with their positions in the row/column

        :param table: input table (will not be changed)
        :return: row_index: where the row/column has to be inserted, new_row: the list of prefixes
        """

        unique_prefix = False
        prefixed = False
        row_index = 0
        new_row = []
        for row_index, row in enumerate(table):
            duplicated_row = []
            new_row = []
            for cell_index, cell in enumerate(row):
                # append if unique or empty cell
                if unique(cell, row) or empty_string(cell):
                    duplicated_row.append(cell)
                    new_row.append("")
                else:
                    # find the first unique cell to the left
                    # don't use the first column and first row
                    # as these will presumably be in the stub header region
                    for prefix in reversed(duplicated_row[1:]):
                        # use the prefix if it is unique and not empty
                        if unique(prefix, row) and not empty_string(prefix):
                            unique_prefix = prefix
                            break
                    # prefix the cell and append it to new row
                    if unique_prefix:
                        duplicated_row.append(unique_prefix + "/" + cell)
                        new_row.append(unique_prefix)
                        prefixed = True
                    # else, if no unique prefix was found, just append the original cell,
                    else:
                        duplicated_row.append(cell)
                        new_row.append("")
            # and continue to the next row (if no prefixing has been performed)
            if prefixed:
                break
        if prefixed:
            return row_index, new_row
        else:
            return None

    # MAIN ALGORITHM
    # 1. first, check the MIPS, to see what header we would have gotten without the prefixing
    # note, cc4 couldn't have changed
    log.debug("Prefixing. Attempt to run main MIPS algorithm.")
    try:
        cc1, cc2 = find_cc1_cc2(table_object, find_cc4(table_object), array)
    except (MIPSError, TypeError):
        log.error("Prefixing was not performed due to failure of MIPS algorithm.")
        return array

    # this flag is used for the return value, if it doesn't change the original table is returned
    prefixed = False

    # 2. DO THE PREFIXING
    # prefixing of column headers
    if prefixed_row_or_column(array):
        row_index, new_row = prefixed_row_or_column(array)
        # only perform prefixing if not below of header region (above is allowed!)
        # to allow prefixing even below the old header region cannot be right
        if row_index <= cc2[0]:
            log.debug("Column header prefixing, row_index= {}".format(row_index))
            log.debug("Prefixed row= {}".format(new_row))
            # Prefixing by adding new row:
            prefixed = True
            prefixed_table = np.insert(array, row_index, new_row, axis=0)

    # prefixing of row headers
    if prefixed_row_or_column(array.T):
        column_index, new_column = prefixed_row_or_column(array.T)
        # only perform prefixing if not to the right of header region (to the left is allowed!)
        # to allow prefixing even below the old header region cannot be right
        if column_index <= cc2[1]:
            log.debug("Row header prefixing, column_index= {}".format(column_index))
            log.debug("Prefixed column= {}".format(new_column))
            # Prefixing by adding a new column:
            prefixed = True
            prefixed_table = np.insert(array, column_index, new_column, axis=1)

    # 3. check the headers again, after prefixing
    # note, cc4 couldn't have changed
    if prefixed:
        # if new headers fail, the prefixing has destroyed the table, which is not a HIT table anymore
        try:
            cc1_new, cc2_new = find_cc1_cc2(table_object, find_cc4(table_object), prefixed_table)
        except (MIPSError, TypeError):
            log.debug("Prefixing was not performed because it destroyed the table")
            return array
        # return prefixed_table only if the prefixing has not made the header to start lower,
        # it can end lower (and this is desired and what we want - not to include the data region into the header),
        # but it cannot start lower, because that would mean that we have removed some of the hierarchy and added
        # hierarchy from the left/above into a column/row
        if cc1_new[0] <= cc1[0] and cc1_new[1] <= cc1[1]:
            # Another condition, the header has to end lower than before, not to include at east one
            # lower row/column that was included before
            if cc2_new[0] <= cc2[0] and cc2_new[1] <= cc2[1]:
                table_object.history._prefixing_performed = True
                log.debug("METHOD. Prefixing was performed.")
                if len(prefixed_table.T) > len(array.T):
                    table_object.history._prefixed_rows = True
                return prefixed_table
            else:
                return array
        else:
            return array
    else:
        return array


def duplicate_spanning_cells(table_object, array):
    """
    Duplicates cell contents into appropriate spanning cells. This is sometimes necessary for `.csv` files where
    information has been lost, or, if the source table is not properly formatted.

    Cells outside the row/column header (such as data cells) will not be duplicated.
    MIPS is run to perform a check for that.

    Algorithm according to Nagy and Seth, 2016, in Procs. ICPR 2016, Cancun, Mexico.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    :param array: Table to use as input
    :type array: Numpy array
    :return: Array with spanning cells copied, if necessary. Alternatively, returns the original table.
    """

    def empty_row(arrayy):
        """Returns 'True' if the whole row is truly empty"""
        for element in arrayy:
            if element:
                return False
        return True

    # running MIPS to find the data region
    log.debug("Spanning cells. Attempt to run MIPS algorithm, to find potential title row.")
    try:
        cc1, cc2 = find_cc1_cc2(table_object, find_cc4(table_object), table_object.pre_cleaned_table)
    except (MIPSError, TypeError):
        log.error("Spanning cells update was not performed due to failure of MIPS algorithm.")
        return array

    log.debug("Spanning cells. Attempt to run main spanning cell algorithm.")
    temp = array.copy()
    top_fill = None
    left_fill = None
    for c in range(0, len(temp.T)):
        flag = 0
        for r in range(cc1[0], len(temp)):
            if temp[r, c]:
                top_fill = temp[r, c]
                flag = 1
            elif flag == 1:
                temp[r, c] = top_fill
            if len(temp) - 1 > r and empty_row(temp[r + 1]):
                flag = 0
    for r in range(cc1[0], len(temp)):
        flag = 0
        for c in range(len(temp.T)):
            if temp[r, c]:
                if (len(temp) - 1 > r and temp[r + 1, c] != temp[r, c]) or temp[r - 1, c] != temp[r, c]:
                    left_fill = temp[r, c]
                    flag = 1
                else:
                    flag = 0
            elif flag == 1:
                temp[r, c] = left_fill
            if len(temp.T) - 1 > c and empty_row(temp.T[c + 1]):
                flag = 0

    # Finding the header regions to make sure the spanning cells additions are not applied in the data region
    # Then, the main MIPS algorithm has to be run
    temp2 = np.copy(temp)
    diff_row_length = 0
    diff_col_length = 0
    if table_object.configs['use_prefixing']:
        temp2 = prefix_duplicate_labels(table_object, temp)
        # reset the prefixing flag
        table_object.history._prefixing_performed = False
        table_object.history._prefixed_rows = False
        diff_row_length = len(temp2) - len(temp)
        diff_col_length = len(temp2.T) - len(temp.T)
    log.debug("Spanning cells. Attempt to run main MIPS algorithm.")
    # disable title row temporarily
    old_title_row_setting = table_object.configs['use_title_row']
    table_object.configs['use_title_row'] = False
    try:
        cc1, cc2 = find_cc1_cc2(table_object, find_cc4(table_object), temp2)
    except (MIPSError, TypeError):
        log.error("Spanning cells update was not performed due to failure of MIPS algorithm.")
        return array
    finally:
        table_object.configs['use_title_row'] = old_title_row_setting

    updated = array.copy()
    # update the original table with values from the updated table if the cells are in the header regions
    # update column header
    for col_header_index in range(cc1[0], cc2[0] + 1 - diff_row_length):
        updated[col_header_index, :] = temp[col_header_index, :]

    # update row header
    for row_header_index in range(cc1[1], cc2[1] + 1 - diff_col_length):
        updated[:, row_header_index] = temp[:, row_header_index]

    # log
    if not np.array_equal(updated, array):
        table_object.history._spanning_cells_extended = True
        log.debug("METHOD. Spanning cells extended.")

    return updated


def header_extension_up(table_object, cc1):
    """
    Extends the header after main MIPS run.

    Algorithm according to Nagy and Seth, 2016, *"Table Headers: An entrance to the data mine"*,
    in Procs. ICPR 2016, Cancun, Mexico.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    :param cc1: `CC1` critical cell
    :return: cc1_new
    """

    cc1_new_row = None
    cc1_new_col = None

    # add row above the identified column header if it does not consist of cells with identical values and if it
    # adds at least one non-blank cell that has a value different from the cell immediately below it
    current_row = table_object.pre_cleaned_table[cc1[0], :]
    for row_index in range(cc1[0]-1, -1, -1):
        # start after the first column to allow for a title
        if len(np.unique(table_object.pre_cleaned_table[row_index, 1:])) == 1:
            cc1_new_row = row_index+1
        else:
            for col_index, cell in enumerate(table_object.pre_cleaned_table[row_index, :]):
                # remove the first row from this check to preserve a title,
                # if the title is the only non-empty element of the row
                if col_index != 0 and \
                        cell != current_row[col_index] and \
                        not table_object.pre_cleaned_table_empty[row_index, col_index]:
                    current_row = table_object.pre_cleaned_table[row_index, :]
                    cc1_new_row = row_index
                    break
    if cc1_new_row is None:
        cc1_new_row = cc1[0]

    # now do the same for the row headers
    current_col = table_object.pre_cleaned_table[:, cc1[1]]
    for col_index in range(cc1[1]-1, -1, -1):
        if len(np.unique(table_object.pre_cleaned_table[:, col_index])) == 1:
            cc1_new_col = col_index+1
        else:
            for row_index, cell in enumerate(table_object.pre_cleaned_table[:, col_index]):
                if cell != current_col[row_index] and not table_object.pre_cleaned_table_empty[row_index, col_index]:
                    current_col = table_object.pre_cleaned_table[:, col_index]
                    cc1_new_col = col_index
                    break
    if cc1_new_col is None:
        cc1_new_col = cc1[1]

    cc1_new = (cc1_new_row, cc1_new_col)

    # log
    if not cc1_new == cc1:
        table_object.history._header_extended_up = True
        log.debug("METHOD. Header extended upwards.")

    return cc1_new


def header_extension_down(table_object, cc1, cc2, cc4):
    """
    Extends the header downwards, if no prefixing was done and if the appropriate stub header is empty.
    For row-header expansion downwards, only the first cell of the stub header has to be empty.
    For column-header expansion to the right, the whole stub header column above has to be empty.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    :param cc2: Critical cell `CC2`
    :type cc2: (int, int)
    :param cc1: Critical cell `CC1`
    :type cc1: (int, int)
    :param cc4: Critical cell `CC4`
    :type cc4: (int, int)
    :return: New `cc2`
    """
    cc2_new = cc2
    extended = False

    # only do downwards header extension if no prefixing was done
    if not table_object.history.prefixing_performed:

        # extend column header downwards, changes cc2 row
        # only the first cell of the stub header has to be empty to accept the move downwards
        row_index = cc2[0]
        while row_index <= cc4[0] and empty_string(table_object.pre_cleaned_table[row_index, cc1[1]]):
            row_index += 1
            cc2_new = (row_index - 1, cc2_new[1])
            if cc2_new != cc2:
                extended = True

        # Check if row header can be shortened now, check duplicate rows accordingly, changes cc2 col
        if extended:
            cc2_new_col = cc2_new[1]
            i = len(table_object.row_header.T)
            while not duplicate_rows(table_object.row_header[:, :i]) and i > 1:
                i -= 1
                if not duplicate_rows(table_object.row_header[:, :i]):
                    cc2_new_col -= 1
            cc2_new = (cc2_new[0], cc2_new_col)
            extended = False

        # extend row header to the right, changes cc2 col
        # this check is more rigorous than above, and all the cells in the stub header have to be empty
        col_index = cc2_new[1]
        while col_index <= cc4[1] and empty_cells(table_object.pre_cleaned_table[cc1[0]:cc2[0]+1, col_index]).all():
            col_index += 1
            if col_index - 1 != cc2_new[1]:
                extended = True
            cc2_new = (cc2_new[0], col_index - 1)

        if extended:
            # Check if column header can be shortened now, changes cc2 row
            cc2_new_row = cc2_new[0]
            i = len(table_object.col_header)
            while not duplicate_columns(table_object.col_header[:i, :]) and i > 1:
                i -= 1
                if not duplicate_columns(table_object.col_header[:i, :]):
                    cc2_new_row -= 1
            cc2_new = (cc2_new_row, cc2_new[1])

        if extended:
            table_object.history._header_extended_down = True

    return cc2_new


def categorize_header(header):
    """
    Performs header categorization (calls the `SymPy` `fact` function) for a given table.

    :param header: header region, Numpy array
    :return: factor_list
    """

    # empty expression and part of the expression that will be factorized
    # these are SymPy expressions
    expression = 0
    part = 0
    for row_index, row in enumerate(header):
        for column_index, cell in enumerate(row):
            if column_index == 0:
                part = Symbol(cell)
            else:
                part = part * Symbol(cell)
        expression = expression + part
    # factorization
    # f = factor(expression, deep=True)
    f = factor_list(expression)
    log.debug("Factorization, initial header: {}".format(expression))
    log.debug("Factorization, factorized header: {}".format(f))
    return f


def build_category_table(table, cc1, cc2, cc3, cc4):
    """
    Build category table for given input table.
    Original header factorization, according to Embley et al., *DOI: 10.1007/s10032-016-0259-1*.
    This version is not used, instead :class:`~tabledataextractor.output.to_pandas.build_category_table` is being used.

    :param table: Table on which to perform the categorization
    :type table: Numpy array
    :param cc1: key MIPS cell
    :param cc2: key MIPS cell
    :param cc3: key MIPS cell
    :param cc4: key MIPS cell
    :return: category table as numpy array
    """

    column_header = table[cc1[0]:cc2[0] + 1, cc3[1]:cc4[1] + 1]
    row_header = table[cc3[0]:cc4[0] + 1, cc1[1]:cc2[1] + 1]
    column_factors = categorize_header(column_header.T)
    row_factors = categorize_header(row_header)


def split_table(table_object):
    """
    Splits table into subtables. Yields :class:`~tabledataextractor.table.table.Table` objects.

    Algorithm:
        If the stub header is repeated in the column header section the table is split up before
        the repeated element.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    """

    # first, the column header
    i = 0
    # the last row of the column/stub header is not used, as it will be determined as
    # data region by the main MIPS algorithm
    for col_index, column in enumerate(table_object.col_header[:-1].T):
        # the first match is backwards and forwards looking
        if i == 0 and column.size > 0 and \
                table_object.stub_header[:-1].T[0].size > 0 and \
                np.array_equal(column, table_object.stub_header[:-1].T[0]):
            yield table_object._pre_cleaned_table[:, 0:col_index + 1].tolist()
            i += 1
        # every other match is only forwards looking
        if i > 0 and column.size > 0 and \
                table_object.stub_header[:-1].T[0].size > 0 and \
                np.array_equal(column, table_object.stub_header[:-1].T[0]):
            yield table_object._pre_cleaned_table[:, col_index + 1:col_index + i * col_index + 2].tolist()
            i += 1

    # now the same thing for the row header
    i = 0
    for row_index, row in enumerate(table_object.row_header[:, :-1]):
        # the first match is backwards and forwards looking
        if i == 0 and row.size > 0 and \
                table_object.stub_header[0, :-1].size > 0 and \
                np.array_equal(row, table_object.stub_header[0, :-1]):
            yield table_object._pre_cleaned_table[0:row_index + 1, :].tolist()
            i += 1
        # every other match is only forwards looking
        if i > 0 and row.size > 0 and \
                table_object.stub_header[0, :-1].size > 0 \
                and np.array_equal(row, table_object.stub_header[0, :-1]):
            yield table_object._pre_cleaned_table[row_index + 1:row_index + i * row_index + 2, :].tolist()
            i += 1


def find_row_header_table(category_table, stub_header):
    """
    Constructs a Table from the row categories of the original table.

    :param category_table: ~tabledataextractor.table.table.Table.category_table
    :type category_table: list
    :param stub_header: ~tabledataextractor.table.table.Table.stub_header
    :type stub_header: numpy.ndarray
    :return: list
    """
    stub_header = stub_header.tolist()
    raw_table = list()
    for line in stub_header:
        new_line = list()
        for item in line:
            new_line.append(item)
        raw_table.append(new_line)
    for line in category_table:
        new_line = list()
        for item in line[1]:
            new_line.append(item)
        raw_table.append(new_line)
    return raw_table


def clean_row_header(pre_cleaned_table, cc2):
    """
    Cleans the row header by removing duplicate rows that span the whole table.
    """
    unmodified_part = pre_cleaned_table[:cc2[0]+1, :]
    modified_part = pre_cleaned_table[cc2[0]+1:, :]

    # delete duplicate rows that extend over the whole table
    _, indices = np.unique(modified_part, axis=0, return_index=True)
    # for logging only, which rows have been removed
    removed_rows = []
    for row_index in range(0, len(modified_part)):
        if row_index not in indices:
            removed_rows.append(row_index)
    # deletion
    modified_part = modified_part[np.sort(indices)]

    return np.vstack((unmodified_part, modified_part))
