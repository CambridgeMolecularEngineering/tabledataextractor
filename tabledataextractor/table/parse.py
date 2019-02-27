# -*- coding: utf-8 -*-
"""
Tools for parsing the table based on Regex expressions etc.
"""

import logging
import re
import numpy as np

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


class CellParser:

    def __init__(self, pattern):
        """
        :param pattern: Regex pattern which defines the cell parser. Use grouping, since matching strings will be returned
            explicitly.
        :type pattern: str
        """
        log.info('Initialization of CellParser with regex pattern: "{}"'.format(pattern))
        assert isinstance(pattern, str)
        self.pattern = pattern

    def parse(self, table, method='match'):
        """
        Inputs a Table object and yields a tuple with the index of the next matching cell, as well as the string that
        was matched.

        :param method:  'search', 'match' or 'fullmatch'; see python re documentation
        :type method: str
        :param table: Input table to be parsed, of type 'numpy.ndarray'
        :type table: numpy.ndarray
        :return: Tuple(int,int,str) with index of cells and the strings of the groups that were matched
        """

        # check if table is of correct type
        assert isinstance(table, np.ndarray)

        result = None
        prog = re.compile(self.pattern)

        for row_index, row in enumerate(table):
            for column_index, cell in enumerate(row):
                if method == 'match':
                    result = prog.match(cell)
                elif method == 'fullmatch':
                    result = prog.fullmatch(cell)
                elif method == 'search':
                    result = prog.search(cell)
                if result:
                    yield row_index, column_index, result.groups()


class StringParser:

    def __init__(self, pattern):
        """
        :param pattern: Regex pattern which defines the string parser. Returns True if pattern matches
        :type pattern: str
        """
        assert isinstance(pattern, str)
        self.pattern = pattern

    def parse(self, string, method='match'):
        """
        Inputs a string and returns true if pattern matches

        :param string:
        :param method:
        :return: str
        """

        # check if string is of correct type
        assert isinstance(string, str)

        result = None
        prog = re.compile(self.pattern)

        if method == 'match':
            result = prog.match(string)
        elif method == 'fullmatch':
            result = prog.fullmatch(string)
        elif method == 'search':
            result = prog.search(string)
        if result:
            return True
        else:
            return False

