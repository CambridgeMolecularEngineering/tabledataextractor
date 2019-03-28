# -*- coding: utf-8 -*-
"""
Footnote handling.

.. codeauthor:: Juraj Mavračić <jm2111@cam.ac.uk>

"""

import logging
import numpy as np
import re
from .parse import CellParser

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Footnote:
    """
    Defines a footnote found in the provided table.
    Contains elements of a footnote.
    Will construct the footnote and find all associated elements.

    :param table: table to work on
    :type table: ~tabledataextractor.table.table.Table
    :param prefix: Prefix that has been identified as footnote prefix
    :type prefix: str
    :param prefix_cell: Index of the cell containing the associated prefix
    :type prefix_cell: (int, int)
    :param text: Optional. Text associated with the found footnote prefix
    :type text: str
    """

    def __init__(self, table, prefix, prefix_cell, text):
        self._table = table
        self.pre_cleaned_table = np.copy(self._table.pre_cleaned_table)

        #: Prefix string, e.g., `"a)"`.
        self.prefix = prefix

        #: Cell index of the prefix, e.g., `(7,0)`.
        self.prefix_cell = prefix_cell

        #: Cell of the footnote text, e.g., `(7,1)`.
        self.text_cell = self.prefix_cell if text else self._find_text_cell()

        #: Footnote text, e.g., `"This is the text of a footnote"`.
        self.text = text if text else self._find_text()

        #: Cell indexes of the cells containing the footnote references within the table.
        self.reference_cells = self._find_reference_cells()

        #: Cell content of the cells contatining the footnote references within the table.
        self.references = self._find_references()

    def _find_text_cell(self):
        """Finds the cell index containing the text associated with the prefix."""
        for column_index in range(self.prefix_cell[1] + 1, np.shape(self.pre_cleaned_table)[1]):
            if not self._table.pre_cleaned_table_empty[self.prefix_cell[0], column_index]:
                return self.prefix_cell[0], column_index
            return None

    def _find_text(self):
        """Finds the text associated with the prefix, only one cell can contain the text."""
        if self.text_cell is not None:
            return str(self.pre_cleaned_table[self.text_cell])
        else:
            return ""

    def _find_reference_cells(self):
        """
        Searches the entire table above each footnote for the previously detected footnote prefix.
        Updates the footnote-internal version of the `pre-cleaned table`, by cutting out the footnote prefix out of the reference cell.

        Rules for matching:

            1. if prefix is `number`:
                a) matches if `(anything)+space+prefix`
            2. if prefix is `a-z`:
                a) matches if `(anything)+space+prefix` OR
                b) matches if `prefix`
            3. else:
                a) matches if found anywhere in any cell

        :return: [(int,int)]

        """
        # indices of the references
        fn_refs = []

        # Case 1a If prefix is number, general
        if re.fullmatch(pattern='[\d]{1,2}', string=self.prefix):
            log.debug("Footnote prefix {} is number".format(self.prefix))
            fn_ref_parser_1a = CellParser('(^.+\s)(' + self.prefix + ')(\s.+)?$')
            for fn_ref in fn_ref_parser_1a.parse(self.pre_cleaned_table[0:self.prefix_cell[0]], method='match'):
                fn_refs.append(fn_ref[:2])
                stripped_text = fn_ref[2][0]
                stripped_text += self.text if self.text is not None else ""
                if fn_ref[2][2] is not None:
                    stripped_text += fn_ref[2][2]
                self.pre_cleaned_table[fn_ref[:2]] = stripped_text

        # Case 2a If prefix is a-z:
        elif re.fullmatch(pattern='[a-zA-Z]', string=self.prefix):
            log.debug("Footnote prefix {} is letter".format(self.prefix))
            fn_ref_parser_2a = CellParser('(^.+\s)(' + self.prefix + ')(\s.+)?$')
            for fn_ref in fn_ref_parser_2a.parse(self.pre_cleaned_table[0:self.prefix_cell[0]], method='match'):
                fn_refs.append(fn_ref[:2])
                stripped_text = fn_ref[2][0]
                stripped_text += self.text if self.text is not None else ""
                if fn_ref[2][2] is not None:
                    stripped_text += fn_ref[2][2]
                self.pre_cleaned_table[fn_ref[:2]] = stripped_text

            # Case 2b If prefix is a-z and alone in the cell
            fn_ref_parser_2b = CellParser('^(' + self.prefix + ')$')
            for fn_ref in fn_ref_parser_2b.parse(self.pre_cleaned_table[0:self.prefix_cell[0]], method='match'):
                log.debug("Footnote prefix {} is letter and is alone in cell.".format(self.prefix))
                fn_refs.append(fn_ref[:2])
                stripped_text = self.text if self.text is not None else ""
                self.pre_cleaned_table[fn_ref[:2]] = stripped_text

        # Case 3, everything else
        else:
            fn_ref_parser = CellParser('(' + re.escape(self.prefix) + ')')
            repl = " "+self.text+" " if self.text is not None else " "
            for fn_ref in fn_ref_parser.replace(self.pre_cleaned_table[0:self.prefix_cell[0]],
                                                repl=repl,
                                                method='search'):
                fn_refs.append(fn_ref[:2])
                stripped_text = fn_ref[2]
                self.pre_cleaned_table[fn_ref[:2]] = stripped_text

        return fn_refs

    def _find_references(self):
        """Collects the raw references, no cleanup"""
        references = []
        for cell in self.reference_cells:
            references.append(self._table.pre_cleaned_table[cell])
        return references

    def __str__(self):
        return "Prefix: {:4}   Text: {:60}   Ref. Cells: {}   " \
               "References: {}".format("'"+str(self.prefix)+"'",
                                       "'"+str(self.text)+"'",
                                       str(self.reference_cells),
                                       str(self.references))


def find_footnotes(table_object):
    """
    Finds a footnote and yields a :class:`~tabledataextractor.table.footnotes.Footnote` object with all the appropriate properties.
    A footnote is defined with::

        FNprefix  = \*, #, ., o, †; possibly followed by "." or ")"

    A search is performed only below the data region.

    :param table_object: Input Table object
    :type table_object: ~tabledataextractor.table.table.Table
    """
    #: finds a footnote cell that possibly contains some text as well
    fn_parser = CellParser(r'^([*#\.o†\da-z][\.\)]?)(?!\d)\s?(([\w\[\]\s\:]+)?\.?)\s?$')
    for fn in fn_parser.parse(table_object.pre_cleaned_table):
        if fn[0] > table_object._cc4[0]:
            footnote = Footnote(table_object, prefix=fn[2][0], prefix_cell=(fn[0], fn[1]), text=fn[2][1])
            yield footnote

