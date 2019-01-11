# -*- coding: utf-8 -*-
"""
tabledataextractor.table.table

Raw, processed and final labelled table.

.. codeauthor:: Juraj Mavračić <jm2111@cam.ac.uk>

"""

import sys
import logging
import numpy as np
import re
from sympy import Symbol
from sympy import factor_list
from tabledataextractor.input import from_any
from tabledataextractor.output.print import print_table, list_as_PrettyTable
from tabledataextractor.output.print import as_string
from tabledataextractor.output.to_csv import write_to_csv
from tabledataextractor.output.to_pandas import to_pandas, build_category_table
from tabledataextractor.table.parse import CellParser, StringParser


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Table:
    """
    Initialized by converting the input to a numpy array form and performing all
    appropriate labelling steps.

    :param file_path: Path to .html or .cvs file, URL or list object that is used as input
    :type file_path: str | list
    :param table_number: Number of the table that we want to input if there are several at the given address/path
    :type table_number: int
    """

    def __init__(self, file_path, table_number=1, **kwargs):
        """
        Will initialize the table object, with all 'None' properties.
        After reading-in of the raw table from a source the table will be analyzed

        :param file_path: Path to .html or .cvs file, URL or list object that is used as input
        :type file_path: str | list
        :param table_number: Number of the table that we want to input if there are several at the given address/path
        :type table_number: int
        """

        log.info('Initialization of table: "{}"'.format(file_path))
        self.file_path = file_path
        self.table_number = table_number

        # TODO Set the keywords based on the provided input dictionary kwargs
        self.use_title_row = True
        self.use_max_data_area = False
        self.use_notes_in_first_col = True
        self.use_prefixing = True
        self.use_footnotes = True




        # read-in the raw table from any source
        self.raw_table = from_any.create_table(self.file_path, table_number)
        # check if everything is ok with the raw table
        if not isinstance(self.raw_table, np.ndarray) or self.raw_table.dtype != '<U60':
            msg = 'Input was not properly converted to numpy array.'
            log.critical(msg)
            raise InputTableError(msg)

        # check that array has dimension greater than one in both dimensions
        if self.raw_table.ndim == 1:
            msg = 'Table has only one row or column.'
            log.critical(msg)
            raise InputTableError(msg)

        # initializing empty elements
        self.cc1 = None
        self.cc2 = None
        self.cc3 = None
        self.cc4 = None
        self.category_table = []
        self.pre_cleaned_table = None
        self.pre_cleaned_table_empty = None
        self.raw_table_empty = None
        self.labels = None
        self.stub_header = None
        self.row_header = None
        self.col_header = None
        self.data = None
        self.transposed = False

        # run the table analysis
        self.analyze_table()

    def analyze_table(self):
        """
        Performs the analysis of the input table.
        Is run automatically on initialization of the table object, but can be re-run manually if needed.
        """

        # mask, 'cell = True' if cell is empty
        self.raw_table_empty = self.empty_cells(self.raw_table)

        # pre-cleaning table
        self.pre_cleaned_table = np.copy(self.raw_table)
        self.pre_clean()
        self.pre_cleaned_table_empty = self.empty_cells(self.pre_cleaned_table)

        # TESTING
        # self.print()

        # prefixing of duplicate labels in the header region
        self.pre_cleaned_table = self.prefix_duplicate_labels(self.pre_cleaned_table)
        self.pre_cleaned_table_empty = self.empty_cells(self.pre_cleaned_table)

        # labelling
        self.labels = np.empty_like(self.pre_cleaned_table, dtype="<U60")
        self.labels[:, :] = '/'
        self.label_sections()

        # making regions proper elements of the table object
        if self.cc1 and self.cc2 and self.cc3 and self.cc4:
            self.stub_header = self.pre_cleaned_table[self.cc1[0]:self.cc2[0] + 1, self.cc1[1]:self.cc2[1] + 1]
            self.row_header = self.pre_cleaned_table[self.cc3[0]:self.cc4[0] + 1, self.cc1[1]:self.cc2[1] + 1]
            self.col_header = self.pre_cleaned_table[self.cc1[0]:self.cc2[0] + 1, self.cc3[1]:self.cc4[1] + 1]
            self.data = self.pre_cleaned_table[self.cc3[0]:self.cc4[0] + 1, self.cc3[1]:self.cc4[1] + 1]

            # categorization
            self.category_table = self.build_category_table(self.pre_cleaned_table, self.cc1, self.cc2, self.cc3,
                                                            self.cc4)

    def transpose(self):
        """
        Transposes the raw_table and calls the analyze_table() function again.
        In this way, if working interactively from a Jupyter notebook, it is possible to input a table and then
        transpose it.
        """
        self.raw_table = self.raw_table.T
        self.transposed = True
        # self.print()
        self.cc1 = None
        self.cc2 = None
        self.cc3 = None
        self.cc4 = None
        self.category_table = []
        self.pre_cleaned_table = None
        self.pre_cleaned_table_empty = None
        self.raw_table_empty = None
        self.labels = None
        self.stub_header = None
        self.row_header = None
        self.col_header = None
        self.data = None
        self.analyze_table()

    def prefix_duplicate_labels(self, table):
        """
        Prefixes duplicate labels in first row or column where this is possible,
        by adding a new row/column containing the preceding (to the left or above) unique labels, if available.

        The algorithm for column headers:

            1. Run MIPS, to find the old header region, without prefixing
            2. For row in table, start with first row of the table
                a) can *meaningful* prefixing in this row been done?
                    * YES --> do prefixing and go to 3, prefixing of only one row is possible; accept prefixing only if prefixed rows/cells are above the end of the header (not in the data region), the prefixed cells can still be above the header
                    * NO  --> go to 2, next row

            3. run MIPS to get new header region
            4. accept prefixing only if the prefixing has not made the header region start lower than before

        Nested prefixing is not supported.

        The algorithm is not completely selective and there might be cases where it's application is undesirable.
        However, on average, it is supposed to significantly improve table-region classification.

        :param table: Table to use as input and to do the prefixing on
        :return prefixed_table: Table with added rows/columns with prefixes, or, input table, if no prefixing was done
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
            duplicated_row = []
            new_row = []
            for row_index, row in enumerate(table):
                duplicated_row = []
                new_row = []
                for cell_index, cell in enumerate(row):
                    # append if unique or empty cell
                    if unique(cell, row) or self.empty_string(cell):
                        duplicated_row.append(cell)
                        new_row.append("")
                    else:
                        # find the first unique cell to the left
                        # don't use the first column and first row
                        # as these will presumably be in the stub header region
                        for prefix in reversed(duplicated_row[1:]):
                            # use the prefix if it is unique and not empty
                            if unique(prefix, row) and not self.empty_string(prefix):
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
        log.info("Prefixing. Attempt to run main MIPS algorithm.")
        try:
            cc1, cc2 = self.find_cc1_cc2(self.find_cc4(), table)
        except:
            log.error("Prefixing was not performed due to failure of MIPS algorithm.")
            return table

        # this flag is used for the return value, if it doesn't change the original table is returned
        prefixed = False

        # 2. DO THE PREFIXING
        # prefixing of column headers
        if prefixed_row_or_column(table):
            row_index, new_row = prefixed_row_or_column(table)
            # only perform prefixing if not below of header region (above is allowed!)
            # to allow prefixing even below the old header region cannot be right
            if row_index <= cc2[0]:
                log.info("Column header prefixing, row_index= {}".format(row_index))
                log.debug("Prefixed row= {}".format(new_row))
                # Prefixing by adding new row:
                prefixed = True
                prefixed_table = np.insert(table, row_index, new_row, axis=0)

        # prefixing of row headers
        if prefixed_row_or_column(table.T):
            column_index, new_column = prefixed_row_or_column(table.T)
            # only perform prefixing if not to the right of header region (to the left is allowed!)
            # to allow prefixing even below the old header region cannot be right
            if column_index <= cc2[1]:
                log.info("Row header prefixing, column_index= {}".format(column_index))
                log.debug("Prefixed column= {}".format(new_column))
                # Prefixing by adding a new column:
                prefixed = True
                prefixed_table = np.insert(table, column_index, new_column, axis=1)

        # 3. check the headers again, after prefixing
        # note, cc4 couldn't have changed
        if prefixed:
            # if new headers fail, the prefixing has destroyed the table, which is not a HIT table anymore
            try:
                cc1_new, cc2_new = self.find_cc1_cc2(self.find_cc4(), prefixed_table)
            except:
                log.info("Prefixing was not performed because it destroyed the table")
                return table
            # return prefixed_table only if the prefixing has not made the header to start lower,
            # it can end lower (and this is desired and what we want - not to include the data region into the header),
            # but it cannot start lower, because that would mean that we have removed some of the hierarchy and added
            # hierarchy from the left/above into a column/row
            if cc1_new[0] <= cc1[0] and cc1_new[1] <= cc1[1]:
                return prefixed_table
            else:
                return table
        else:
            return table

    def find_cc4(self):
        """
        Searches for cell 'CC4'.

        Searching from the bottom of the pre-cleaned table for the last row with a minority of empty cells.
        Rows with at most a few empty cells are assumed to be part of the data region rather than notes or footnotes rows
        (which usually have only one or two non-empty cells).

        :return: (int,int)
        """
        # searching from the bottom of original table:
        n_rows = len(self.pre_cleaned_table)
        for row_index in range(n_rows - 1, -1, -1):
            # counting the number of full cells
            # if n_empty < n_full terminate, this is our goal row
            n_full = 0
            n_columns = len(self.pre_cleaned_table_empty[row_index])
            for empty in self.pre_cleaned_table_empty[row_index]:
                if not empty:
                    n_full += 1
                if n_full > int(n_columns / 2):
                    return row_index, n_columns - 1

    def find_cc1_cc2(self,cc4,table, use_max_data_area=False):
        """
        Searches for cells 'CC2' and 'CC3' using the MIPS algorithm published by Embley et. al.
        MIPS locates the critical cells that define the minimum row and column headers needed to index
        every data cell.

        :param cc4: Tuple, position of CC4 cell found with find_cc4()
        :param table: table which will be used, has to be passed explicitly
        :param use_max_data_area: If set to True the maximum data area for CC2 will be used, according to Embley et al.
        However, this is an unsafe setting and the default 'False' is usually better.
        :type cc4: Tuple
        :type use_max_data_area: boolean
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

        def table_slice_cc2(table,r2,r_max,c1,c2):
            """
            Function to cut the correct slices out of array for CC2 in find_cc1_cc2().
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
            if r2+1 == r_max and c1 == c2:
                section_1 = table[r2+1, c1]
            elif r2+1 == r_max and c1 != c2:
                section_1 = table[r2+1, c1:c2+1]
            elif r2+1 != r_max and c1 != c2:
                section_1 = table[r2+1:r_max+1, c1:c2+1]
            elif r2 + 1 != r_max and c1 == c2:
                section_1 = table[r2 + 1:r_max+1, c1]
            else:
                log.critical("Not defined section_1, r2+1= {}, r_max= {}, c1= {}, c2= {}".format(r2+1, r_max, c1, c2))
                section_1 = None

            # contrary to the published pseudocode the row maximum is r2, not r2-1
            # one more row and column index than in the published pseudocode is needed,
            # since the a:b notation in python doesn't include b
            if r1 == r2 and c2+1 == c_max:
                section_2 = table[r1, c2+1]
            elif r1 == r2 and c2+1 != c_max:
                section_2 = table[r1, c2+1 : c_max+1]
            elif r1 != r2 and c2+1 != c_max:
                section_2 = table[r1: r2+1, c2+1: c_max+1]
            elif r1 != r2 and c2+1 == c_max:
                section_2 = table[r1: r2+1, c2+1]
            else:
                log.critical("Not defined section_2, r2-1= {}, r1= {}, c2+1= {}, c_max= {}".format(r2-1, r1, c2+1, c_max))
                section_2 = None

            return section_1,section_2

        def table_slice_1_cc1(table, r1, r2, c2, c_max):
            """
            Function to cut a correct slice out of array for CC1 in find_cc1_cc2().
            Cuts out the column header.
            """
            # one more row and column index than in the published pseudocode is needed,
            # since the a:b notation in python doesn't include b
            # contrary to the published pseudocode, the correct range is [r1:r2,c2+1:c_max] and not [r1+1:r2,c2+1:c_max]
            if r1 == r2 and c2+1 == c_max:
                section = table[r1, c2+1]
            elif r1 == r2 and c2+1 != c_max:
                section = table[r1, c2+1:c_max+1]
            elif r1 != r2 and c2+1 != c_max:
                section = table[r1: r2+1, c2 + 1:c_max+1]
            elif r1 != r2 and c2+1 == c_max:
                section = table[r1: r2+1, c2 + 1]
            else:
                log.critical("Not defined section 1 for cc1, r1+1= {}, r2= {}, c2+1= {}, c_max= {}".format(r1+1, r2, c2+1, c_max))
                section = None
            return section

        def table_slice_2_cc1(table, r2, r_max, c1, c2):
            """
            Function to cut a correct slice out of array for CC1 in find_cc1_cc2().
            Cuts out the row header.
            """
            # one more row and column index than in the published pseudocode is needed,
            # since the a:b notation in python doesn't include b
            # contrary to the published pseudocode, the correct range is [r2:r_max,c1:c2] and not [r2+1:c2,c1+1:r_max]
            if r2 == r_max and c1 == c2:
                section = table[r2, c1]
            elif r2 == r_max and c1 != c2:
                section = table[r2, c1 : c2+1 ]
            elif r2 != r_max and c1 != c2:
                section = table[r2 : r_max+1, c1 : c2+1 ]
            elif r2 != r_max and c1 == c2:
                section = table[r2 : r_max+1, c1]
            else:
                log.critical("Not defined section 2 for cc1, r2+1= {}, c2= {}, c1+1= {}, r_max= {}".format(r2+1, c2, c1+1, r_max))
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

            temp_section_1, temp_section_2 = table_slice_cc2(table, r2, r_max, c1, c2)

            log.debug("temp_section_1:\n{}".format(temp_section_1))
            log.debug("temp_section_2:\n{}".format(temp_section_2))
            log.debug("duplicate_rows= {}, duplicate_columns= {}".
                      format(duplicate_rows(temp_section_1), duplicate_rows(temp_section_2)))

            if not duplicate_rows(temp_section_1) and not duplicate_columns(temp_section_2):
                if use_max_data_area:
                    data_area = (r_max - r2) * (c_max - c2)
                    log.debug("The data area of the new candidate C2= {} is *1: {}".format((r2, c2), data_area))
                    log.debug("Data area:\n{}".format(table[r2+1:r_max+1, c2+1:c_max+1]))
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
                if use_max_data_area:
                    data_area = (r_max - r2) * (c_max - c2)
                    log.debug("The data area of the new candidate C2= {} is *2: {}".format((r2, c2), data_area))
                    log.debug("Data area:\n{}".format(table[r2 + 1:r_max + 1, c2 + 1:c_max + 1]))
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
                if use_max_data_area:
                    data_area = (r_max - r2) * (c_max - c2)
                    log.debug("The data area of the new candidate C2= {} is *3: {}".format((r2, c2), data_area))
                    log.debug("Data area:\n{}".format(table[r2 + 1:r_max + 1, c2 + 1:c_max + 1]))
                    if data_area >= max_area:
                        max_area = data_area
                        cc2 = (r2, c2)
                        log.debug("CC2= {}".format(cc2))
                else:
                    cc2 = (r2, c2)
            # if none of those above is satisfied, just finish the loop
            else:
                r2 = r2 + 1
                if use_max_data_area:
                    data_area = (r_max - r2) * (c_max - c2)
                    log.debug("The data area of the new candidate C2= {} is *4: {}".format((r2, c2), data_area))
                    log.debug("Data area:\n{}".format(table[r2 + 1:r_max + 1, c2 + 1:c_max + 1]))
                    if data_area >= max_area:
                        max_area = data_area
                        cc2 = (r2, c2)
                        log.debug("CC2= {}".format(cc2))
                    break
                else:
                    cc2 = (r2, c2)
                    break

        log.debug("Ended loop with:  r_max= {}, c_max= {}, c1= {}, c2= {}, r1= {}, r2= {}, cc2= {}\n\n\n\n".format(r_max, c_max, c1, c2, r1, r2, cc2))

        # re-initialization of r2 and c2 from cc2; missing in the pseudocode
        r2 = cc2[0]
        c2 = cc2[1]

        # Locate CC1 at intersection of the top row and the leftmost column necessary for indexing:
        log.debug("Potentially duplicate columns:\n{}".format(table_slice_1_cc1(table, r1, r2, c2, c_max)))
        while not duplicate_columns(table_slice_1_cc1(table, r1, r2, c2, c_max)) and r1 <= r2:
            log.debug("Potentially duplicate columns:\n{}".format(table_slice_1_cc1(table, r1, r2, c2, c_max)))
            log.debug("Duplicate columns= {}".format(duplicate_columns(table_slice_1_cc1(table, r1, r2, c2, c_max))))
            r1 = r1 + 1
            log.debug("r1= {}".format(r1))

        log.debug("Potentially duplicate rows:\n{}".format(table_slice_2_cc1(table, r2, r_max, c1, c2)))
        while not duplicate_rows(table_slice_2_cc1(table, r2, r_max, c1, c2)) and c1 <= c2:

            log.debug("Potentially duplicate rows:\n{}".format(table_slice_2_cc1(table, r2, r_max, c1, c2)))
            log.debug("Duplicate rows= {}".format(duplicate_rows(table_slice_2_cc1(table, r2, r_max, c1, c2))))
            c1 = c1 + 1
            log.debug("c1= {}".format(c1))

        # final cc1 is (r1-1,c1-1), because the last run of the while loops doesn't count
        # a problem could arise if the code never stepped through the while loops,
        # returning a cc1 with a negative index.
        # however, this should never happen since the final headers CANNOT have duplicate rows/columns,
        # by definition of cc2.
        # hence, the assertions:
        assert not duplicate_columns(table_slice_1_cc1(table, r1=0, r2=cc2[0], c2=cc2[1], c_max=c_max))
        assert not duplicate_rows(table_slice_2_cc1(table, r2=cc2[0], r_max=r_max, c1=0, c2=cc2[1]))
        assert r1 >= 0 and c1 >= 0
        cc1 = (r1-1, c1-1)

        return cc1, cc2

    def find_cc3(self,cc2):
        """
        Searches for cell 'CC3', as the leftmost cell of the first filled row of the data region.

        :param cc2: Tuple, position of CC2 cell found with find_cc4()
        :type cc2: Tuple
        :return: (int,int)
        """

        # Comment on implementation:
        #   There are two options on how to implement the search for CC3:
        #   1. With the possibility of 'Notes' rows directly below the header:
        #       - the first half filled row below the header is considered as the start of the data region,
        #         just like for the CC4 cell
        #   2. Without the possibility of 'Notes' ros directly below the header:
        #       - the first row below the header is considered as the start of the data region
        #   Option 1 is implemented by Embley et. al. However, for scientific tables it might be more common
        #   that the first data row has only 1 entry. Therefore we might have to choose option 2.

        # OPTION 1
        # searching from the top of table for first half-full row, starting with first row below the header:
        n_rows = len(self.pre_cleaned_table[cc2[0]+1:])
        log.debug("n_rows= {}".format(n_rows))
        for row_index in range(cc2[0]+1,cc2[0]+1+n_rows, 1):
            n_full = 0
            n_columns = len(self.pre_cleaned_table[row_index,cc2[1]+1:])
            log.debug("n_columns= {}".format(n_columns))
            for column_index in range(cc2[1]+1,cc2[1]+1+n_columns,1):
                empty = self.pre_cleaned_table_empty[row_index,column_index]
                if not empty:
                    n_full += 1
                if n_full >= int(n_columns / 2):
                    return (row_index, cc2[1]+1)
        raise SystemError("No CC3 critical cell found! No data region defined.")
        # OPTION 2
        # return (cc2[0]+1,cc2[1]+1)

    def find_title_row(self):
        """
        Searches for the topmost non-empty row.
        :return: int
        """
        for row_index, empty_row in enumerate(self.pre_cleaned_table_empty):
            if not empty_row.all():
                return row_index

    def find_note_cells(self):
        """
        Searches for all non-empty cells that have not been labelled previously.
        :return: Tuple
        """
        for row_index,row in enumerate(self.labels):
            for column_index,cell in enumerate(row):
                if cell == '/' and not self.pre_cleaned_table_empty[row_index,column_index]:
                    yield row_index,column_index

    def find_FNprefix(self,cc4):
        """
        FNprefix  = \*, #, ., o, †; possibly followed by "." or ")".
        Searches only below the data region.

        :param cc4: end of data region
        :type cc4: (int,int)
        :return: List of cell indexes that match the FNprefix
        """
        fn_prefix = []
        fn_prefix_parser = CellParser('^([*#\.o†\da-z][\.\)]?)$')
        for fn_prefix_index in fn_prefix_parser.parse(self.pre_cleaned_table):
            if fn_prefix_index[0] > cc4[0]:
                fn_prefix.append(fn_prefix_index)
        return fn_prefix

    def find_FNtext(self,fn_prefix):
        """
        All the cells following a footnote marker in the same row as an fn_prefix cell.

        :param fn_prefix: List of FNprefix cells, indexes
        :type fn_prefix: list[(int,int)]
        :return: List of FNtext cells, indexes
        """
        fn_text = []
        for fn_prefix_cell in fn_prefix:
            # append all non-empty cells following fn_prefix index in the same row
            for column_index in range(fn_prefix_cell[1]+1,np.shape(self.pre_cleaned_table)[1]):
                if not self.pre_cleaned_table_empty[fn_prefix_cell[0],column_index]:
                    fn_text.append((fn_prefix_cell[0],column_index))
        return fn_text

    def find_FNprefix_FNtext(self,cc4):
        """
        FNprefix  = \*, #, ., o, †; possibly followed by "." or ")", followed by FNtext in the same cell.
        FNtext can be started by any word character '\w', '[' or ']'
        Searches only below the data region.

        :param cc4: end of data region
        :type cc4: (int,int)
        :return: List of cell indexes that match the FNprefix+FNtext
        """
        fn_prefix_fn_text = []
        fn_prefix_fn_text_parser = CellParser('^([*#\.o†\da-z][\.\)]?)\s([\w\[\]\s]+)')
        for fn_prefix_fn_text_index in fn_prefix_fn_text_parser.parse(self.pre_cleaned_table):
            if fn_prefix_fn_text_index[0] > cc4[0]:
                fn_prefix_fn_text.append(fn_prefix_fn_text_index)
        return fn_prefix_fn_text

    def find_FNref(self,fn_prefix,fn_prefix_fn_text):
        """
        Searches the entire table above each footnote for the previously detected and isolated footnote markers.

        Rules for matching:
            1. if prefix is number: a) matches if (anything)+space+prefix OR b) prefix(if not in data region)
            2. if prefix is a-z:    a) matches if (anything)+space+prefix OR b) prefix
            3. else:                matches if found anywhere in any cell

        :param FNprefix:
        :param FNprefix_FNtext:
        :return: List((int,int))
        """
        fn_refs = []

        for footnote in fn_prefix+fn_prefix_fn_text:

            # Case 1a If prefix is number, general
            if re.fullmatch(pattern='[\d]{1,2}',string=footnote[2][0]):
                log.debug("Footnote prefix {} is number".format(footnote[2][0]))
                fn_ref_parser_1a = CellParser('(^.+\s)('+footnote[2][0]+')(\s.+)?$')
                for fn_ref in fn_ref_parser_1a.parse(self.pre_cleaned_table[0:footnote[0]], method='match'):
                    fn_refs.append(fn_ref)

            # Case 1b If prefix is number and not in 'Data' region
                fn_ref_parser_1b = CellParser('^('+footnote[2][0]+')$')
                for fn_ref in fn_ref_parser_1b.parse(self.pre_cleaned_table[0:footnote[0]], method='match'):
                     if self.labels[fn_ref[0],fn_ref[1]] != 'Data':
                        log.debug("Footnote prefix {} is number, and is in {} region".format(footnote[2][0], self.labels[fn_ref[0],fn_ref[1]]))
                        fn_refs.append(fn_ref)

            # Case 2a If prefix is a-z:
            elif re.fullmatch(pattern='[a-zA-Z]',string=footnote[2][0]):
                log.debug("Footnote prefix {} is letter".format(footnote[2][0]))
                fn_ref_parser_2a = CellParser('(^.+\s)('+footnote[2][0]+')(\s.+)?$')
                for fn_ref in fn_ref_parser_2a.parse(self.pre_cleaned_table[0:footnote[0]], method='match'):
                    fn_refs.append(fn_ref)

            # Case 2b If prefix is a-z and alone in the cell
                fn_ref_parser_2b = CellParser('^('+footnote[2][0]+')$')
                for fn_ref in fn_ref_parser_2b.parse(self.pre_cleaned_table[0:footnote[0]], method='match'):
                    log.debug("Footnote prefix {} is letter and is alone in cell.".format(footnote[2][0]))
                    fn_refs.append(fn_ref)

            # Case 3, everything else
            else:
                fn_ref_parser = CellParser('('+re.escape(footnote[2][0])+')')
                for fn_ref in fn_ref_parser.parse(self.pre_cleaned_table[0:footnote[0]], method='search'):
                    fn_refs.append(fn_ref)
        return fn_refs

    def empty_cells(self,table):
        """
        Returns a mask with 'True' for all empty cells in the original array and 'False' for non-empty cells.
        The regular expression below, which defines an empty cell can be tweaked.
        """
        empty = np.full_like(table, fill_value=False, dtype=bool)
        empty_parser = CellParser(r'^([\s\-\–\"]+)?$')
        for empty_cell in empty_parser.parse(table, method='fullmatch'):
            empty[empty_cell[0],empty_cell[1]] = True
        return empty

    def empty_string(self, string):
        """
        Returns 'True' if a particular string is empty, which is defined with a regular expression
        :param string:
        :return:
        """
        empty_parser = StringParser(r'^([\s\-\–\"]+)?$')
        return empty_parser.parse(string, method='fullmatch')

    def pre_clean(self):
        """
        Remove empty and duplicate rows and columns that extend over the whole table.
        Replace 'None' cells with spaces.

        :return:
        """

        # find empty rows and delete them
        empty_rows = []
        for row_index,row in enumerate(self.raw_table_empty):
            if False not in row:
                empty_rows.append(row_index)
        log.info("Empty rows {} deleted.".format(empty_rows))
        self.pre_cleaned_table = np.delete(self.pre_cleaned_table,empty_rows, axis=0)

        # find empty columns and delete them
        empty_columns = []
        for column_index,column in enumerate(self.raw_table_empty.T):
            if False not in column:
                empty_columns.append(column_index)
        log.info("Empty columns {} deleted.".format(empty_columns))
        self.pre_cleaned_table = np.delete(self.pre_cleaned_table,empty_columns, axis=1)

        # delete duplicate rows that extend over the whole table
        _, indices = np.unique(self.pre_cleaned_table,axis=0,return_index=True)
        # for logging only, which rows have been removed
        removed_rows = []
        for row_index in range(0,len(self.pre_cleaned_table)):
            if row_index not in indices:
                removed_rows.append(row_index)
        log.info("Duplicate rows {} removed.".format(removed_rows))
        # deletion:
        self.pre_cleaned_table = self.pre_cleaned_table[np.sort(indices)]

        # delete duplicate columns that extend over the whole table
        _, indices = np.unique(self.pre_cleaned_table, axis=1, return_index=True)
        # for logging only, which rows have been removed
        removed_columns = []
        for column_index in range(0, len(self.pre_cleaned_table.T)):
            if column_index not in indices:
                removed_columns.append(column_index)
        log.info("Duplicate columns {} removed.".format(removed_columns))
        # deletion:
        self.pre_cleaned_table = self.pre_cleaned_table[:,np.sort(indices)]
        log.info("Table shape changed from {} to {}.".format(np.shape(self.raw_table),np.shape(self.pre_cleaned_table)))

    def label_sections(self):
        """
        Labelling of all classification table elements.
        """

        title_row = self.find_title_row()

        cc4 = self.find_cc4()
        log.info("Table Cell CC4 = {}".format(cc4))
        self.labels[cc4] = 'CC4'
        self.cc4 = cc4

        try:
            cc1, cc2 = self.find_cc1_cc2(cc4, self.pre_cleaned_table)
            log.info("Table Cell CC1 = {}; Table Cell CC2 = {}".format(cc1, cc2))
            self.labels[cc1] = 'CC1'
            self.labels[cc2] = 'CC2'
            self.cc1 = cc1
            self.cc2 = cc2
        # this is ugly but defining a custom exception raises an error, due to the assertion in find_cc1_cc2()
        # TODO make the exceptions nice and proper
        except:
            msg = "\n==================================================================================\n" \
                  "!!!!!!! ERROR: Main MIPS Algorithm failed. Maybe the input table is bad    !!!!!!!  \n" \
                  "==================================================================================\n"
            print("Table({}, table_number={}, transposed={})".format(self.file_path, self.table_number, self.transposed))
            print(msg)
            log.critical(msg)
            return None

        cc3 = self.find_cc3(cc2)
        log.info("Table Cell CC3 = {}".format(cc3))
        self.labels[cc3] = 'CC3'
        self.cc3 = cc3

        self.labels[title_row, :] = 'TableTitle'
        self.labels[cc1[0]:cc2[0]+1, cc1[1]:cc2[1]+1] = 'StubHeader'
        self.labels[cc3[0]:cc4[0]+1, cc1[1]:cc2[1]+1] = 'RowHeader'
        self.labels[cc1[0]:cc2[0]+1, cc3[1]:cc4[1]+1] = 'ColHeader'
        self.labels[cc3[0]:cc4[0]+1, cc3[1]:cc4[1]+1] = 'Data'

        # Footnotes
        fn_prefix = self.find_FNprefix(cc4)
        log.info("FNPrefix Cells = {}".format(fn_prefix))
        for fn_prefix_index in fn_prefix:
            self.labels[fn_prefix_index[0], fn_prefix_index[1]] = 'FNprefix'

        fn_text = self.find_FNtext(fn_prefix)
        log.info("FNtext Cells = {}".format(fn_text))
        for fn_text_index in fn_text:
            self.labels[fn_text_index] = 'FNtext'

        fn_prefix_fn_text = self.find_FNprefix_FNtext(cc4)
        log.info("FNPrefix&FNtext Cells = {}".format(fn_prefix_fn_text))
        for fn_prefix_fn_text_index in fn_prefix_fn_text:
            self.labels[fn_prefix_fn_text_index[0], fn_prefix_fn_text_index[1]] = 'FNprefix & FNtext'

        fn_refs = self.find_FNref(fn_prefix, fn_prefix_fn_text)
        log.info("FNref Cells = {}".format(fn_refs))
        for fn_ref in fn_refs:
            if self.labels[fn_ref[0], fn_ref[1]] != '/':
                self.labels[fn_ref[0], fn_ref[1]] = self.labels[fn_ref[0], fn_ref[1]] + ' & FNref'
            else:
                self.labels[fn_ref[0], fn_ref[1]] = 'FNref'

        # all non-empty unlabelled cells at this point are labelled 'Note'
        for note_cell in self.find_note_cells():
            self.labels[note_cell] = 'Note'

    def categorize_header(self, header):
        """
        Performs header categorization (calls the SymPy fact function) for a given table.

        :param header: Header region, Numpy array
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

    def build_category_table(self, table, cc1, cc2, cc3, cc4):
        """
        Build category table for given input table.

        :param table: Table on which to perform the categorization
        :param cc1: key cell
        :param cc2: key cell
        :param cc3: key cell
        :param cc4: key cell
        :return: category table as numpy array, Pandas data frame is used to create it
        """

        # Obsolete code, original header factorization, according to Embley et al.
        # column_header = table[cc1[0]:cc2[0] + 1, cc3[1]:cc4[1] + 1]
        # row_header = table[cc3[0]:cc4[0] + 1, cc1[1]:cc2[1] + 1]
        # column_factors = self.categorize_header(column_header.T)
        # row_factors = self.categorize_header(row_header)

        # Make the Pandas DataFrame
        dataframe = to_pandas(self)
        category_table = build_category_table(dataframe)
        return category_table

    def print(self):
        log.info("Printing table: {}".format(self.file_path))
        print_table(self.raw_table)
        print_table(self.pre_cleaned_table)
        # print_table(self.labels)

    def to_csv(self, file_path):
        log.info("Saving raw table to .csv to file: {}".format(self.file_path))
        write_to_csv(self.raw_table, file_path=file_path)

    def __str__(self):
        """As the user wants to see it"""
        log.info("Printing table: {}".format(self.file_path))
        output = as_string(self.pre_cleaned_table)
        return output

    def __repr__(self):
        """As the developer wants to see it"""
        intro = "Table({}, table_number={}, transposed={})".format(self.file_path, self.table_number, self.transposed)
        log.info("Repr. table: {}".format(self.file_path))
        array_width = np.shape(self.pre_cleaned_table)[1]
        input_string = as_string(self.raw_table)
        results_string = as_string(
            np.concatenate(
                (self.pre_cleaned_table, np.full((1, array_width), "", dtype='<U60'), self.labels)
            )
        )
        t = list_as_PrettyTable(self.category_table)
        return intro + "\n\n" + input_string + results_string + str(t)


class InputTableError(Exception):
    """
    Use when something is wrong with the provided input.
    """
    def __init__(self, message):
        self.message = message
