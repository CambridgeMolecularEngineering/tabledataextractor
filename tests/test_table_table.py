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
from tabledataextractor.input import from_csv
from tabledataextractor.output.print import print_table

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
        input_path = './tests/data/table_example1.csv'
        expected = (6,7)
        self.do_table(input_path, expected)

    def test_cc4_2(self):
        """
        Here, the true result would actually be (4,5).
        However, in find_cc4() we choose the criterion that the data region starts, from below, when at least half of
        the row is non-empty.
        """
        input_path = './tests/data/table_example2.csv'
        expected = (3,5)
        self.do_table(input_path, expected)

    def test_cc4_3(self):
        input_path = './tests/data/table_example3.csv'
        expected = (7,10)
        self.do_table(input_path, expected)

    def test_cc4_4(self):
        input_path = './tests/data/table_example4.csv'
        expected = (2,5)
        self.do_table(input_path, expected)

    def test_cc4_5(self):
        input_path = './tests/data/table_example5.csv'
        expected = (3,5)
        self.do_table(input_path, expected)

    def test_cc4_6(self):
        input_path = './tests/data/table_example6.csv'
        expected = (11,3)
        self.do_table(input_path, expected)

    def test_cc4_7(self):
        input_path = './tests/data/table_example7.csv'
        expected = (8,10)
        self.do_table(input_path, expected)


class TableCC1CC2(Table):
    """Derivative of Table used to isolate testing for CC1 and CC2"""
    def __init__(self, *args):
        super().__init__(*args)

    def label_sections(self):
        """Label CC1 and CC2 and stop."""
        cc4 = self.find_cc4()
        cc1, cc2 = self.find_cc1_cc2(cc4, self.pre_cleaned_table)
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
        cc1, cc2 = self.find_cc1_cc2(cc4, self.pre_cleaned_table)
        cc3 = self.find_cc3(cc2)
        log.info("Table Cell CC3 = {}".format(cc3))
        self.labels[cc3] = 'CC3'
        return cc3


