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

from tabledataextractor.table.algorithms import find_cc4, find_cc1_cc2, prefix_duplicate_labels, duplicate_spanning_cells, header_extension, find_cc3, find_title_row, find_note_cells, empty_cells, pre_clean, split_table
from tabledataextractor.table.footnotes import find_footnotes

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
            return build_category_table(to_pandas(self))
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
        return empty_cells(self._pre_cleaned_table)

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
        self._raw_table_empty = empty_cells(self.raw_table)

        # check if array is empty
        if self._raw_table_empty.all():
            msg = 'Input table is empty.'
            log.critical(msg)
            raise InputError(msg)

        self._pre_cleaned_table = pre_clean(self.raw_table)
        log.info("Table shape changed from {} to {}.".format(np.shape(self.raw_table), np.shape(self.pre_cleaned_table)))

        if self._configs['use_spanning_cells']:
            self._pre_cleaned_table = duplicate_spanning_cells(self, self._pre_cleaned_table)

        # prefixing of duplicate labels in the header region
        if self._configs['use_prefixing']:
            self._pre_cleaned_table = prefix_duplicate_labels(self, self._pre_cleaned_table)

        self._label_sections()

    def transpose(self):
        """
        Transposes the :class:`~tabledataextractor.Table.raw_table` and calls the :class:`~tabledataextractor.Table._analyze_table` function again.
        In this way, if working interactively from a Jupyter notebook, it is possible to input a table and then
        transpose it.
        """
        self._history = History()
        self.history._table_transposed = True
        self._analyze_table()

    def _copy_footnotes(self, footnote):
        """
        Updates the pre-cleaned table with updated reference cells for a given footnote
        """
        if not np.array_equal(self._pre_cleaned_table, footnote.pre_cleaned_table):
            self._pre_cleaned_table = np.copy(footnote.pre_cleaned_table)
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

        for footnote in find_footnotes(self):
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

    @property
    def subtables(self):
        """List of all subtables. Each subtable is an instance of :class:`~tabledataextractor.table.table.Table`."""
        tables = []
        g = split_table(self)
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
                    tables.append(Table(subtable))
        return tables

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







