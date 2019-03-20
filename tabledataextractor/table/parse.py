# -*- coding: utf-8 -*-
"""
Tools for parsing the table based on regular expressions.
"""

import logging
import re
import numpy as np

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


class CellParser:
    """
    :param pattern: Regular expression pattern which defines the cell parser. Use `grouping`, since matching strings will be returned explicitly.
    :type pattern: str

    """
    def __init__(self, pattern):

        log.info('Initialization of CellParser with regex pattern: "{}"'.format(pattern))
        assert isinstance(pattern, str)
        self.pattern = pattern

    def parse(self, table, method='match'):
        """
        Inputs a table and yields a tuple with the index of the next matching cell, as well as the string that
        was matched.

        :param method:  `search`, `match` or `fullmatch`; Python `Regular expressions <https://docs.python.org/3.6/library/re.html>`_
        :type method: str
        :param table: Input table to be parsed
        :type table: numpy.ndarray
        :yield: (int, int, str) with index of cells and the strings of the groups that were matched

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

    def cut(self, table, method='match'):
        """
        Inputs a table and yields a tuple with the index of the next matching cell, as well as a string
        that is obtained from the original string by cutting out the match string.

        :param method:  `search`, `match` or `fullmatch`; see Python `Regular expressions <https://docs.python.org/3.6/library/re.html>`_
        :type method: str
        :param table: Input table to be parsed, of type 'numpy.ndarray'
        :type table: numpy.ndarray
        :yield: (int, int, str) with index of cells and the strings of the groups that were matched

        """
        # check if table is of correct type
        assert isinstance(table, np.ndarray)

        prog = re.compile(self.pattern)
        for result in self.parse(table, method):
            yield result[0], result[1], prog.sub("", table[result[:2]])

    def replace(self, table, repl, method='match'):
        """
        Inputs a table and yields a tuple with the index of the next matching cell, as well as a string
        that is obtained from the original string by cutting out the match string and replacing it with another string.

        :param method: `search`, `match` or `fullmatch`; see Python `Regular expressions <https://docs.python.org/3.6/library/re.html>`_
        :type method: str
        :param table: Input table to be parsed
        :type table: numpy.ndarray
        :param repl: Replacement string that will be included instead of the patters
        :type repl: str
        :yield: (int, int, str) with index of cells and the strings of the groups that were matched

        """

        # check if table is of correct type
        assert isinstance(table, np.ndarray)

        prog = re.compile(self.pattern)
        for result in self.parse(table, method):
            yield result[0], result[1], prog.sub(repl, table[result[:2]])


class StringParser:
    """
    :param pattern: Regular expression pattern that defines the string parser.
    :type pattern: str

    """
    def __init__(self, pattern):
        assert isinstance(pattern, str)
        self.pattern = pattern

    def parse(self, string, method='match'):
        """
        Inputs a string and returns `True` if pattern matches.

        :param string: Input string
        :param method: `search`, `match` or `fullmatch`; see Python `Regular expressions <https://docs.python.org/3.6/library/re.html>`_
        :type string: str
        :type method: str
        :return: True/False
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

    def cut(self, string):
        """
        Inputs a string and returns the same string with the pattern cut out

        :param string: Input string
        :type string: str
        :return: string with `pattern` cut out
        """

        # check if string is of correct type
        assert isinstance(string, str)

        prog = re.compile(self.pattern)
        result = prog.sub(string, "")
        return result
