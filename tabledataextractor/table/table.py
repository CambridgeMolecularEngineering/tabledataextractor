# -*- coding: utf-8 -*-
"""
tabledataextractor.table.table

Raw, processed and final table objects.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""

import logging
import numpy as np
from tabledataextractor.input import from_csv
from tabledataextractor.output.print import print_table

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Table:

    def __init__(self, file_path):
        log.info('Initialization of table: "{}"'.format(file_path))
        self.file_path = file_path
        self.raw_table = from_csv.read(file_path)

        # check if everything is ok with the raw table
        if not isinstance(self.raw_table, np.ndarray):
            msg = 'Input was not proeprly converted to numpy array.'
            log.critical(msg)
            raise TypeError(msg)

        # mask, cell = True if cell is empty
        self.empty = np.empty_like(self.raw_table, dtype=bool)
        self.empty_cells()
        log.debug("Empty cells in {}:\n{}".format(file_path, self.empty))

        # pre-cleaned table
        self.pre_cleaned_table = np.copy(self.raw_table)
        self.pre_clean()

        # shadow table with labels
        self.labels = np.empty_like(self.raw_table, dtype="<U20")
        self.label_sections()

    def find_cc4(self):
        """
        Searches for cell 'CC4'.

        Searching from the bottom of the original table for the last row with a minority of empty cells.
        Rows with at most a few empty cells are assumed to be part of the data region rather than notes or footnotes rows
        (which usually have only one or two non-empty cells).

        :return: (int,int)
        """
        # searching from the bottom of original table:
        n_rows = len(self.raw_table)
        for row_index in range(n_rows - 1, -1, -1):
            # counting the number of full cells
            # if n_empty < n_full terminate, this is our goal row
            n_full = 0
            n_columns = len(self.empty[row_index])
            for empty in self.empty[row_index]:
                if not empty:
                    n_full += 1
                if n_full > int(n_columns / 2):
                    return row_index, n_columns - 1


    def find_cc2_cc3(self,cc4):
        """
        Searches for cells 'CC2' and 'CC3' using the MIPS algorithm.

        """

        # Initialize
        c_max = cc4[1]; r_max = cc4[0]
        r1 = 0; c1 = 0; r2 = r_max - 1; c2 = 0
        rightflag = 0; upflag = 0
        max_area = 0

        # Locate candidate MIPs by finding the minimum indexing headers:
        #while c2 < c_max and r2 >= r1:
            # if [r2 + 1, c1 : r_max, c2] has no duplicate rows and [r1, c2 + 1 : r2 - 1, c_max] has no duplicate columns

        #    temp_section = self.raw_table[ r2+1 : r_max, c1 : c2]

            # check if there are duplicate rows in temp_section which are not empty










        # correct
        return (3,0),(5,1)
































    def empty_cells(self):
        for i, row in enumerate(self.raw_table):
            for j, cell in enumerate(row):
                if cell == '':
                    self.empty[i, j] = True
                else:
                    self.empty[i, j] = False



    def pre_clean(self):
        """
        Remove empty and duplicate rows and columns that extend over the whole table

        :return:
        """

        # find empty rows and delete them
        empty_rows = []
        for row_index,row in enumerate(self.empty):
            if False not in row:
                empty_rows.append(row_index)
        log.debug("Empty rows {} deleted.".format(empty_rows))
        self.pre_cleaned_table = np.delete(self.pre_cleaned_table,empty_rows, axis=0)

        # find empty columns and delete them
        empty_columns = []
        for column_index,column in enumerate(self.empty.T):
            if False not in column:
                empty_columns.append(column_index)
        log.debug("Empty columns {} deleted.".format(empty_columns))
        self.pre_cleaned_table = np.delete(self.pre_cleaned_table,empty_columns, axis=1)

        # TODO Finish removing duplicated rows and columns
        # delete duplicate rows that extend over the whole table
        self.pre_cleaned_table,indices = np.unique(self.pre_cleaned_table,axis=0,return_index=True)
        log.debug("Indices are: {}".format(indices))





    def label_sections(self):
        """
        Labelling of all classification table elements.
        """

        cc4 = self.find_cc4()
        log.debug("Table Cell CC4 = {}".format(cc4))
        self.labels[cc4] = 'CC4'

        cc2,cc3 = self.find_cc2_cc3(cc4)
        log.debug("Table Cell CC2 = {}; Table Cell CC3 = {}".format(cc2,cc3))
        self.labels[cc2] = 'CC2'
        self.labels[cc3] = 'CC3'








    def print(self):
        log.info("Printing table: {}".format(self.file_path))
        print_table(self.raw_table)
        print_table(self.labels)
        print_table(self.pre_cleaned_table)
