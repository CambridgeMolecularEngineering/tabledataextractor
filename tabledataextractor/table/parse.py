# -*- coding: utf-8 -*-
"""
tabledataextractor.table.parse

Toold for parsing the table based on Regex expressions etc.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""

import logging
import re

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class CellParser:

    def __init__(self,pattern):
        log.info('Initialization of CellParser with regex pattern: "{}"'.format(pattern))
        self.pattern = pattern

    def parse(self,table,method='match'):
        """
        Inputs a Table object and yields a tuple with the index of the next matching cell.
        Parameter 'method = search', 'method = match', 'method = fullmatch' (see python re manual)

        :param:
        :return: Tuple(int,int)
        """

        # check if table is of correct type
        # assert isinstance(table, )

        result = None
        prog = re.compile(self.pattern)

        for row_index,row in enumerate(table):
            for column_index,cell in enumerate(row):
                if method == 'match':
                    result = prog.match(cell)
                elif method == 'fullmatch':
                    result = prog.fullmatch(cell)
                elif method == 'search':
                    result = prog.search(cell)
                if result:
                    yield row_index,column_index








