# -*- coding: utf-8 -*-
"""
Indicates which methods have been used on the table.
This should be checked for testing on a sample dataset, to justify the choice of settings for the given domain.

.. codeauthor:: Juraj Mavračić <jm2111@cam.ac.uk>

"""

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class History:
    """
    Stores ``True``/``False``, indicating if a method has been used on the particular ``Table()`` instance.
    """

    def __init__(self):
        self._title_row_removed = False
        self._prefixing_performed = False
        self._footnotes_copied = False
        self._spanning_cells_extended = False
        self._header_extended = False
        log.info("History() object created.")

    @property
    def title_row_removed(self):
        return self._title_row_removed

    @property
    def prefixing_performed(self):
        return self._prefixing_performed

    @property
    def footnotes_copied(self):
        return self._footnotes_copied

    @property
    def spanning_cells_extended(self):
        return self._spanning_cells_extended

    @property
    def header_extended(self):
        return self._header_extended

    def __repr__(self):
        out = str()
        out += "title_row_removed       = {}".format(self.title_row_removed)
        out += "\n" + "prefixing_performed     = {}".format(self.prefixing_performed)
        out += "\n" + "footnotes_copied        = {}".format(self.footnotes_copied)
        out += "\n" + "spanning_cells_extended = {}".format(self.spanning_cells_extended)
        out += "\n" + "header_extended         = {}".format(self.header_extended)
        return out







