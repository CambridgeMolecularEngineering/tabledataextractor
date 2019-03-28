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

from tabledataextractor.table.algorithms import find_cc4, find_cc1_cc2, prefix_duplicate_labels, duplicate_spanning_cells, header_extension, find_cc3, find_title_row, find_note_cells
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
            return find_title_row(self)

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
        for note_cell in find_note_cells(self, temp):
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
            self._pre_cleaned_table = duplicate_spanning_cells(self, self._pre_cleaned_table)
            # self._pre_cleaned_table_empty = self.empty_cells(self._pre_cleaned_table)

        # prefixing of duplicate labels in the header region
        if self._configs['use_prefixing']:
            self._pre_cleaned_table = prefix_duplicate_labels(self, self._pre_cleaned_table)
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

    # @staticmethod
    # def _empty_string(string):
    #     """
    #     Returns `True` if a particular string is empty, which is defined with a regular expression.
    #
    #     :param string: Input string for testing
    #     :type string: str
    #     :return: True/False
    #     """
    #     empty_parser = StringParser(r'^([\s\-\–\"]+)?$')
    #     return empty_parser.parse(string, method='fullmatch')

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
            cc1, cc2 = find_cc1_cc2(self, cc4, self._pre_cleaned_table)
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
            self._cc1 = header_extension(self, self._cc1)
            log.info("Header extension, new cc1 = {}".format(self._cc1))

        cc3 = find_cc3(self, cc2)
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







