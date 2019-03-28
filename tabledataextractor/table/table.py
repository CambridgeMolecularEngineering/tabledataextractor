# -*- coding: utf-8 -*-
"""
Represents a table in a highly standardized format.

.. codeauthor:: Juraj Mavračić <jm2111@cam.ac.uk>

"""

import logging

import numpy as np
from sympy import Symbol
from sympy import factor_list, factor

from tabledataextractor.input import from_any
from tabledataextractor.output.print import as_string, print_table, list_as_PrettyTable
from tabledataextractor.output.to_csv import write_to_csv
from tabledataextractor.output.to_pandas import to_pandas, build_category_table
from tabledataextractor.table.parse import CellParser, StringParser
from tabledataextractor.exceptions import TDEError, InputError, MIPSError
from tabledataextractor.table.footnotes import Footnote
from tabledataextractor.table.history import History

from tabledataextractor.table.algorithms import find_cc4

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


class Table:
    """
    Main `TableDataExtractor` object that includes the raw (input), cleaned (processes) and labelled tables.
    Represents the table input (.csv, .html, python list, url) in a highly standardized `category table` format,
    using the MIPS (*Minimum Indexing Point Search*) algorithm.

    Optional configuration keywords (defaults):

        * ``use_title_row = True``
            A title row will be assumed if possible.
        * ``use_prefixing = True``
            Will perform the prefixing steps if row or column index cells are not unique.
        * ``use_spanning_cells = True``
            Will duplicate spanning cells in the row and column header regions if needed.
        * ``use_header_extension = True``
            Will extend the row and column header beyond the MIPS-defined headers, if needed.
        * ``use_footnotes = True``
            Will copy the footnote text into the appropriate cells of the table and remove the footnote prefix.
        * ``use_max_data_area = False``
            If ``True`` the max data area will be used to determine the cell `CC2` in the main MIPS algorithm. It is probably never necessary to set this to True.

    :param file_path: Path to .html or .cvs file, URL or list object that is used as input
    :type file_path: str | list
    :param table_number: Number of table to read, if there are several at the given url, or in the html file
    :type table_number: int

    """

    def __init__(self, file_path, table_number=1, **kwargs):
        """Runs required `TableDataExtractor` algorithms automatically upon initialization."""
        log.info('Initialization of table: "{}"'.format(file_path))
        self._file_path = file_path
        self._table_number = table_number

        # default configs
        self._configs = {'use_title_row': True,
                         'use_prefixing': True,
                         'use_footnotes': True,
                         'use_spanning_cells': True,
                         'use_header_extension': True,
                         'use_max_data_area': False}
        self._set_configs(**kwargs)
        self._history = History()
        self._analyze_table()

    @property
    def footnotes(self):
        """
        List of footnotes in the table. Each footnote is an instance of :class:`~tabledataextractor.table.footnotes.Footnote`.
        """
        return self._footnotes

    @property
    def title_row(self):
        """Title row of the table as Python list."""
        if self._configs['use_title_row']:
            return self._find_title_row()

    @property
    def history(self):
        """
        Indicates which algorithms have been applied to the table by TableDataExtractor.
        Instance of :class:`~tabledataextractor.table.history.History`.
        """
        return self._history

    @property
    def labels(self):
        """Cell labels. Python List"""
        temp = np.empty_like(self._pre_cleaned_table, dtype="<U60")
        temp[:, :] = '/'

        if self.configs['use_title_row']:
            temp[self.title_row, :] = 'TableTitle'

        temp[self._cc1[0]:self._cc2[0] + 1, self._cc1[1]:self._cc2[1] + 1] = 'StubHeader'
        temp[self._cc3[0]:self._cc4[0] + 1, self._cc1[1]:self._cc2[1] + 1] = 'RowHeader'
        temp[self._cc1[0]:self._cc2[0] + 1, self._cc3[1]:self._cc4[1] + 1] = 'ColHeader'
        temp[self._cc3[0]:self._cc4[0] + 1, self._cc3[1]:self._cc4[1] + 1] = 'Data'

        for footnote in self.footnotes:
            temp[footnote.prefix_cell[0], footnote.prefix_cell[1]] = 'FNprefix'
            if footnote.text_cell is not None:
                temp[footnote.text_cell[0], footnote.text_cell[1]] = 'FNtext' if temp[footnote.text_cell[0], footnote.text_cell[1]] == '/' else 'FNprefix & FNtext'
            for ref_cell in footnote.reference_cells:
                temp[ref_cell[0], ref_cell[1]] = 'FNref' if temp[ref_cell[0], ref_cell[1]] == '/' else temp[ref_cell[0], ref_cell[1]] + ' & FNref'

        # all non-empty unlabelled cells at this point are labelled 'Note'
        for note_cell in self._find_note_cells(temp):
            temp[note_cell] = 'Note'
        return temp

    @property
    def configs(self):
        """Dictionary of configuration keywords."""
        return self._configs

    @property
    def raw_table(self):
        """
        Input table, as provided to `TableDataExtractor`.
        """
        try:
            temp = from_any.create_table(self._file_path, self._table_number)
        except TypeError as e:
            raise
        else:
            assert isinstance(temp, np.ndarray) and temp.dtype == '<U60'
            if temp.ndim == 1:
                msg = 'Input table has only one row or column.'
                log.critical(msg)
                raise InputError(msg)
            if not self.history.table_transposed:
                return temp
            else:
                return temp.T

    @property
    def pre_cleaned_table(self):
        """
        Cleaned-up table as :class:`numpy.ndarray`.
        This table is used for labelling the table regions, finding data-cells and building the category table.
        """
        return self._pre_cleaned_table

    @property
    def category_table(self):
        """Standardized table, where each row corresponds to a single data point of the original table. Python list."""
        if self._cc1 and self._cc2 and self._cc3 and self._cc4:
            return self._build_category_table(self._pre_cleaned_table, self._cc1, self._cc2, self._cc3, self._cc4)
        else:
            msg = "Category table not built. Critical cells have not been found."
            raise MIPSError(msg)

    @property
    def col_header(self):
        """Column header of the table. Python list."""
        if self._cc1 and self._cc2 and self._cc3 and self._cc4:
            return self._pre_cleaned_table[self._cc1[0]:self._cc2[0] + 1, self._cc3[1]:self._cc4[1] + 1]
        else:
            msg = "No column header. Critical cells have not been found."
            raise MIPSError(msg)

    @property
    def row_header(self):
        """Row header of the table. Python list."""
        if self._cc1 and self._cc2 and self._cc3 and self._cc4:
            return self._pre_cleaned_table[self._cc3[0]:self._cc4[0] + 1, self._cc1[1]:self._cc2[1] + 1]
        else:
            msg = "No row header. Critical cells have not been found."
            raise MIPSError(msg)

    @property
    def stub_header(self):
        """Stub header of the table. Python list."""
        if self._cc1 and self._cc2 and self._cc3 and self._cc4:
            return self._pre_cleaned_table[self._cc1[0]:self._cc2[0] + 1, self._cc1[1]:self._cc2[1] + 1]
        else:
            msg = "No stub header. Critical cells have not been found."
            raise MIPSError(msg)

    @property
    def data(self):
        """Data region of the table. Python list."""
        if self._cc1 and self._cc2 and self._cc3 and self._cc4:
            return self._pre_cleaned_table[self._cc3[0]:self._cc4[0] + 1, self._cc3[1]:self._cc4[1] + 1]
        else:
            msg = "No data region. Critical cells have not been found."
            raise MIPSError(msg)

    @property
    def pre_cleaned_table_empty(self):
        """Mask array with `True` for all empty cells of the ``pre_cleaned_table``."""
        return self.empty_cells(self._pre_cleaned_table)

    def _set_configs(self, **kwargs):
        """Sets the configuration parameters based on the user input."""
        for key, value in kwargs.items():
            if key in self._configs:
                self._configs[key] = value
            else:
                msg = 'Keyword "{}" does not exist.'.format(key)
                log.critical(msg)
                raise InputError(msg)
        log.info('Configuration parameters are: {}'.format(self._configs))

    def _analyze_table(self):
        """
        Performs the analysis of the input table
        and is run automatically on initialization of the table object, but can be re-run manually if needed.
        """

        self._footnotes = []

        # mask, 'cell = True' if cell is empty
        self._raw_table_empty = self.empty_cells(self.raw_table)

        # check if array is empty
        if self._raw_table_empty.all():
            msg = 'Input table is empty.'
            log.critical(msg)
            raise InputError(msg)

        # pre-cleaning table
        self._pre_cleaned_table = np.copy(self.raw_table)
        self._pre_clean()
        # self._pre_cleaned_table_empty = self.empty_cells(self._pre_cleaned_table)

        if self._configs['use_spanning_cells']:
            self._pre_cleaned_table = self._duplicate_spanning_cells(self._pre_cleaned_table)
            # self._pre_cleaned_table_empty = self.empty_cells(self._pre_cleaned_table)

        # prefixing of duplicate labels in the header region
        if self._configs['use_prefixing']:
            self._pre_cleaned_table = self._prefix_duplicate_labels(self._pre_cleaned_table)
            # self._pre_cleaned_table_empty = self.empty_cells(self._pre_cleaned_table)

        # labelling
        # self.labels = np.empty_like(self._pre_cleaned_table, dtype="<U60")
        # self.labels[:, :] = '/'
        self._label_sections()

    def transpose(self):
        """
        Transposes the :class:`~tabledataextractor.Table.raw_table` and calls the :class:`~tabledataextractor.Table._analyze_table` function again.
        In this way, if working interactively from a Jupyter notebook, it is possible to input a table and then
        transpose it.
        """
        # self.raw_table = self.raw_table.T
        self._history = History()
        self.history._table_transposed = True
        self._analyze_table()

    def _duplicate_spanning_cells(self, table):
        """
        Duplicates cell contents into appropriate spanning cells. This is sometimes necessary for `.csv` files where
        information has been lost, or, if the source table is not properly formatted.

        Cells outside the row/column header (such as data cells) will not be duplicated.
        MIPS is run to perform a check for that.

        Algorithm according to Nagy and Seth, 2016

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
            cc1, cc2 = self._find_cc1_cc2(find_cc4(self), self._pre_cleaned_table)
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
                if len(temp)-1 > r and empty_row(temp[r+1]):
                    flag = 0
        for r in range(cc1[0], len(temp)):
            flag = 0
            for c in range(len(temp.T)):
                if temp[r, c]:
                    if (len(temp)-1 > r and temp[r+1, c] != temp[r, c]) or temp[r-1, c] != temp[r, c]:
                        left_fill = temp[r, c]
                        flag = 1
                    else:
                        flag = 0
                elif flag == 1:
                    temp[r, c] = left_fill
                if len(temp.T)-1 > c and empty_row(temp.T[c+1]):
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
            cc1, cc2 = self._find_cc1_cc2(find_cc4(self), temp2)
        except (MIPSError, TypeError):
            log.error("Spanning cells update was not performed due to failure of MIPS algorithm.")
            return table
        finally:
            self._configs['use_title_row'] = old_title_row_setting

        updated = table.copy()
        # update the original table with values from the updated table if the cells are in the header regions
        # update column header
        for col_header_index in range(cc1[0], cc2[0]+1-diff_row_length):
            updated[col_header_index, :] = temp[col_header_index, :]

        # update row header
        for row_header_index in range(cc1[1], cc2[1]+1-diff_col_length):
            updated[:, row_header_index] = temp[:, row_header_index]

        # log
        if not np.array_equal(updated, table):
            self.history._spanning_cells_extended = True
            log.info("METHOD. Spanning cells extended.")

        return updated

    def _prefix_duplicate_labels(self, table):
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
        4. accept prefixing only if the prefixing has not made the header region start lower than before

        :param table: Table to use as input and to do the prefixing on
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
                    if unique(cell, row) or self._empty_string(cell):
                        duplicated_row.append(cell)
                        new_row.append("")
                    else:
                        # find the first unique cell to the left
                        # don't use the first column and first row
                        # as these will presumably be in the stub header region
                        for prefix in reversed(duplicated_row[1:]):
                            # use the prefix if it is unique and not empty
                            if unique(prefix, row) and not self._empty_string(prefix):
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
            cc1, cc2 = self._find_cc1_cc2(find_cc4(self), table)
        except (MIPSError, TypeError):
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
                cc1_new, cc2_new = self._find_cc1_cc2(find_cc4(self), prefixed_table)
            except (MIPSError, TypeError):
                log.info("Prefixing was not performed because it destroyed the table")
                return table
            # return prefixed_table only if the prefixing has not made the header to start lower,
            # it can end lower (and this is desired and what we want - not to include the data region into the header),
            # but it cannot start lower, because that would mean that we have removed some of the hierarchy and added
            # hierarchy from the left/above into a column/row
            if cc1_new[0] <= cc1[0] and cc1_new[1] <= cc1[1]:
                self.history._prefixing_performed = True
                log.info("METHOD. Prefixing was performed.")
                return prefixed_table
            else:
                return table
        else:
            return table

    # def _find_cc4(self):
    #     """
    #     Searches for critical cell `CC4`.
    #
    #     Searching from the bottom of the pre-cleaned table for the last row with a minority of empty cells.
    #     Rows with at most a few empty cells are assumed to be part of the data region rather than notes or footnotes rows
    #     (which usually only have one or two non-empty cells).
    #
    #     :return: cc4
    #     """
    #     # searching from the bottom of original table:
    #     n_rows = len(self._pre_cleaned_table)
    #     for row_index in range(n_rows - 1, -1, -1):
    #         # counting the number of full cells
    #         # if n_empty < n_full terminate, this is our goal row
    #         n_full = 0
    #         n_columns = len(self.pre_cleaned_table_empty[row_index])
    #         for empty in self.pre_cleaned_table_empty[row_index]:
    #             if not empty:
    #                 n_full += 1
    #             if n_full > int(n_columns / 2):
    #                 return row_index, n_columns - 1

    def _find_cc1_cc2(self, cc4, table):
        """
        Main MIPS (*Minimum Indexing Point Search*) algorithm, according to Embley et al., *DOI: 10.1007/s10032-016-0259-1*.
        Searches for critical cells `CC2` and `CC3`.
        MIPS locates the critical cells that define the minimum row and column headers needed to index
        every data cell.

        :param cc4: Position of `CC4` cell found with find_cc4()
        :param table: table to search for `CC1` and `CC2`
        :type table: numpy array
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
            Function to cut the correct slices out of array for CC2 in _find_cc1_cc2().
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

            temp_section_1, temp_section_2 = table_slice_cc2(table, r2, r_max, c1, c2)

            log.debug("temp_section_1:\n{}".format(temp_section_1))
            log.debug("temp_section_2:\n{}".format(temp_section_2))
            log.debug("duplicate_rows= {}, duplicate_columns= {}".
                      format(duplicate_rows(temp_section_1), duplicate_rows(temp_section_2)))

            if not duplicate_rows(temp_section_1) and not duplicate_columns(temp_section_2):
                if self._configs['use_max_data_area']:
                    data_area = (r_max - r2) * (c_max - c2)
                    log.debug("The data area of the new candidate C2= {} is *1: {}".format((r2, c2), data_area))
                    log.debug("Data area:\n{}".format(table[r2 + 1:r_max + 1, c2 + 1:c_max + 1]))
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
                if self._configs['use_max_data_area']:
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
                if self._configs['use_max_data_area']:
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
                if self._configs['use_max_data_area']:
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

        log.debug(
            "Ended loop with:  r_max= {}, c_max= {}, c1= {}, c2= {}, r1= {}, r2= {}, cc2= {}\n\n\n\n".format(r_max,
                                                                                                             c_max, c1,
                                                                                                             c2, r1, r2,
                                                                                                             cc2))

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
        try:
            assert not duplicate_columns(table_slice_1_cc1(table, r1=0, r2=cc2[0], c2=cc2[1], c_max=c_max))
            assert not duplicate_rows(table_slice_2_cc1(table, r2=cc2[0], r_max=r_max, c1=0, c2=cc2[1]))
            assert r1 >= 0 and c1 >= 0
            cc1 = (r1 - 1, c1 - 1)
        except AssertionError:
            raise MIPSError("Error in _find_cc1_cc2")

        # provision for using the uppermost row possible for cc1, if titles are turned of
        if not self._configs['use_title_row']:
            if cc1[0] != 0:
                log.info("METHOD. Title row removed, cc1 was shifted from {} to {}".format(cc1, (0, cc1[1])))
                cc1 = (0, cc1[1])
                self.history._title_row_removed = True
        else:
            self.history._title_row_removed = False

        return cc1, cc2

    def _header_extension(self, cc1):
        """
        Extends the header after main MIPS run.
        According to Nagy and Seth, 2016, *"Table Headers: An entrance to the data mine"*.

        :return: cc1_new
        """

        cc1_new_row = None
        cc1_new_col = None

        # add row above the identified column header if it does not consist of cells with identical values and if it
        # adds at least one non-blank cell that has a value different from the cell immediately below it
        current_row = self._pre_cleaned_table[cc1[0], :]
        for row_index in range(cc1[0]-1, -1, -1):
            # start after the first column to allow for a title
            if len(np.unique(self._pre_cleaned_table[row_index, 1:])) == 1:
                cc1_new_row = row_index+1
            else:
                for col_index, cell in enumerate(self._pre_cleaned_table[row_index, :]):
                    # remove the first row from this check to preserve a title,
                    # if the title is the only non-empty element of the row
                    if col_index != 0 and \
                            cell != current_row[col_index] and \
                            not self.pre_cleaned_table_empty[row_index, col_index]:
                        current_row = self._pre_cleaned_table[row_index, :]
                        cc1_new_row = row_index
                        break
        if cc1_new_row is None:
            cc1_new_row = cc1[0]

        # now do the same for the row headers
        current_col = self._pre_cleaned_table[:, cc1[1]]
        for col_index in range(cc1[1]-1, -1, -1):
            if len(np.unique(self._pre_cleaned_table[:, col_index])) == 1:
                cc1_new_col = col_index+1
            else:
                for row_index, cell in enumerate(self._pre_cleaned_table[:, col_index]):
                    if cell != current_col[row_index] and not self.pre_cleaned_table_empty[row_index, col_index]:
                        current_col = self._pre_cleaned_table[:, col_index]
                        cc1_new_col = col_index
                        break
        if cc1_new_col is None:
            cc1_new_col = cc1[1]

        cc1_new = (cc1_new_row, cc1_new_col)

        # log
        if not cc1_new == cc1:
            self.history._header_extended = True
            log.info("METHOD. Header extended.")

        return cc1_new

    def _find_cc3(self, cc2):
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

        :param cc2: Tuple, position of `CC2` cell found with find_cc4()
        :type cc2: (int,int)
        :return: cc3
        """

        # OPTION 1
        # searching from the top of table for first half-full row, starting with first row below the header:
        n_rows = len(self._pre_cleaned_table[cc2[0] + 1:])
        log.debug("n_rows= {}".format(n_rows))
        for row_index in range(cc2[0] + 1, cc2[0] + 1 + n_rows, 1):
            n_full = 0
            n_columns = len(self._pre_cleaned_table[row_index, cc2[1] + 1:])
            log.debug("n_columns= {}".format(n_columns))
            for column_index in range(cc2[1] + 1, cc2[1] + 1 + n_columns, 1):
                empty = self.pre_cleaned_table_empty[row_index, column_index]
                if not empty:
                    n_full += 1
                if n_full >= int(n_columns / 2):
                    return row_index, cc2[1] + 1
        raise MIPSError("No CC3 critical cell found! No data region defined.")
        # OPTION 2
        # return (cc2[0]+1,cc2[1]+1)

    def _find_title_row(self):
        """
        Searches for the topmost non-empty row.

        :return: int
        """
        for row_index, empty_row in enumerate(self.pre_cleaned_table_empty):
            if not empty_row.all():
                return row_index

    def _find_note_cells(self, labels_table):
        """
        Searches for all non-empty cells that have not been labelled differently.

        :return: Tuple
        """
        for row_index, row in enumerate(labels_table):
            for column_index, cell in enumerate(row):
                if cell == '/' and not self.pre_cleaned_table_empty[row_index, column_index]:
                    yield row_index, column_index

    def _find_footnotes(self):
        """
        Finds a footnote and yields a Footnote() object will all the appropriate properties.
        A footnote is defined with::

            FNprefix  = \*, #, ., o, †; possibly followed by "." or ")"

        A search is performed only below the data region.
        """
        #: finds a footnote cell that possibly contains some text as well
        fn_parser = CellParser(r'^([*#\.o†\da-z][\.\)]?)(?!\d)\s?(([\w\[\]\s\:]+)?\.?)\s?$')
        for fn in fn_parser.parse(self._pre_cleaned_table):
            if fn[0] > self._cc4[0]:
                footnote = Footnote(self, prefix=fn[2][0], prefix_cell=(fn[0], fn[1]), text=fn[2][1])
                yield footnote

    @staticmethod
    def empty_cells(table, regex=r'^([\s\-\–\"]+)?$'):
        """
        Returns a mask with `True` for all empty cells in the original array and `False` for non-empty cells.
        The regular expression which defines an empty cell can be tweaked.
        """
        empty = np.full_like(table, fill_value=False, dtype=bool)
        empty_parser = CellParser(regex)
        for empty_cell in empty_parser.parse(table, method='fullmatch'):
            empty[empty_cell[0], empty_cell[1]] = True
        return empty

    @staticmethod
    def _empty_string(string):
        """
        Returns `True` if a particular string is empty, which is defined with a regular expression.

        :param string: Input string for testing
        :type string: str
        :return: True/False
        """
        empty_parser = StringParser(r'^([\s\-\–\"]+)?$')
        return empty_parser.parse(string, method='fullmatch')

    def _pre_clean(self):
        """
        Removes empty and duplicate rows and columns that extend over the whole table.
        """

        # find empty rows and delete them
        empty_rows = []
        for row_index, row in enumerate(self._raw_table_empty):
            if False not in row:
                empty_rows.append(row_index)
        log.info("Empty rows {} deleted.".format(empty_rows))
        self._pre_cleaned_table = np.delete(self._pre_cleaned_table, empty_rows, axis=0)

        # find empty columns and delete them
        empty_columns = []
        for column_index, column in enumerate(self._raw_table_empty.T):
            if False not in column:
                empty_columns.append(column_index)
        log.info("Empty columns {} deleted.".format(empty_columns))
        self._pre_cleaned_table = np.delete(self._pre_cleaned_table, empty_columns, axis=1)

        # delete duplicate rows that extend over the whole table
        _, indices = np.unique(self._pre_cleaned_table, axis=0, return_index=True)
        # for logging only, which rows have been removed
        removed_rows = []
        for row_index in range(0, len(self._pre_cleaned_table)):
            if row_index not in indices:
                removed_rows.append(row_index)
        log.info("Duplicate rows {} removed.".format(removed_rows))
        # deletion:
        self._pre_cleaned_table = self._pre_cleaned_table[np.sort(indices)]

        # delete duplicate columns that extend over the whole table
        _, indices = np.unique(self._pre_cleaned_table, axis=1, return_index=True)
        # for logging only, which rows have been removed
        removed_columns = []
        for column_index in range(0, len(self._pre_cleaned_table.T)):
            if column_index not in indices:
                removed_columns.append(column_index)
        log.info("Duplicate columns {} removed.".format(removed_columns))
        # deletion:
        self._pre_cleaned_table = self._pre_cleaned_table[:, np.sort(indices)]
        log.info(
            "Table shape changed from {} to {}.".format(np.shape(self.raw_table), np.shape(self._pre_cleaned_table)))


    def _copy_footnotes(self, footnote):
        """
        Updates the pre-cleaned table with updated reference cells for a given footnote
        """
        if not np.array_equal(self._pre_cleaned_table, footnote.pre_cleaned_table):
            self._pre_cleaned_table = np.copy(footnote.pre_cleaned_table)
            #self.pre_cleaned_table_empty = self.empty_cells(self._pre_cleaned_table)
            self.history._footnotes_copied = True
            log.info("METHOD. Footnotes copied into cells.")


    def _label_sections(self):
        """
        Labelling of all classification table elements.
        """


        cc4 = find_cc4(self)
        log.info("Table Cell CC4 = {}".format(cc4))
        # self.labels[cc4] = 'CC4'
        self._cc4 = cc4

        for footnote in self._find_footnotes():
            self._footnotes.append(footnote)
            if self._configs['use_footnotes']:
                self._copy_footnotes(footnote)

        try:
            cc1, cc2 = self._find_cc1_cc2(cc4, self._pre_cleaned_table)
        except (MIPSError, TypeError):
            msg = "ERROR: Main MIPS Algorithm failed. Maybe the input table is bad!"
            log.critical(msg)
            raise MIPSError(msg)
        else:
            log.info("Table Cell CC1 = {}; Table Cell CC2 = {}".format(cc1, cc2))
            self._cc1 = cc1
            self._cc2 = cc2

        # provisions for header extension
        if self._configs['use_header_extension']:
            self._cc1 = self._header_extension(self._cc1)
            log.info("Header extension, new cc1 = {}".format(self._cc1))

        cc3 = self._find_cc3(cc2)
        log.info("Table Cell CC3 = {}".format(cc3))
        # self.labels[cc3] = 'CC3'
        self._cc3 = cc3



    @staticmethod
    def _categorize_header(header):
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

    def _split_table(self):
        """
        Splits table into subtables. Yields :class:`~tabledataextractor.table.table.Table` objects.

        Algorithm:
            If the stub header is repeated in the column header section the table is split up before
            the repeated element.

        """

        # first, the column header
        i = 0
        # the last row of the column/stub header is not used, as it will be determined as
        # data region by the main MIPS algorithm
        for col_index, column in enumerate(self.col_header[:-1].T):
            # the first match is backwards and forwards looking
            if i == 0 and column.size > 0 and \
                    self.stub_header[:-1].T[0].size > 0 and \
                    np.array_equal(column, self.stub_header[:-1].T[0]):
                yield Table(self._pre_cleaned_table[:, 0:col_index + 1].tolist())
                i += 1
            # every other match is only forwards looking
            if i > 0 and column.size > 0 and \
                    self.stub_header[:-1].T[0].size > 0 and \
                    np.array_equal(column, self.stub_header[:-1].T[0]):
                yield Table(self._pre_cleaned_table[:, col_index + 1:col_index + i * col_index + 2].tolist())
                i += 1

        # now the same thing for the row header
        i = 0
        for row_index, row in enumerate(self.row_header[:, :-1]):
            # the first match is backwards and forwards looking
            if i == 0 and row.size > 0 and \
                    self.stub_header[0, :-1].size > 0 and \
                    np.array_equal(row, self.stub_header[0, :-1]):
                yield Table(self._pre_cleaned_table[0:row_index + 1, :].tolist())
                i += 1
            # every other match is only forwards looking
            if i > 0 and row.size > 0 and \
                    self.stub_header[0, :-1].size > 0 \
                    and np.array_equal(row, self.stub_header[0, :-1]):
                yield Table(self._pre_cleaned_table[row_index + 1:row_index + i * row_index + 2, :].tolist())
                i += 1

    @property
    def subtables(self):
        """List of all subtables. Each subtable is an instance of :class:`~tabledataextractor.table.table.Table`."""
        tables = []
        g = self._split_table()
        while True:
            try:
                subtable = next(g, None)
            except MIPSError as e:
                log.exception("Subtable MIPS failure {}".format(e.args))
                break
            else:
                if subtable is None:
                    break
                else:
                    tables.append(subtable)
        return tables

    def _build_category_table(self, table, cc1, cc2, cc3, cc4):
        """
        Build category table for given input table.
        Uses a Pandas data frame is to create the category table.

        :param table: Table on which to perform the categorization
        :param cc1: key MIPS cell
        :param cc2: key MIPS cell
        :param cc3: key MIPS cell
        :param cc4: key MIPS cell
        :return: category table as numpy array
        """

        # Obsolete code, original header factorization, according to Embley et al.
        # column_header = table[cc1[0]:cc2[0] + 1, cc3[1]:cc4[1] + 1]
        # row_header = table[cc3[0]:cc4[0] + 1, cc1[1]:cc2[1] + 1]
        # column_factors = self._categorize_header(column_header.T)
        # row_factors = self._categorize_header(row_header)

        # Make the Pandas DataFrame
        dataframe = to_pandas(self)
        category_table = build_category_table(dataframe)
        return category_table

    def contains(self, pattern):
        """
        Returns true if table contains a particular string.

        :param pattern: Regular expression for input
        :return: True/False
        """
        parser = StringParser(pattern)
        for row in self.category_table:
            string = row[0] + ' '
            string += ' '.join(row[1]) + ' '
            string += ' '.join(row[2])
            if parser.parse(string, method='search'):
                return True
        return False

    def print(self):
        """Prints raw table, cleaned table and labels nicely."""
        log.info("Printing table: {}".format(self._file_path))
        print_table(self.raw_table)
        print_table(self._pre_cleaned_table)
        print_table(self.labels)

    def print_raw_table(self):
        """Prints raw input table nicely."""
        print_table(self.raw_table)

    def to_csv(self, file_path):
        log.info("Saving raw table to .csv to file: {}".format(self._file_path))
        write_to_csv(self.raw_table, file_path=file_path)

    def to_pandas(self):
        log.info("Converting table to Pandas DataFrame: {}".format(self._file_path))
        return to_pandas(self)

    def __str__(self):
        """As the user wants to see it"""
        log.info("Printing table: {}".format(self._file_path))
        t = list_as_PrettyTable(self.category_table)
        return str(t)

    def __repr__(self):
        """As the developer wants to see it"""
        intro = "Table({}, table_number={}, transposed={})".format(self._file_path, self._table_number, self.history.table_transposed)
        log.info("Repr. table: {}".format(self._file_path))
        array_width = np.shape(self._pre_cleaned_table)[1]
        input_string = as_string(self.raw_table)
        results_string = as_string(
            np.concatenate(
                (self._pre_cleaned_table, np.full((1, array_width), "", dtype='<U60'), self.labels)
            )
        )
        t = list_as_PrettyTable(self.category_table)
        return intro + "\n\n" + input_string + results_string + str(t)







