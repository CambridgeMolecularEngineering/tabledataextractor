# -*- coding: utf-8 -*-
"""
tabledataextractor.table.table

Raw, processed and final labelled table.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""

import logging
import numpy as np
from tabledataextractor.input import from_csv
from tabledataextractor.output.print import print_table
from tabledataextractor.table.parse import CellParser

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
        self.labels[:,:] = '/'
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
        :type cc4: Tuple
        """

        # Initialize
        cc2 = None
        c_max = cc4[1]
        r_max = cc4[0]
        r1 = 0
        c1 = 0
        r2 = r_max - 1
        c2 = 0
        upflag = 0
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
            Function to cut the correct slices out of array for CC2 in find_cc1_cc2()
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
                section_1 = None

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
                section_2 = None

            return section_1,section_2

        def table_slice_1_cc1(table, r1, r2, c2, c_max):
            """
            Function to cut a correct slice out of array for CC1 in find_cc1_cc2()
            """
            # one more row and column index than in the published pseudocode is needed,
            # since the a:b notation in python doesn't include b
            if r1 + 1 == r2 and c2+1 == c_max:
                section = table[r1 + 1, c2+1]
            elif r1 + 1 == r2 and c2+1 != c_max:
                section = table[r1 + 1, c2+1:c_max+1]
            elif r1 + 1 != r2 and c2+1 != c_max:
                section = table[r1 + 1 : r2+1, c2 + 1:c_max+1]
            elif r1 + 1 != r2 and c2+1 == c_max:
                section = table[r1 + 1 : r2+1, c2 + 1]
            else:
                log.critical("Not defined section 1 for cc1, r1+1= {}, r2= {}, c2+1= {}, c_max= {}".format(r1+1, r2, c2+1, c_max))
                section = None
            return section

        def table_slice_2_cc1(table, r2, r_max, c1, c2):
            """
            Function to cut a correct slice out of array for CC1 in find_cc1_cc2()
            """
            # one more row and column index than in the published pseudocode is needed,
            # since the a:b notation in python doesn't include b
            if r2 + 1 == c2 and c1+1 == r_max:
                section = table[r2 + 1, c1 + 1]
            elif r2 + 1 == c2 and c1+1 != r_max:
                section = table[r2 + 1, c1+1 : r_max+1 ]
            elif r2 + 1 != c2 and c1+1 != r_max:
                section = table[r2+1 : c2+1, c1+1 : r_max+1 ]
            elif r2 + 1 != c2 and c1+1 == r_max:
                section = table[r2+1 : c2+1, c1+1]
            else:
                log.critical("Not defined section 2 for cc1, r2+1= {}, c2= {}, c1+1= {}, r_max= {}".format(r2+1, c2, c1+1, r_max))
                section = None
            return section

        # MAIN MIPS algorithm
        # Locate candidate MIPs by finding the minimum indexing headers:
        while c2 < c_max  and r2 >= r1:

            log.debug("Entering loop: c2= {}, c_max= {}, c1= {}, r2= {}, r1= {}".format(c2,c_max,c1,r2,r1))

            temp_section_1, temp_section_2 = table_slice_cc2(self.pre_cleaned_table,r2,r_max,c1,c2)

            log.debug("\ntemp_section_1:\n{}\n\t{: <40}\ntemp_section_2:\n{}".format(temp_section_1,"",temp_section_2))

            if not duplicate_rows(temp_section_1) and not duplicate_columns(temp_section_2):
                r2 = r2 - 1
                upflag = 1
            else:
                # ====================================================================================================
                # This part is added to the algorithm by me
                # re-initialize max_area if still 0 but we are about to change column
                # remember this cc2 as the first candidate
                # The 'if upflag == 1' check is uncertain, it needs to be tested on example tables, when there is no
                # header present etc.
                # It might be that, if there is no cc2 at all that due to the 'upflag == 1' check
                # nothing will be returned by the function, which would cause a crash
                if max_area == 0 and upflag == 1:
                    data_area = (r_max - r2 + 1) * (c_max - c2 + 1)
                    log.debug("The data area of the FIRST C2 is: {}".format(data_area))
                    max_area = data_area
                    cc2 = (r2,c2)
                # ====================================================================================================

                c2 = c2 + 1

                if upflag == 1:
                    data_area = (r_max - r2 + 1) * (c_max - c2 + 1)
                    log.debug("The data area of the NEW C2 is: {}".format(data_area))
                    if data_area > max_area:
                        max_area = data_area
                        cc2 = (r2,c2)
                        log.debug("CC2 = {}".format(cc2))
                    upflag = 0

            log.debug("End of loop:   c2= {}, c_max= {}, c1= {}, r2= {}, r1= {}\n\n\n\n".format(c2,c_max,c1,r2,r1))

        # re-initialization of r2 and c2 from cc2, added by me; missing in the pseudocode
        r2 = cc2[0]
        c2 = cc2[1]

        # Locate CC1 at intersection of the top row and the leftmost aolumn necessary for indexing:
        # test 'r1 < r2' added by me, missing in the pseudocode
        while not duplicate_columns(table_slice_1_cc1(self.pre_cleaned_table, r1, r2, c2, c_max)) and r1 < r2:
            r1 = r1 + 1
        # test 'c1 < c2' added by me, missing in the pseudocode
        while not duplicate_rows(table_slice_2_cc1(self.pre_cleaned_table, r2, r_max, c1, c2)) and c1 < c2:
            c1 = c1 + 1

        cc1 = (r1,c1)

        return cc1,cc2


    def find_cc3(self,cc2):
        """
        Searches for cell 'CC3', as the leftmost cell of the first filled row of data region.

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
        for row_index in range(cc2[0]+1,n_rows, 1):
            n_full = 0
            n_columns = len(self.pre_cleaned_table[row_index,cc2[1]+1:])
            for column_index in range(cc2[1]+1,n_columns,1):
                empty = self.pre_cleaned_table_empty[row_index,column_index]
                if not empty:
                    n_full += 1
                if n_full > int(n_columns / 2):
                    return (row_index, cc2[1]+1)
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

    def find_FNprefix(self):
        """
        Returns a list of cell indexes that match the FNprefix (*, #, ., o, †)
        :return:
        """
        result = []
        fn_prefix_parser = CellParser('^[*#.o†\d]')
        for fn_prefix in fn_prefix_parser.parse(self.pre_cleaned_table,method='match'):
            result.append(fn_prefix)



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

        title_row = self.find_title_row()

        cc4 = self.find_cc4()
        log.info("Table Cell CC4 = {}".format(cc4))
        self.labels[cc4] = 'CC4'

        cc1,cc2 = self.find_cc1_cc2(cc4)
        log.info("Table Cell CC1 = {}; Table Cell CC2 = {}".format(cc1,cc2))
        self.labels[cc1] = 'CC1'
        self.labels[cc2] = 'CC2'

        cc3 = self.find_cc3(cc2)
        log.info("Table Cell CC3 = {}".format(cc3))
        self.labels[cc3] = 'CC3'

        self.labels[title_row, :] = 'TableTitle'
        self.labels[cc1[0]:cc2[0]+1, cc1[1]:cc2[1]+1] = 'StubHeader'
        self.labels[cc3[0]:cc4[0]+1, cc1[1]:cc2[1]+1] = 'RowHeader'
        self.labels[cc1[0]:cc2[0]+1, cc3[1]:cc4[1]+1] = 'ColHeader'
        self.labels[cc3[0]:cc4[0]+1, cc3[1]:cc4[1]+1] = 'Data'

        # Footnotes
        # For labelling footnotes I need a regex labeler class, which will be a cell parser
        # so, to define fn_prefix, you will write:
        # fn_prefix = CellParser(string)
        # CellParser has a method which inputs a table object and returns the index-es of the cells with the given
        # match
        # the advantage of this is that CellParser will be general and enable me to parse anything I want, custom labels
        fn_prefix = self.find_FNprefix()
        log.info("FNPrefix Cells = {}".format(fn_prefix))


        # all non-empty unlabelled cells at this point are labelled 'Note'
        for note_cell in self.find_note_cells():
            self.labels[note_cell] = 'Note'


    def print(self):
        log.info("Printing table: {}".format(self.file_path))
        print_table(self.raw_table)
        print_table(self.pre_cleaned_table)
        print_table(self.labels)