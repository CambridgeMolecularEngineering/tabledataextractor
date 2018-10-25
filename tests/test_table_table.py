# -*- coding: utf-8 -*-
"""
tabledataextractor.tests.test_table_table.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test main table object.
These tests depend on the input from csv working properly.
Juraj Mavračić (jm2111@cam.ac.uk)
"""

import unittest
import logging

from tabledataextractor import Table

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TableCC4(Table):
    """Derivative of Table used to isolate testing for CC4"""
    def __init__(self, *args):
        super().__init__(*args)

    def label_sections(self):
        """Labels only CC4"""
        cc4 = self.find_cc4()
        log.info("Table Cell CC4 = {}".format(cc4))
        self.labels[cc4] = 'CC4'

class TestCC4(unittest.TestCase):

    def label_sections(self):
        """Labels only CC4"""
        cc4 = self.find_cc4()
        log.info("Table Cell CC4 = {}".format(cc4))
        self.labels[cc4] = 'CC4'

    def do_table(self, input_path, expected):
        log.debug("Test CC4, Table: {}".format(input_path))
        table = TableCC4(input_path)
        result = table.find_cc4()
        log.debug("Result = {}".format(result))
        self.assertTupleEqual(expected, result)

    def test_cc4_1(self):
        input_path = './data/table_example1.csv'
        expected = (6,7)
        self.do_table(input_path, expected)

    def test_cc4_2(self):
        """
        Here, the true result would actually be (4,5).
        However, in find_cc4() we choose the criterion that the data region starts, from below, when at least half of
        the row is non-empty.
        """
        input_path = './data/table_example2.csv'
        expected = (3,5)
        self.do_table(input_path, expected)

    def test_cc4_3(self):
        input_path = './data/table_example3.csv'
        expected = (7,10)
        self.do_table(input_path, expected)

    def test_cc4_4(self):
        input_path = './data/table_example4.csv'
        expected = (2,5)
        self.do_table(input_path, expected)

    def test_cc4_5(self):
        input_path = './data/table_example5.csv'
        expected = (3,5)
        self.do_table(input_path, expected)

    def test_cc4_6(self):
        input_path = './data/table_example6.csv'
        expected = (11,3)
        self.do_table(input_path, expected)

    def test_cc4_7(self):
        input_path = './data/table_example7.csv'
        expected = (8,10)
        self.do_table(input_path, expected)






if __name__ == '__main__':
    unittest.main()