class TestCC1CC2(unittest.TestCase):

    def do_table(self, input_path, expected):
        log.debug("Test CC1 & CC2, Table: {}".format(input_path))
        table = TableCC1CC2(input_path)
        table.print()
        result = table.find_cc1_cc2(table.find_cc4(), table.pre_cleaned_table)
        log.debug("Result = {}".format(result))
        self.assertTupleEqual(expected, result)

    def test_cc1_cc2_1(self):
        input_path = './tests/data/table_example1.csv'
        expected = (0,1),(1,1)
        self.do_table(input_path, expected)

    def test_cc1_cc2_2(self):
        """Lack of row header section on the LHS"""
        input_path = './tests/data/table_example2.csv'
        expected = (0,0),(2,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_3(self):
        input_path = './tests/data/table_example3.csv'
        expected = (1,0),(2,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_4(self):
        input_path = './tests/data/table_example4.csv'
        expected = (0,0),(0,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_5(self):
        input_path = './tests/data/table_example5.csv'
        expected = (0,0),(1,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_6(self):
        """Table is composed of two tables"""
        input_path = './tests/data/table_example6.csv'
        expected = (1,0),(1,0)
        self.do_table(input_path, expected)

    def test_cc1_cc2_7(self):
        input_path = './tests/data/table_example7.csv'
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
        input_path = './tests/data/table_example1.csv'
        expected = (2,2)
        self.do_table(input_path, expected)

    def test_cc3_2(self):
        """Lack of row header section on the LHS"""
        input_path = './tests/data/table_example2.csv'
        expected = (3,1)
        self.do_table(input_path, expected)

    def test_cc3_3(self):
        input_path = './tests/data/table_example3.csv'
        expected = (3,1)
        self.do_table(input_path, expected)

    def test_cc3_4(self):
        input_path = './tests/data/table_example4.csv'
        expected = (1,1)
        self.do_table(input_path, expected)

    def test_cc3_5(self):
        input_path = './tests/data/table_example5.csv'
        expected = (2,1)
        self.do_table(input_path, expected)

    def test_cc3_6(self):
        """Table is composed of two tables"""
        input_path = './tests/data/table_example6.csv'
        expected = (2,1)
        self.do_table(input_path, expected)

    def test_cc3_7(self):
        input_path = './tests/data/table_example7.csv'
        expected = (4,1)
        self.do_table(input_path, expected)


class TestDuplicateLabelPrefixing(unittest.TestCase):

    def do_table(self, input_path, expected_path):
        log.debug("Test duplicate label prefixing: {}".format(input_path))
        table = Table(input_path)
        print_table(table.raw_table)
        print_table(table.pre_cleaned_table)
        result = table.pre_cleaned_table.tolist()
        expected = from_csv.read(expected_path).tolist()
        self.assertListEqual(expected, result)

    def test_table_8(self):
        """Prefixing in column header"""
        input_path = './tests/data/table_example8.csv'
        expected_path = './tests/data/table_example8b.csv'
        self.do_table(input_path, expected_path)

    def test_table_9(self):
        """Prefixing in row header"""
        input_path = './tests/data/table_example9.csv'
        expected_path = './tests/data/table_example9b.csv'
        self.do_table(input_path, expected_path)

    def test_table_10(self):
        """Prefixing will destroy the labelling"""
        input_path = './tests/data/table_example10.csv'
        expected_path = './tests/data/table_example10b.csv'
        self.do_table(input_path, expected_path)

    def test_table_11(self):
        """Prefixing is not performed, column header"""
        input_path = './tests/data/table_example11.csv'
        expected_path = './tests/data/table_example11b.csv'
        self.do_table(input_path, expected_path)

    def test_table_12(self):
        """Prefixing is not performed, row header"""
        input_path = './tests/data/table_example12.csv'
        expected_path = './tests/data/table_example12b.csv'
        self.do_table(input_path, expected_path)


class TestTableLabels(unittest.TestCase):

    def do_table(self, input_path, expected):
        log.debug("Test complete table labelling: {}".format(input_path))
        table = Table(input_path)
        print(repr(table))
        result = table.labels.tolist()
        self.assertListEqual(expected, result)

    def test_table_1(self):
        input_path = './tests/data/table_example1.csv'
        expected = [['TableTitle', 'StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['/',    'StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.do_table(input_path, expected)

    def test_table_2(self):
        """Lack of row header section on the LHS"""
        input_path = './tests/data/table_example2.csv'
        expected = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'Note', 'Note', '/', '/', '/']]
        self.do_table(input_path, expected)

    def test_table_3(self):
        input_path = './tests/data/table_example3.csv'
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
        input_path = './tests/data/table_example4.csv'
        expected = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.do_table(input_path, expected)

    def test_table_5(self):
        input_path = './tests/data/table_example5.csv'
        expected = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.do_table(input_path, expected)

    def test_table_6(self):
        """Table is composed of two tables"""
        input_path = './tests/data/table_example6.csv'
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
        input_path = './tests/data/table_example7.csv'
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


class TestCategorizationTable(unittest.TestCase):

    def do_table(self, input_path, expected):
        log.debug("Test Categorization Table: {}".format(input_path))
        table = Table(input_path)
        print(repr(table))
        result = table.category_table
        self.assertListEqual(expected, result)

    def test_table_1(self):
        input_path = './tests/data/table_example1.csv'
        expected = [['4.64', ['This study'], ['Rutile', 'a = b (A)']], ['2.99', ['This study'], ['Rutile', 'c (A)']], ['0.305', ['This study'], ['Rutile', 'u']], ['3.83', ['This study'], ['Anatase', 'a = b (A)']], ['9.62', ['This study'], ['Anatase', 'c (A)']], ['0.208', ['This study'], ['Anatase', 'u']], ['4.67', ['GGA [25]'], ['Rutile', 'a = b (A)']], ['2.97', ['GGA [25]'], ['Rutile', 'c (A)']], ['0.305', ['GGA [25]'], ['Rutile', 'u']], ['3.80', ['GGA [25]'], ['Anatase', 'a = b (A)']], ['9.67', ['GGA [25]'], ['Anatase', 'c (A)']], ['0.207', ['GGA [25]'], ['Anatase', 'u']], ['4.63', ['GGA [26]'], ['Rutile', 'a = b (A)']], ['2.98', ['GGA [26]'], ['Rutile', 'c (A)']], ['0.305', ['GGA [26]'], ['Rutile', 'u']], ['""', ['GGA [26]'], ['Anatase', 'a = b (A)']], ['""', ['GGA [26]'], ['Anatase', 'c (A)']], ['""', ['GGA [26]'], ['Anatase', 'u']], ['""', ['HF [27]'], ['Rutile', 'a = b (A)']], ['""', ['HF [27]'], ['Rutile', 'c (A)']], ['""', ['HF [27]'], ['Rutile', 'u']], ['3.76', ['HF [27]'], ['Anatase', 'a = b (A)']], ['9.85', ['HF [27]'], ['Anatase', 'c (A)']], ['0.202', ['HF [27]'], ['Anatase', 'u']], ['4.594', ['Expt. [23]'], ['Rutile', 'a = b (A)']], ['2.958', ['Expt. [23]'], ['Rutile', 'c (A)']], ['0.305', ['Expt. [23]'], ['Rutile', 'u']], ['3.785', ['Expt. [23]'], ['Anatase', 'a = b (A)']], ['9.514', ['Expt. [23]'], ['Anatase', 'c (A)']], ['0.207', ['Expt. [23]'], ['Anatase', 'u']]]
        self.do_table(input_path, expected)

    def test_table_2(self):
        """Table without a row header."""
        input_path = './tests/data/table_example2.csv'
        expected = [['2.990', ['4.640'], ['2006', 'Government transfers', 'Implicit transfer rates1 %']], ['0.305', ['4.640'], ['2006', 'Government transfers', 'Shares %']], ['3.830', ['4.640'], ['2007', 'Government transfers', 'Average $ constant 2007']], ['9.620', ['4.640'], ['2007', 'Government transfers', 'Implicit transfer rates1 %']], ['0.208', ['4.640'], ['2007', 'Government transfers', 'Shares %']]]
        self.do_table(input_path, expected)

    def test_table_3(self):
        input_path = './tests/data/table_example3.csv'
        expected = [['3735', ['Norway'], ['Million dollar', '2007']], ['4006', ['Norway'], ['Million dollar', '2008']], ['4081', ['Norway'], ['Million dollar', '2009']], ['4580', ['Norway'], ['Million dollar', '2010*']], ['4936', ['Norway'], ['Million dollar', '2011*']], ['0.95', ['Norway'], ['Percentage of GNI', '2007']], ['0.89', ['Norway'], ['Percentage of GNI', '2008']], ['1.06', ['Norway'], ['Percentage of GNI', '2009']], ['1.1', ['Norway'], ['Percentage of GNI', '2010*']], ['1', ['Norway'], ['Percentage of GNI', '2011*']], ['2562', ['Denmark'], ['Million dollar', '2007']], ['2803', ['Denmark'], ['Million dollar', '2008']], ['2810', ['Denmark'], ['Million dollar', '2009']], ['2871', ['Denmark'], ['Million dollar', '2010*']], ['2981', ['Denmark'], ['Million dollar', '2011*']], ['0.81', ['Denmark'], ['Percentage of GNI', '2007']], ['0.82', ['Denmark'], ['Percentage of GNI', '2008']], ['0.88', ['Denmark'], ['Percentage of GNI', '2009']], ['0.91', ['Denmark'], ['Percentage of GNI', '2010*']], ['0.86', ['Denmark'], ['Percentage of GNI', '2011*']], ['2669', ['Australia'], ['Million dollar', '2007']], ['2954', ['Australia'], ['Million dollar', '2008']], ['2762', ['Australia'], ['Million dollar', '2009']], ['3826', ['Australia'], ['Million dollar', '2010*']], ['4799', ['Australia'], ['Million dollar', '2011*']], ['0.32', ['Australia'], ['Percentage of GNI', '2007']], ['0.32', ['Australia'], ['Percentage of GNI', '2008']], ['0.29', ['Australia'], ['Percentage of GNI', '2009']], ['0.32', ['Australia'], ['Percentage of GNI', '2010*']], ['0.35', ['Australia'], ['Percentage of GNI', '2011*']], ['320', ['New Zealand'], ['Million dollar', '2007']], ['348', ['New Zealand'], ['Million dollar', '2008']], ['309', ['New Zealand'], ['Million dollar', '2009']], ['342', ['New Zealand'], ['Million dollar', '2010*']], ['429', ['New Zealand'], ['Million dollar', '2011*']], ['0.27', ['New Zealand'], ['Percentage of GNI', '2007']], ['0.3', ['New Zealand'], ['Percentage of GNI', '2008']], ['0.28', ['New Zealand'], ['Percentage of GNI', '2009']], ['0.26', ['New Zealand'], ['Percentage of GNI', '2010*']], ['0.28', ['New Zealand'], ['Percentage of GNI', '2011*']], ['104206', ['OECD/DAC1'], ['Million dollar', '2007']], ['121954', ['OECD/DAC1'], ['Million dollar', '2008']], ['119778', ['OECD/DAC1'], ['Million dollar', '2009']], ['128465', ['OECD/DAC1'], ['Million dollar', '2010*']], ['133526', ['OECD/DAC1'], ['Million dollar', '2011*']], ['0.27', ['OECD/DAC1'], ['Percentage of GNI', '2007']], ['0.3', ['OECD/DAC1'], ['Percentage of GNI', '2008']], ['0.31', ['OECD/DAC1'], ['Percentage of GNI', '2009']], ['0.32', ['OECD/DAC1'], ['Percentage of GNI', '2010*']], ['0.31', ['OECD/DAC1'], ['Percentage of GNI', '2011*']]]
        self.do_table(input_path, expected)

    def test_table_4(self):
        input_path = './tests/data/table_example4.csv'
        expected = [['1647218', ['2003'], ['Short messages/thousands']], ['24.3', ['2003'], ['A Change %']], ['347', ['2003'], [' Short messages/subscription']], ['2314', ['2003'], ['Multimedia messages/thousands']], ['', ['2003'], ['B Change %']], ['2193498', ['2004'], ['Short messages/thousands']], ['33.2', ['2004'], ['A Change %']], ['439', ['2004'], [' Short messages/subscription']], ['7386', ['2004'], ['Multimedia messages/thousands']], ['219.2', ['2004'], ['B Change %']]]
        self.do_table(input_path, expected)

    def test_table_5(self):
        input_path = './tests/data/table_example5.csv'
        expected = [['1647218', ['2003'], ['', 'Short messages/thousands']], ['24.3', ['2003'], ['Short messages/thousands', 'Change %']], ['347', ['2003'], ['', ' Short messages/subscription']], ['2314', ['2003'], ['', 'Multimedia messages/thousands']], ['', ['2003'], ['Multimedia messages/thousands', 'Change %']], ['2193498', ['2004'], ['', 'Short messages/thousands']], ['33.2', ['2004'], ['Short messages/thousands', 'Change %']], ['439', ['2004'], ['', ' Short messages/subscription']], ['7386', ['2004'], ['', 'Multimedia messages/thousands']], ['219.2', ['2004'], ['Multimedia messages/thousands', 'Change %']]]
        self.do_table(input_path, expected)

    def test_table_7(self):
        input_path = './tests/data/table_example7.csv'
        expected = [['3735', ['Norwaya)'], ['Million dollar', '2007']], ['4081', ['Norwaya)'], ['Million dollar', '2009']], ['4006', ['Norwaya)'], ['Million dollar', '2008']], ['4580', ['Norwaya)'], ['Million dollar', '2010*']], ['4936', ['Norwaya)'], ['Million dollar', '2011*']], ['0.95', ['Norwaya)'], ['Percentage of GNI', '2007']], ['0.89', ['Norwaya)'], ['Percentage of GNI', '2008']], ['1.06', ['Norwaya)'], ['Percentage of GNI', '2009']], ['1.1', ['Norwaya)'], ['Percentage of GNI', '2010*']], ['1', ['Norwaya)'], ['Percentage of GNI', '2011*']], ['2562', ['Denmark'], ['Million dollar', '2007']], ['2810', ['Denmark'], ['Million dollar', '2009']], ['2803', ['Denmark'], ['Million dollar', '2008']], ['2871', ['Denmark'], ['Million dollar', '2010*']], ['2981', ['Denmark'], ['Million dollar', '2011*']], ['0.81', ['Denmark'], ['Percentage of GNI', '2007']], ['0.82', ['Denmark'], ['Percentage of GNI', '2008']], ['0.88', ['Denmark'], ['Percentage of GNI', '2009']], ['0.91', ['Denmark'], ['Percentage of GNI', '2010*']], ['0.86', ['Denmark'], ['Percentage of GNI', '2011*']], ['2669', ['Australia'], ['Million dollar', '2007']], ['2762', ['Australia'], ['Million dollar', '2009']], ['2954', ['Australia'], ['Million dollar', '2008']], ['3826', ['Australia'], ['Million dollar', '2010*']], ['4799', ['Australia'], ['Million dollar', '2011*']], ['0.32', ['Australia'], ['Percentage of GNI', '2007']], ['0.32', ['Australia'], ['Percentage of GNI', '2008']], ['0.29', ['Australia'], ['Percentage of GNI', '2009']], ['0.32', ['Australia'], ['Percentage of GNI', '2010*']], ['0.35', ['Australia'], ['Percentage of GNI', '2011*']], ['320', ['New Zealand'], ['Million dollar', '2007']], ['309', ['New Zealand'], ['Million dollar', '2009']], ['348', ['New Zealand'], ['Million dollar', '2008']], ['342', ['New Zealand'], ['Million dollar', '2010*']], ['429', ['New Zealand'], ['Million dollar', '2011*']], ['0.27', ['New Zealand'], ['Percentage of GNI', '2007']], ['0.3', ['New Zealand'], ['Percentage of GNI', '2008']], ['0.28', ['New Zealand'], ['Percentage of GNI', '2009']], ['0.26', ['New Zealand'], ['Percentage of GNI', '2010*']], ['0.28', ['New Zealand'], ['Percentage of GNI', '2011*']], ['104206', ['OECD/DAC 1'], ['Million dollar', '2007']], ['119778', ['OECD/DAC 1'], ['Million dollar', '2009']], ['121954', ['OECD/DAC 1'], ['Million dollar', '2008']], ['128465', ['OECD/DAC 1'], ['Million dollar', '2010*']], ['133526', ['OECD/DAC 1'], ['Million dollar', '2011*']], ['0.27', ['OECD/DAC 1'], ['Percentage of GNI', '2007']], ['0.3', ['OECD/DAC 1'], ['Percentage of GNI', '2008']], ['0.31', ['OECD/DAC 1'], ['Percentage of GNI', '2009']], ['0.32', ['OECD/DAC 1'], ['Percentage of GNI', '2010*']], ['0.31', ['OECD/DAC 1'], ['Percentage of GNI', '2011*']]]
        self.do_table(input_path, expected)

    def test_table_8(self):
        input_path = './tests/data/table_example8.csv'
        expected = [['1647218', ['2003'], ['', 'Short messages/thousands']], ['24.3', ['2003'], ['Short messages/thousands', 'Change %']], ['347', ['2003'], ['', 'Short messages/subscription']], ['2314', ['2003'], ['', 'Multimedia messages/thousands']], ['', ['2003'], ['Multimedia messages/thousands', 'Change %']], ['2193498', ['2004'], ['', 'Short messages/thousands']], ['33.2', ['2004'], ['Short messages/thousands', 'Change %']], ['439', ['2004'], ['', 'Short messages/subscription']], ['7386', ['2004'], ['', 'Multimedia messages/thousands']], ['219.2', ['2004'], ['Multimedia messages/thousands', 'Change %']]]
        self.do_table(input_path, expected)

    def test_table_9(self):
        input_path = './tests/data/table_example9.csv'
        expected = [['1647218', ['', 'Short messages/thousands'], ['2003']], ['2193498', ['', 'Short messages/thousands'], ['2004']], ['24.3', ['Short messages/thousands', 'Change %'], ['2003']], ['33.2', ['Short messages/thousands', 'Change %'], ['2004']], ['347', ['', 'Short messages/subscription'], ['2003']], ['439', ['', 'Short messages/subscription'], ['2004']], ['2314', ['', 'Multimedia messages/thousands'], ['2003']], ['7386', ['', 'Multimedia messages/thousands'], ['2004']], ['', ['Multimedia messages/thousands', 'Change %'], ['2003']], ['219.2', ['Multimedia messages/thousands', 'Change %'], ['2004']]]
        self.do_table(input_path, expected)

    def test_table_10(self):
        """Table where prefixing destroys the layout"""
        input_path = './tests/data/table_example10.csv'
        expected = [['', [''], ['', 'Short messages/thousands']], ['A', [''], ['Short messages/thousands', 'Change %']], ['', [''], ['', ' Short messages/subscription']], ['', [''], ['', 'Multimedia messages/thousands']], ['B', [''], ['Multimedia messages/thousands', 'Change %']], ['1647218', ['2003'], ['', 'Short messages/thousands']], ['24.3', ['2003'], ['Short messages/thousands', 'Change %']], ['347', ['2003'], ['', ' Short messages/subscription']], ['2314', ['2003'], ['', 'Multimedia messages/thousands']], ['', ['2003'], ['Multimedia messages/thousands', 'Change %']], ['2193498', ['2004'], ['', 'Short messages/thousands']], ['33.2', ['2004'], ['Short messages/thousands', 'Change %']], ['439', ['2004'], ['', ' Short messages/subscription']], ['7386', ['2004'], ['', 'Multimedia messages/thousands']], ['219.2', ['2004'], ['Multimedia messages/thousands', 'Change %']]]
        self.do_table(input_path, expected)

    def test_table_11(self):
        input_path = './tests/data/table_example11b.csv'
        expected = [['1647218', ['2003'], ['', 'Short messages/thousands']], ['24.3', ['2003'], ['Category A', 'Change %']], ['347', ['2003'], ['', ' Short messages/subscription']], ['2314', ['2003'], ['', 'Multimedia messages/thousands']], ['', ['2003'], ['Category B', 'Change %']], ['2193498', ['2004'], ['', 'Short messages/thousands']], ['33.2', ['2004'], ['Category A', 'Change %']], ['439', ['2004'], ['', ' Short messages/subscription']], ['7386', ['2004'], ['', 'Multimedia messages/thousands']], ['219.2', ['2004'], ['Category B', 'Change %']]]
        self.do_table(input_path, expected)

    def test_table_12(self):
        input_path = './tests/data/table_example12.csv'
        expected = [['1647218', ['', 'Short messages/thousands'], ['2003']], ['2193498', ['', 'Short messages/thousands'], ['2004']], ['24.3', ['Category A', 'Change %'], ['2003']], ['33.2', ['Category A', 'Change %'], ['2004']], ['347', ['', 'Short messages/subscription'], ['2003']], ['439', ['', 'Short messages/subscription'], ['2004']], ['2314', ['', 'Multimedia messages/thousands'], ['2003']], ['7386', ['', 'Multimedia messages/thousands'], ['2004']], ['', ['Category B', 'Change %'], ['2003']], ['219.2', ['Category B', 'Change %'], ['2004']]]
        self.do_table(input_path, expected)

    def test_table_13(self):
        """Coordination numbers"""
        input_path = './tests/data/table_example13.csv'
        expected = [['1.82 ± 0.3', ['NAsAs'], ['As40Te60']], ['1.07 ± 0.3', ['NAsAs'], ['As30Cu10Te60']], ['1.13 ± 0.3', ['NAsAs'], ['As20Cu20Te60']], ['1.18 ± 0.3', ['NAsAs'], ['As15Cu25Te60']], ['0.79 ± 0.3', ['NAsAs'], ['As10Cu30Te60']], ['-', ['NAsCu'], ['As40Te60']], ['0.37 ± 0.2', ['NAsCu'], ['As30Cu10Te60']], ['0.71 ± 0.25', ['NAsCu'], ['As20Cu20Te60']], ['0.85 ± 0.25', ['NAsCu'], ['As15Cu25Te60']], ['0.51 ± 0.3', ['NAsCu'], ['As10Cu30Te60']], ['1.34 ± 0.3', ['NAsTe'], ['As40Te60']], ['1.58 ± 0.3', ['NAsTe'], ['As30Cu10Te60']], ['1.80 ± 0.3', ['NAsTe'], ['As20Cu20Te60']], ['1.94 ± 0.4', ['NAsTe'], ['As15Cu25Te60']], ['2.76 ± 0.6', ['NAsTe'], ['As10Cu30Te60']], ['-', ['NCuAs'], ['As40Te60']], ['1.11 ± 0.6', ['NCuAs'], ['As30Cu10Te60']], ['0.71 ± 0.25', ['NCuAs'], ['As20Cu20Te60']], ['0.51 ± 0.15', ['NCuAs'], ['As15Cu25Te60']], ['0.17 ± 0.1', ['NCuAs'], ['As10Cu30Te60']], ['-', ['NCuCu'], ['As40Te60']], ['1.07 ± 0.6', ['NCuCu'], ['As30Cu10Te60']], ['1.69 ± 0.5', ['NCuCu'], ['As20Cu20Te60']], ['1.83 ± 0.5', ['NCuCu'], ['As15Cu25Te60']], ['3.11 ± 0.7', ['NCuCu'], ['As10Cu30Te60']], ['-', ['NCuTe'], ['As40Te60']], ['2.32 ± 0.6', ['NCuTe'], ['As30Cu10Te60']], ['2.01 ± 0.6', ['NCuTe'], ['As20Cu20Te60']], ['2.46 ± 0.6', ['NCuTe'], ['As15Cu25Te60']], ['2.17 ± 0.5', ['NCuTe'], ['As10Cu30Te60']], ['0.89', ['NTeAs'], ['As40Te60']], ['0.79 ± 0.25', ['NTeAs'], ['As30Cu10Te60']], ['0.60 ± 0.2', ['NTeAs'], ['As20Cu20Te60']], ['0.49 ± 0.2', ['NTeAs'], ['As15Cu25Te60']], ['0.46 ± 0.1', ['NTeAs'], ['As10Cu30Te60']], ['-', ['NTeCu'], ['As40Te60']], ['0.39 ± 0.2', ['NTeCu'], ['As30Cu10Te60']], ['0.67 ± 0.2', ['NTeCu'], ['As20Cu20Te60']], ['1.03 ± 0.25', ['NTeCu'], ['As15Cu25Te60']], ['1.08 ± 0.25', ['NTeCu'], ['As10Cu30Te60']], ['1.01', ['NTeTe'], ['As40Te60']], ['1.14 ± 0.2', ['NTeTe'], ['As30Cu10Te60']], ['1.43 ± 0.2', ['NTeTe'], ['As20Cu20Te60']], ['1.44 ± 0.2', ['NTeTe'], ['As15Cu25Te60']], ['1.65 ± 0.2', ['NTeTe'], ['As10Cu30Te60']], ['3.16 ± 0.3', ['NAsAs + NAsTe'], ['As40Te60']], ['2.65 ± 0.3', ['NAsAs + NAsTe'], ['As30Cu10Te60']], ['2.93 ± 0.3', ['NAsAs + NAsTe'], ['As20Cu20Te60']], ['3.12 ± 0.3', ['NAsAs + NAsTe'], ['As15Cu25Te60']], ['3.55 ± 0.6', ['NAsAs + NAsTe'], ['As10Cu30Te60']], ['1.90 ± 0.2', ['NTeAs + NTeTe'], ['As40Te60']], ['1.93 ± 0.2', ['NTeAs + NTeTe'], ['As30Cu10Te60']], ['2.03 ± 0.2', ['NTeAs + NTeTe'], ['As20Cu20Te60']], ['1.93 ± 0.2', ['NTeAs + NTeTe'], ['As15Cu25Te60']], ['2.11 ± 0.2', ['NTeAs + NTeTe'], ['As10Cu30Te60']], ['3.16 ± 0.3', ['NAs'], ['As40Te60']], ['3.02 ± 0.3', ['NAs'], ['As30Cu10Te60']], ['3.64 ± 0.3', ['NAs'], ['As20Cu20Te60']], ['3.97 ± 0.3', ['NAs'], ['As15Cu25Te60']], ['4.06 ± 0.6', ['NAs'], ['As10Cu30Te60']], ['-', ['NCu'], ['As40Te60']], ['4.50 ± 1.0', ['NCu'], ['As30Cu10Te60']], ['4.41 + 0.5', ['NCu'], ['As20Cu20Te60']], ['4.80 ± 0.5', ['NCu'], ['As15Cu25Te60']], ['5.45 ± 0.6', ['NCu'], ['As10Cu30Te60']], ['1.90 ± 0.2', ['NTe'], ['As40Te60']], ['2.32 ± 0.2', ['NTe'], ['As30Cu10Te60']], ['2.70 ± 0.2', ['NTe'], ['As20Cu20Te60']], ['2.96 ± 0.2', ['NTe'], ['As15Cu25Te60']], ['3.19 ± 0.3', ['NTe'], ['As10Cu30Te60']]]
        self.do_table(input_path, expected)


class TestSingleRowColumnTable(unittest.TestCase):

    def do_table(self, input_path, expected, expected_t, expected_cat, expected_cat_t):
        log.debug("Test single column/row table: {}".format(input_path))

        # Table labels
        table = Table(input_path)
        print(repr(table))
        result = table.labels.tolist()
        self.assertListEqual(expected, result)

        # Category table
        result = table.category_table
        self.assertListEqual(expected_cat, result)

        # Inverted table labels
        table.transpose()
        print(repr(table))
        result = table.labels.tolist()
        self.assertListEqual(expected_t, result)

        # Inverted category table
        result = table.category_table
        self.assertListEqual(expected_cat_t, result)

    def test_table_1(self):
        input_path = './tests/data/te_01.csv'
        expected = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_t = [['StubHeader', 'ColHeader'],
                      ['RowHeader', 'Data'],
                      ['RowHeader', 'Data'],
                      ['RowHeader', 'Data'],
                      ['RowHeader', 'Data'],
                      ['RowHeader', 'Data'],
                      ['RowHeader', 'Data']]
        expected_cat = [['"4.64"', ['"This study"'], ['"A"']], ['"2.99"', ['"This study"'], ['"B"']], ['"0.305"', ['"This study"'], ['"C"']], ['"3.83"', ['"This study"'], ['"D"']], ['"9.62"', ['"This study"'], ['"E"']], ['"0.208"', ['"This study"'], ['"F"']]]
        expected_cat_t = [['"4.64"', ['"A"'], ['"This study"']], ['"2.99"', ['"B"'], ['"This study"']], ['"0.305"', ['"C"'], ['"This study"']], ['"3.83"', ['"D"'], ['"This study"']], ['"9.62"', ['"E"'], ['"This study"']], ['"0.208"', ['"F"'], ['"This study"']]]
        self.do_table(input_path, expected, expected_t, expected_cat, expected_cat_t)

    def test_table_2(self):
        input_path = './tests/data/te_02.csv'
        expected = [['StubHeader', 'ColHeader'],
                    ['RowHeader', 'Data'],
                    ['RowHeader', 'Data'],
                    ['RowHeader', 'Data'],
                    ['RowHeader', 'Data'],
                    ['RowHeader', 'Data'],
                    ['RowHeader', 'Data']]
        expected_t = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                      ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_cat = [['"4.64"', ['"A"'], ['"This study"']], ['"2.99"', ['"B"'], ['"This study"']], ['"0.305"', ['"C"'], ['"This study"']], ['"3.83"', ['"D"'], ['"This study"']], ['"9.62"', ['"E"'], ['"This study"']], ['"0.208"', ['"F"'], ['"This study"']]]
        expected_cat_t = [['"4.64"', ['"This study"'], ['"A"']], ['"2.99"', ['"This study"'], ['"B"']], ['"0.305"', ['"This study"'], ['"C"']], ['"3.83"', ['"This study"'], ['"D"']], ['"9.62"', ['"This study"'], ['"E"']], ['"0.208"', ['"This study"'], ['"F"']]]
        self.do_table(input_path, expected, expected_t, expected_cat, expected_cat_t)

    def test_table_3(self):
        input_path = './tests/data/te_03.csv'
        expected = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'],
                    ['/', 'StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                    ['/', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'],
                    ['Note', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_t = [['TableTitle', 'StubHeader', 'ColHeader', 'ColHeader'],
                      ['Note', 'RowHeader', 'Data', 'Data'],
                      ['Note', 'RowHeader', 'Data', 'Data'],
                      ['Note', 'RowHeader', 'Data', 'Data'],
                      ['Note', 'RowHeader', 'Data', 'Data'],
                      ['Note', 'RowHeader', 'Data', 'Data'],
                      ['Note', 'RowHeader', 'Data', 'Data']]
        expected_cat = [['"B"', ['"A"'], ['"Test3"']], ['"C"', ['"A"'], ['"Test4"']], ['"D"', ['"A"'], ['"Test5"']], ['"E"', ['"A"'], ['"Test6"']], ['"F"', ['"A"'], ['"Test7"']], ['"2.99"', ['"4.64"'], ['"Test3"']], ['"0.305"', ['"4.64"'], ['"Test4"']], ['"3.83"', ['"4.64"'], ['"Test5"']], ['"9.62"', ['"4.64"'], ['"Test6"']], ['"0.208"', ['"4.64"'], ['"Test7"']]]
        expected_cat_t = [['"A"', ['"Test2"'], ['""']], ['"4.64"', ['"Test2"'], ['"This study"']], ['"B"', ['"Test3"'], ['""']], ['"2.99"', ['"Test3"'], ['"This study"']], ['"C"', ['"Test4"'], ['""']], ['"0.305"', ['"Test4"'], ['"This study"']], ['"D"', ['"Test5"'], ['""']], ['"3.83"', ['"Test5"'], ['"This study"']], ['"E"', ['"Test6"'], ['""']], ['"9.62"', ['"Test6"'], ['"This study"']], ['"F"', ['"Test7"'], ['""']], ['"0.208"', ['"Test7"'], ['"This study"']]]
        self.do_table(input_path, expected, expected_t, expected_cat, expected_cat_t)


if __name__ == '__main__':
    unittest.main()


