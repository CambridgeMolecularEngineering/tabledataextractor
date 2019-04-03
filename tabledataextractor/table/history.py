# -*- coding: utf-8 -*-
"""
Indicates to the user which methods have been used on the table.
This should be checked for testing on a sample dataset, to justify the choice of settings for the given domain.

.. codeauthor:: Juraj Mavračić <jm2111@cam.ac.uk>

"""

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class History:
    """
    Stores `True`/`False` for each property, indicating if a method has been used on the particular :class:`~tabledataextractor.table.table.Table` instance.
    """

    def __init__(self):
        self._title_row_removed = False
        self._prefixing_performed = False
        self._prefixed_rows = False
        self._footnotes_copied = False
        self._spanning_cells_extended = False
        self._header_extended = False
        self._table_transposed = False
        log.info("History() object created.")

    @property
    def title_row_removed(self):
        """Indicates whether a title row has been removed from the table."""
        return self._title_row_removed

    @property
    def prefixing_performed(self):
        """Indicates whether prefixing has been performed on the table."""
        return self._prefixing_performed

    @property
    def prefixed_rows(self):
        """Indicates whether prefixing has been performed on the rows (left side)."""
        return self._prefixed_rows

    @property
    def footnotes_copied(self):
        """Indicates whether footnotes have been copied into the table cells."""
        return self._footnotes_copied

    @property
    def spanning_cells_extended(self):
        """
        Indicates whether the content of cells has been duplicated into neighbouring cells,
        in case of cells that are merged cells (spanning cells).
        """
        return self._spanning_cells_extended

    @property
    def header_extended(self):
        """Indicates whether the header has been extended beyond the result obtained by the MIPS
         (*Minimum Indexing Point Search*) algorithm."""
        return self._header_extended

    @property
    def table_transposed(self):
        """Indicates whether the table has been transposed."""
        return self._table_transposed

    def __repr__(self):
        out = str()
        out += "title_row_removed       = {}".format(self.title_row_removed)
        out += "\n" + "prefixing_performed     = {}".format(self.prefixing_performed)
        out += "\n" + "prefixed_rows           = {}".format(self.prefixed_rows)
        out += "\n" + "footnotes_copied        = {}".format(self.footnotes_copied)
        out += "\n" + "spanning_cells_extended = {}".format(self.spanning_cells_extended)
        out += "\n" + "header_extended         = {}".format(self.header_extended)
        out += "\n" + "table_transposed        = {}".format(self._table_transposed)
        return out







