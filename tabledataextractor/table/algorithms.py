# -*- coding: utf-8 -*-
"""
Algorithms for TableDataExtractor.

.. codeauthor:: Juraj Mavračić <jm2111@cam.ac.uk>

"""

import logging
import numpy as np

from tabledataextractor.exceptions import MIPSError

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def find_cc4(table):
    """
    Searches for critical cell `CC4`.

    Searching from the bottom of the pre-cleaned table for the last row with a minority of empty cells.
    Rows with at most a few empty cells are assumed to be part of the data region rather than notes or footnotes rows
    (which usually only have one or two non-empty cells).

    :param table: Input Table object
    :type table: ~tabledataextractor.table.table.Table
    :return: cc4
    """
    # searching from the bottom of original table:
    n_rows = len(table.pre_cleaned_table)
    for row_index in range(n_rows - 1, -1, -1):
        # counting the number of full cells
        # if n_empty < n_full terminate, this is our goal row
        n_full = 0
        n_columns = len(table.pre_cleaned_table_empty[row_index])
        for empty in table.pre_cleaned_table_empty[row_index]:
            if not empty:
                n_full += 1
            if n_full > int(n_columns / 2):
                return row_index, n_columns - 1


def find_cc1_cc2(table_object, cc4, array):
    """
    Main MIPS (*Minimum Indexing Point Search*) algorithm, according to Embley et al., *DOI: 10.1007/s10032-016-0259-1*.
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
            log.info("METHOD. Title row removed, cc1 was shifted from {} to {}".format(cc1, (0, cc1[1])))
            cc1 = (0, cc1[1])
            table_object.history._title_row_removed = True
    else:
        table_object.history._title_row_removed = False

    return cc1, cc2

def duplicate_spanning_cells(table):
    """
    Duplicates cell contents into appropriate spanning cells. This is sometimes necessary for `.csv` files where
    information has been lost, or, if the source table is not properly formatted.

    Cells outside the row/column header (such as data cells) will not be duplicated.
    MIPS is run to perform a check for that.

    Algorithm according to Nagy and Seth, 2016, in Procs. ICPR 2016, Cancun, Mexico.

    :param table: Table to use as input
    :type table: Numpy array
    :return: Table with spanning cells copied, if necessary. Alternatively, returns the original table.
    """

    def empty_row(array):
        """Returns 'True' if the whole row is truly empty"""
        for element in array:
            if element:
                return False
        return True

    # running MIPS to find the data region
    log.info("Spanning cells. Attempt to run MIPS algorithm, to find potential title row.")
    try:
        cc1, cc2 = self._find_cc1_cc2(self._find_cc4(), self._pre_cleaned_table)
    except (MIPSError, TypeError):
        log.error("Spanning cells update was not performed due to failure of MIPS algorithm.")
        return table

    log.info("Spanning cells. Attempt to run main spanning cell algorithm.")
    temp = table.copy()
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
    if self._configs['use_prefixing']:
        temp2 = self._prefix_duplicate_labels(temp)
        # reset the prefixing flag
        self.history._prefixing_performed = False
        diff_row_length = len(temp2) - len(temp)
        diff_col_length = len(temp2.T) - len(temp.T)
    log.info("Spanning cells. Attempt to run main MIPS algorithm.")
    # disable title row temporarily
    old_title_row_setting = self._configs['use_title_row']
    self._configs['use_title_row'] = False
    try:
        cc1, cc2 = self._find_cc1_cc2(self._find_cc4(), temp2)
    except (MIPSError, TypeError):
        log.error("Spanning cells update was not performed due to failure of MIPS algorithm.")
        return table
    finally:
        self._configs['use_title_row'] = old_title_row_setting

    updated = table.copy()
    # update the original table with values from the updated table if the cells are in the header regions
    # update column header
    for col_header_index in range(cc1[0], cc2[0] + 1 - diff_row_length):
        updated[col_header_index, :] = temp[col_header_index, :]

    # update row header
    for row_header_index in range(cc1[1], cc2[1] + 1 - diff_col_length):
        updated[:, row_header_index] = temp[:, row_header_index]

    # log
    if not np.array_equal(updated, table):
        self.history._spanning_cells_extended = True
        log.info("METHOD. Spanning cells extended.")

    return updated


