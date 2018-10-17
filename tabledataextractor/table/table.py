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
        self.raw_table_empty = self.empty_cells(self.raw_table)

        # pre-cleaned table
        self.pre_cleaned_table = np.copy(self.raw_table)
        self.pre_clean()
        self.pre_cleaned_table_empty = self.empty_cells(self.pre_cleaned_table)

        # shadow table with labels
        self.labels = np.empty_like(self.pre_cleaned_table, dtype="<U20")
        self.labels[:,:] = 'Not labeled.'
        self.label_sections()


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


    def find_cc1_cc2(self,cc4):
        """
        Searches for cells 'CC2' and 'CC3' using the MIPS algorithm.

        :param cc4: Tuple, position of CC4 cell found with find_cc4()
        :type cc4: int
        """

        # Initialize
        c_max = cc4[1]
        r_max = cc4[0]
        r1 = 0
        c1 = 0
        r2 = r_max - 1
        c2 = 0
        upflag = 0
        max_area = 0


        def table_slice(table,r2,r_max,c1,c2):
            """
            Function to cut the correct slice out of array for in find_cc1_cc2()
            :param table:
            :param r2:
            :param r_max:
            :param c1:
            :param c2:
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

            if r1 == r2-1 and c2+1 == c_max:
                section_2 = table[r1, c2+1]
            elif r1 == r2-1 and c2+1 != c_max:
                section_2 = table[r1, c2+1 : c_max+1]
            elif r1 != r2-1 and c2+1 != c_max:
                section_2 = table[r1 : r2-1+1, c2+1 : c_max+1]
            elif r1 != r2-1 and c2+1 == c_max:
                section_2 = table[r1 : r2-1+1, c2+1]
            else:
                log.critical("Not defined section_2, r2-1= {}, r1= {}, c2+1= {}, c_max= {}".format(r2-1, r1, c2+1, c_max))

            return section_1,section_2

        # Locate candidate MIPs by finding the minimum indexing headers:
        while c2 < c_max  and r2 >= r1:

            log.debug("Entering loop: c2= {}, c_max= {}, c1= {}, r2= {}, r1= {}".format(c2,c_max,c1,r2,r1))

            temp_section_1, temp_section_2 = table_slice(self.pre_cleaned_table,r2,r_max,c1,c2)

            log.debug("\ntemp_section_1:\n{}\n\t{: <40}\ntemp_section_2:\n{}".format(temp_section_1,"",temp_section_2))

            # check if there are duplicate rows in temp_section_1
            duplicate_rows = False
            # section array has to have a dimension of >0 and be non-empty for duplicate testing to make sense:
            if temp_section_1.ndim > 0 and temp_section_1.size:
                _, indices = np.unique(temp_section_1, axis=0, return_index=True)
                if len(temp_section_1) > len(indices):
                    duplicate_rows = True

            # check if there are duplicate columns in temp_section_2
            duplicate_columns = False
            # section array has to have a dimension of >0 and be non-empty for duplicate testing to make any sense:
            if temp_section_2.T.ndim > 0 and temp_section_2.T.size:
                _, indices = np.unique(temp_section_2.T, axis=0, return_index=True)
                if len(temp_section_2.T) > len(indices):
                    duplicate_columns = True

            if not duplicate_rows and not duplicate_columns:
                r2 = r2 - 1
                upflag = 1
            else:
                # ====================================================================================================
                # This part is added to the algorithm by me
                # re-initialize max_area if still 0 but we are about to change column
                # remember this cc2 as the first candidate
                # The 'if upflag == 1' check is uncertain, it needs to be tested on example tables, when there is no
                # header present etc.
                if max_area == 0 and upflag == 1:
                    data_area = (r_max - r2 + 1) * (c_max - c2 + 1)
                    log.debug("The data area of the FIRST C2 is: {}".format(data_area))
                    max_area = data_area
                    cc2 = (r2,c2)
                # ====================================================================================================

                c2 = c2 + 1

                log.debug("duplicate_rows = {}".format(duplicate_rows))
                log.debug("duplicate_columns = {}".format(duplicate_columns))

                if upflag == 1:
                    data_area = (r_max - r2 + 1) * (c_max - c2 + 1)
                    log.debug("The data area of the NEW C2 is: {}".format(data_area))
                    if data_area > max_area:
                        max_area = data_area
                        cc2 = (r2,c2)
                        log.debug("CC2 = {}".format(cc2))
                    upflag = 0

            log.debug("End of loop:   c2= {}, c_max= {}, c1= {}, r2= {}, r1= {}\n\n\n\n".format(c2,c_max,c1,r2,r1))

        # This is the CC1 part
        # Locate CC1 at intersection of the top row and the leftmost column necessary for indexing
        # r1 = 1; c1 = 1
        # unique_columns = True; unique_rows = True
        # temp_section_1 = self.pre_cleaned_table[ r1+1 : r2, c2+1 : c_max ]
        # temp_section_2 = self.pre_cleaned_table[ r2+1 : c2, c1+1 : r_max ] # strange
        # while unique_columns == True:
        #     _, indices = np.unique(temp_section_1, axis=1, return_index=True)
        #     if len(temp_section_1.T) != len(indices):
        #         unique_columns = False
        #     r1 += 1
        # while unique_rows == True:
        #     _, indices = np.unique(temp_section_2, axis=0, return_index=True)
        #     if len(temp_section_2) != len(indices):
        #         unique_rows = False
        #     c1 += 1
        # cc1 = (r1,c1)
        #return cc1,cc2

        return cc2


    def empty_cells(self,table):
        empty = np.empty_like(table, dtype=bool)
        for i, row in enumerate(table):
            for j, cell in enumerate(row):
                if cell == '':
                    empty[i, j] = True
                else:
                    empty[i, j] = False
        return empty


    def pre_clean(self):
        """
        Remove empty and duplicate rows and columns that extend over the whole table.

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

        cc4 = self.find_cc4()
        log.info("Table Cell CC4 = {}".format(cc4))
        self.labels[cc4] = 'CC4'

        # cc2,cc3 = self.find_cc1_cc2(cc4)
        # log.info("Table Cell CC1 = {}; Table Cell CC2 = {}".format(cc1,cc2))
        # self.labels[cc1] = 'CC1'
        # self.labels[cc2] = 'CC2'

        cc2 = self.find_cc1_cc2(cc4)
        log.info("Table Cell CC2 = {}".format(cc2))
        self.labels[cc2] = 'CC2'


    def print(self):
        log.info("Printing table: {}".format(self.file_path))
        print_table(self.raw_table)
        print_table(self.pre_cleaned_table)
        print_table(self.labels)
