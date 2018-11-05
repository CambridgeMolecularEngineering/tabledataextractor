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
        self.labels[cc4] = 'CC4'
        log.info("Table Cell CC4 = {}".format(cc4))

class TestCC4(unittest.TestCase):

    def do_table(self, input_path, expected):
        log.debug("Test CC4, Table: {}".format(input_path))
        table = TableCC4(input_path)
        table.print()
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


class TableCC1CC2(Table):
    """Derivative of Table used to isolate testing for CC1 and CC2"""
    def __init__(self, *args):
        super().__init__(*args)

    def label_sections(self):
        """Label CC1 and CC2 and stop."""
        cc4 = self.find_cc4()
        cc1,cc2 = self.find_cc1_cc2(cc4)
        log.info("Table Cell CC1 = {}; Table Cell CC2 = {}".format(cc1, cc2))
        self.labels[cc1] = 'CC1'
        self.labels[cc2] = 'CC2'


class TableCC3(Table):
    """Derivative of Table used to isolate testing for CC3"""
    def __init__(self, *args):
        super().__init__(*args)

    def label_sections(self):
        """Label CC3."""
        cc4 = self.find_cc4()
        cc1,cc2 = self.find_cc1_cc2(cc4)
        cc3 = self.find_cc3(cc2)
        log.info("Table Cell CC3 = {}".format(cc3))
        self.labels[cc3] = 'CC3'
        return cc3


class TestCC1CC2(unittest.TestCase):

    def do_table(self, input_path, expected):
        log.debug("Test CC1 & CC2, Table: {}".format(input_path))
        table = TableCC1CC2(input_path)
        table.print()
        result = table.find_cc1_cc2(table.find_cc4())
        log.debug("Result = {}".format(result))
        self.assertTupleEqual(expected, result)

    def test_cc1_cc2_1(self):
        input_path = './data/table_example1.csv'
        expected = (0,1),(1,1)
        self.do_table(input_path, expected)

    def test_cc1_cc2_2(self):
        """Lack of row header section on the LHS"""
        input_path = './data/table_example2.csv'
        expected = (0,0),(2,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_3(self):
        input_path = './data/table_example3.csv'
        expected = (1,0),(2,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_4(self):
        input_path = './data/table_example4.csv'
        expected = (0,0),(0,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_5(self):
        input_path = './data/table_example5.csv'
        expected = (0,0),(1,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_6(self):
        """Table is composed of two tables"""
        input_path = './data/table_example6.csv'
        expected = (1,0),(1,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_7(self):
        input_path = './data/table_example7.csv'
        expected = (1,0),(2,0)
        self.do_table(input_path, expected)

class TestCC3(unittest.TestCase):

    def do_table(self, input_path, expected):
        log.debug("Test CC3, Table: {}".format(input_path))
        table = TableCC3(input_path)
        result = table.label_sections()
        log.debug("Result = {}".format(result))
        table.print()
        self.assertTupleEqual(expected, result)

    def test_cc3_1(self):
        input_path = './data/table_example1.csv'
        expected = (2,2)
        self.do_table(input_path, expected)

    def test_cc3_2(self):
        """Lack of row header section on the LHS"""
        input_path = './data/table_example2.csv'
        expected = (3,1)
        self.do_table(input_path, expected)

    def test_cc3_3(self):
        input_path = './data/table_example3.csv'
        expected = (3,1)
        self.do_table(input_path, expected)

    def test_cc3_4(self):
        input_path = './data/table_example4.csv'
        expected = (1,1)
        self.do_table(input_path, expected)

    def test_cc3_5(self):
        input_path = './data/table_example5.csv'
        expected = (2,1)
        self.do_table(input_path, expected)

    def test_cc3_6(self):
        """Table is composed of two tables"""
        input_path = './data/table_example6.csv'
        expected = (2,1)
        self.do_table(input_path, expected)

    def test_cc3_7(self):
        input_path = './data/table_example7.csv'
        expected = (4,1)
        self.do_table(input_path, expected)


class TestTableLabels(unittest.TestCase):

    def do_table(self, input_path, expected):
        log.debug("Test complete table labelling: {}".format(input_path))
        table = Table(input_path)
        table.print()
        result = table.labels.tolist()
        self.assertListEqual(expected, result)

    def test_table_1(self):
        input_path = './data/table_example1.csv'
        expected = [['TableTitle', 'StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['Note', 'StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.do_table(input_path, expected)

    def test_table_2(self):
        """Lack of row header section on the LHS"""
        input_path = './data/table_example2.csv'
        expected = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'Note', 'Note', '/', '/', '/']]
        self.do_table(input_path, expected)

    def test_table_3(self):
        input_path = './data/table_example3.csv'
        expected = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.do_table(input_path, expected)

    def test_table_4(self):
        input_path = './data/table_example4.csv'
        expected = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.do_table(input_path, expected)

    def test_table_5(self):
        input_path = './data/table_example5.csv'
        expected = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.do_table(input_path, expected)

    def test_table_6(self):
        """Table is composed of two tables"""
        input_path = './data/table_example6.csv'
        expected = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['RowHeader', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data']]
        self.do_table(input_path, expected)

    def test_table_7(self):
        input_path = './data/table_example7.csv'
        expected = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader & FNref', 'ColHeader & FNref', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader & FNref', 'ColHeader & FNref'],
                    ['FNref', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/'],
                    ['RowHeader & FNref', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader & FNref', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['FNprefix & FNtext', 'Note', '/', '/', '/', '/', '/', '/', '/', '/', '/'],
                    ['FNprefix', 'FNtext', '/', '/', '/', '/', '/', '/', '/', '/', '/'],
                    ['Note', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/'],
                    ['FNprefix & FNtext', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/']]

        self.do_table(input_path, expected)


if __name__ == '__main__':
    unittest.main()


