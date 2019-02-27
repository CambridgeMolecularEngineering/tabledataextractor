# -*- coding: utf-8 -*-
"""
Footnote handling

.. codeauthor:: Juraj Mavračić <jm2111@cam.ac.uk>

"""

import logging
import numpy as np
from .parse import CellParser


class Footnote:
    """
    Defines a footnote found in the provided table.
    Contains elements of the footnote:
        * prefix_string, prefix_cell
        * text, text_cell
        * reference_cells
    """

    def __init__(self, table, prefix_string, prefix_cell, text):
        """
        Will construct the footnote and find all associated elements
        :param table: TDE Table() object
        :type Table: Table()
        """
        self.table = table
        self.prefix_string = prefix_string
        self.prefix_cell = prefix_cell
        self.text = text
        self.text_cell = self.prefix_cell if self.text is not None else None

        #TODO Find text and text cells
        #TODO Find reference cells

    def _find_text(self):
        # append all non-empty cells following fn_prefix index in the same row
        for column_index in range(self.prefix_cell[1] + 1, np.shape(self.table.pre_cleaned_table)[1]):
            if not self.table.pre_cleaned_table_empty[self.prefix_cell[0], column_index]:
                return self.prefix_cell[0], column_index

    def __str__(self):
        return "Prefix: " + str(self.prefix_string) + \
               "  Cell: " + str(self.prefix_cell) + \
               "  Text: " + str(self.text) + \
               "  Cell: " + str(self.text_cell)




