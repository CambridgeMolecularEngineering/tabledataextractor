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


class Table():

    def __init__(self,file_path):
        log.info('Initialization of table: "{}"'.format(file_path))
        self.file_path = file_path
        self.raw_table = from_csv.read(file_path)

        # check if everything is ok with the raw table
        if not isinstance(self.raw_table,np.ndarray):
            msg = 'Input was not proeprly converted to numpy array.'
            log.critical(msg)
            raise TypeError(msg)

        # mask, cell = True if cell is empty
        self.empty = np.empty_like(self.raw_table,dtype=bool)
        self.empty_cells()
        log.debug("Empty cells in {}:\n{}".format(file_path,self.empty))

        # shadow table with labels
        self.labels = np.empty_like(self.raw_table,dtype="<U20")
        self.label_sections()






    def find_CC4(self):
        """
        Searches for cell 'CC4'

        :return: (int,int)
        """

        # Searching from the bottom of the original table for the last row with a minority of empty cells
        # Rows with at most a few empty cells are assumed to be part of the data region rather than notes or footnotes rows
        # (which usually have only one or two non-empty cells)
        # TODO Finish the find CC4 function
        for i,row in enumerate(np.flipud(self.empty)):
            n_empty = 0
            n_full = 0
            for cell in enumerate(row):
                if cell == True:
                    n_empty = n_empty + 1
                else:
                    n_full = n_full + 1
            if n_full > n_empty:
                return i,len(row)-1


    def empty_cells(self):
        for i,row in enumerate(self.raw_table):
            for j,cell in enumerate(row):
                if cell == '':
                    self.empty[i,j] = True
                else:
                    self.empty[i,j] = False

    def label_sections(self):
        """
        Labelling of all classification table elements

        :return:
        """
        cc4 = self.find_CC4()
        print(cc4)
        self.labels[cc4] = 'CC4'


    def print(self):
        log.info("Printing of table: {}".format(self.file_path))
        print_table(self.raw_table)
        print_table(self.labels)





