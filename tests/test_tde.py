# -*- coding: utf-8 -*-
"""
Tests full tables - default config - only correct outcomes

.. codeauthor:: Juraj Mavračić (jm2111@cam.ac.uk)

"""

import unittest
import logging
from tabledataextractor import Table

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class TestTDE(unittest.TestCase):

    def do_table(self, input_path, expected_labels, expected_category_table):
        log.debug("Test TDE, Table: {}".format(input_path))
        table = Table(input_path)
        table.print()
        labels = table.labels.tolist()
        category_table = table.category_table
        self.assertListEqual(expected_labels, labels)
        self.assertListEqual(expected_category_table, category_table)

    def do_subtable(self, input_path, subtable_number, expected_labels, expected_category_table):
        log.debug("Test TDE, SubTable: {}".format(input_path))
        table = Table(input_path)
        table.subtables[subtable_number].print_raw_table()
        labels = table.subtables[subtable_number].labels.tolist()
        category_table = table.subtables[subtable_number].category_table
        self.assertListEqual(expected_labels, labels)
        self.assertListEqual(expected_category_table, category_table)

    def test_01(self):
        input_path = './tests/data/table_example1.csv'
        expected_labels = [['StubHeader', 'StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['4.64', ['Computational', 'This study'], ['Rutile', 'a = b (A)']], ['2.99', ['Computational', 'This study'], ['Rutile', 'c (A)']], ['0.305', ['Computational', 'This study'], ['Rutile', 'u']], ['3.83', ['Computational', 'This study'], ['Anatase', 'a = b (A)']], ['9.62', ['Computational', 'This study'], ['Anatase', 'c (A)']], ['0.208', ['Computational', 'This study'], ['Anatase', 'u']], ['4.67', ['Computational', 'GGA [25]'], ['Rutile', 'a = b (A)']], ['2.97', ['Computational', 'GGA [25]'], ['Rutile', 'c (A)']], ['0.305', ['Computational', 'GGA [25]'], ['Rutile', 'u']], ['3.80', ['Computational', 'GGA [25]'], ['Anatase', 'a = b (A)']], ['9.67', ['Computational', 'GGA [25]'], ['Anatase', 'c (A)']], ['0.207', ['Computational', 'GGA [25]'], ['Anatase', 'u']], ['4.63', ['Computational', 'GGA [26]'], ['Rutile', 'a = b (A)']], ['2.98', ['Computational', 'GGA [26]'], ['Rutile', 'c (A)']], ['0.305', ['Computational', 'GGA [26]'], ['Rutile', 'u']], ['NoValue', ['Computational', 'GGA [26]'], ['Anatase', 'a = b (A)']], ['NoValue', ['Computational', 'GGA [26]'], ['Anatase', 'c (A)']], ['NoValue', ['Computational', 'GGA [26]'], ['Anatase', 'u']], ['NoValue', ['Computational', 'HF [27]'], ['Rutile', 'a = b (A)']], ['NoValue', ['Computational', 'HF [27]'], ['Rutile', 'c (A)']], ['NoValue', ['Computational', 'HF [27]'], ['Rutile', 'u']], ['3.76', ['Computational', 'HF [27]'], ['Anatase', 'a = b (A)']], ['9.85', ['Computational', 'HF [27]'], ['Anatase', 'c (A)']], ['0.202', ['Computational', 'HF [27]'], ['Anatase', 'u']], ['4.594', ['Experimental', 'Expt. [23]'], ['Rutile', 'a = b (A)']], ['2.958', ['Experimental', 'Expt. [23]'], ['Rutile', 'c (A)']], ['0.305', ['Experimental', 'Expt. [23]'], ['Rutile', 'u']], ['3.785', ['Experimental', 'Expt. [23]'], ['Anatase', 'a = b (A)']], ['9.514', ['Experimental', 'Expt. [23]'], ['Anatase', 'c (A)']], ['0.207', ['Experimental', 'Expt. [23]'], ['Anatase', 'u']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_02(self):
        input_path = './tests/data/table_example10.csv'
        expected_labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['1647218', ['2003'], ['Short messages/thousands', 'Short messages/thousands']], ['24.3', ['2003'], ['Change %', 'A']], ['347', ['2003'], [' Short messages/subscription', ' Short messages/subscription']], ['2314', ['2003'], ['Multimedia messages/thousands', 'Multimedia messages/thousands']], ['NoValue', ['2003'], ['Change %', 'B']], ['2193498', ['2004'], ['Short messages/thousands', 'Short messages/thousands']], ['33.2', ['2004'], ['Change %', 'A']], ['439', ['2004'], [' Short messages/subscription', ' Short messages/subscription']], ['7386', ['2004'], ['Multimedia messages/thousands', 'Multimedia messages/thousands']], ['219.2', ['2004'], ['Change %', 'B']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_03(self):
        input_path = './tests/data/table_example13.csv'
        expected_labels = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['1.82 ± 0.3', ['NAsAs'], ['As40Te60']],
                                   ['1.07 ± 0.3', ['NAsAs'], ['As30Cu10Te60']],
                                   ['1.13 ± 0.3', ['NAsAs'], ['As20Cu20Te60']],
                                   ['1.18 ± 0.3', ['NAsAs'], ['As15Cu25Te60']],
                                   ['0.79 ± 0.3', ['NAsAs'], ['As10Cu30Te60']],
                                   ['NoValue', ['NAsCu'], ['As40Te60']],
                                   ['0.37 ± 0.2', ['NAsCu'], ['As30Cu10Te60']],
                                   ['0.71 ± 0.25', ['NAsCu'], ['As20Cu20Te60']],
                                   ['0.85 ± 0.25', ['NAsCu'], ['As15Cu25Te60']],
                                   ['0.51 ± 0.3', ['NAsCu'], ['As10Cu30Te60']],
                                   ['1.34 ± 0.3', ['NAsTe'], ['As40Te60']],
                                   ['1.58 ± 0.3', ['NAsTe'], ['As30Cu10Te60']],
                                   ['1.80 ± 0.3', ['NAsTe'], ['As20Cu20Te60']],
                                   ['1.94 ± 0.4', ['NAsTe'], ['As15Cu25Te60']],
                                   ['2.76 ± 0.6', ['NAsTe'], ['As10Cu30Te60']],
                                   ['NoValue', ['NCuAs'], ['As40Te60']],
                                   ['1.11 ± 0.6', ['NCuAs'], ['As30Cu10Te60']],
                                   ['0.71 ± 0.25', ['NCuAs'], ['As20Cu20Te60']],
                                   ['0.51 ± 0.15', ['NCuAs'], ['As15Cu25Te60']],
                                   ['0.17 ± 0.1', ['NCuAs'], ['As10Cu30Te60']],
                                   ['NoValue', ['NCuCu'], ['As40Te60']],
                                   ['1.07 ± 0.6', ['NCuCu'], ['As30Cu10Te60']],
                                   ['1.69 ± 0.5', ['NCuCu'], ['As20Cu20Te60']],
                                   ['1.83 ± 0.5', ['NCuCu'], ['As15Cu25Te60']],
                                   ['3.11 ± 0.7', ['NCuCu'], ['As10Cu30Te60']],
                                   ['NoValue', ['NCuTe'], ['As40Te60']],
                                   ['2.32 ± 0.6', ['NCuTe'], ['As30Cu10Te60']],
                                   ['2.01 ± 0.6', ['NCuTe'], ['As20Cu20Te60']],
                                   ['2.46 ± 0.6', ['NCuTe'], ['As15Cu25Te60']],
                                   ['2.17 ± 0.5', ['NCuTe'], ['As10Cu30Te60']],
                                   ['0.89', ['NTeAs'], ['As40Te60']],
                                   ['0.79 ± 0.25', ['NTeAs'], ['As30Cu10Te60']],
                                   ['0.60 ± 0.2', ['NTeAs'], ['As20Cu20Te60']],
                                   ['0.49 ± 0.2', ['NTeAs'], ['As15Cu25Te60']],
                                   ['0.46 ± 0.1', ['NTeAs'], ['As10Cu30Te60']],
                                   ['NoValue', ['NTeCu'], ['As40Te60']],
                                   ['0.39 ± 0.2', ['NTeCu'], ['As30Cu10Te60']],
                                   ['0.67 ± 0.2', ['NTeCu'], ['As20Cu20Te60']],
                                   ['1.03 ± 0.25', ['NTeCu'], ['As15Cu25Te60']],
                                   ['1.08 ± 0.25', ['NTeCu'], ['As10Cu30Te60']],
                                   ['1.01', ['NTeTe'], ['As40Te60']],
                                   ['1.14 ± 0.2', ['NTeTe'], ['As30Cu10Te60']],
                                   ['1.43 ± 0.2', ['NTeTe'], ['As20Cu20Te60']],
                                   ['1.44 ± 0.2', ['NTeTe'], ['As15Cu25Te60']],
                                   ['1.65 ± 0.2', ['NTeTe'], ['As10Cu30Te60']],
                                   ['3.16 ± 0.3', ['NAsAs + NAsTe'], ['As40Te60']],
                                   ['2.65 ± 0.3', ['NAsAs + NAsTe'], ['As30Cu10Te60']],
                                   ['2.93 ± 0.3', ['NAsAs + NAsTe'], ['As20Cu20Te60']],
                                   ['3.12 ± 0.3', ['NAsAs + NAsTe'], ['As15Cu25Te60']],
                                   ['3.55 ± 0.6', ['NAsAs + NAsTe'], ['As10Cu30Te60']],
                                   ['1.90 ± 0.2', ['NTeAs + NTeTe'], ['As40Te60']],
                                   ['1.93 ± 0.2', ['NTeAs + NTeTe'], ['As30Cu10Te60']],
                                   ['2.03 ± 0.2', ['NTeAs + NTeTe'], ['As20Cu20Te60']],
                                   ['1.93 ± 0.2', ['NTeAs + NTeTe'], ['As15Cu25Te60']],
                                   ['2.11 ± 0.2', ['NTeAs + NTeTe'], ['As10Cu30Te60']],
                                   ['3.16 ± 0.3', ['NAs'], ['As40Te60']],
                                   ['3.02 ± 0.3', ['NAs'], ['As30Cu10Te60']],
                                   ['3.64 ± 0.3', ['NAs'], ['As20Cu20Te60']],
                                   ['3.97 ± 0.3', ['NAs'], ['As15Cu25Te60']],
                                   ['4.06 ± 0.6', ['NAs'], ['As10Cu30Te60']],
                                   ['NoValue', ['NCu'], ['As40Te60']],
                                   ['4.50 ± 1.0', ['NCu'], ['As30Cu10Te60']],
                                   ['4.41 + 0.5', ['NCu'], ['As20Cu20Te60']],
                                   ['4.80 ± 0.5', ['NCu'], ['As15Cu25Te60']],
                                   ['5.45 ± 0.6', ['NCu'], ['As10Cu30Te60']],
                                   ['1.90 ± 0.2', ['NTe'], ['As40Te60']],
                                   ['2.32 ± 0.2', ['NTe'], ['As30Cu10Te60']],
                                   ['2.70 ± 0.2', ['NTe'], ['As20Cu20Te60']],
                                   ['2.96 ± 0.2', ['NTe'], ['As15Cu25Te60']],
                                   ['3.19 ± 0.3', ['NTe'], ['As10Cu30Te60']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_04(self):
        input_path = './tests/data/table_example3.csv'
        expected_labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['3735', ['Norway'], ['Million dollar', '2007']], ['4006', ['Norway'], ['Million dollar', '2008']], ['4081', ['Norway'], ['Million dollar', '2009']], ['4580', ['Norway'], ['Million dollar', '2010*']], ['4936', ['Norway'], ['Million dollar', '2011*']], ['0.95', ['Norway'], ['Percentage of GNI', '2007']], ['0.89', ['Norway'], ['Percentage of GNI', '2008']], ['1.06', ['Norway'], ['Percentage of GNI', '2009']], ['1.1', ['Norway'], ['Percentage of GNI', '2010*']], ['1', ['Norway'], ['Percentage of GNI', '2011*']], ['2562', ['Denmark'], ['Million dollar', '2007']], ['2803', ['Denmark'], ['Million dollar', '2008']], ['2810', ['Denmark'], ['Million dollar', '2009']], ['2871', ['Denmark'], ['Million dollar', '2010*']], ['2981', ['Denmark'], ['Million dollar', '2011*']], ['0.81', ['Denmark'], ['Percentage of GNI', '2007']], ['0.82', ['Denmark'], ['Percentage of GNI', '2008']], ['0.88', ['Denmark'], ['Percentage of GNI', '2009']], ['0.91', ['Denmark'], ['Percentage of GNI', '2010*']], ['0.86', ['Denmark'], ['Percentage of GNI', '2011*']], ['2669', ['Australia'], ['Million dollar', '2007']], ['2954', ['Australia'], ['Million dollar', '2008']], ['2762', ['Australia'], ['Million dollar', '2009']], ['3826', ['Australia'], ['Million dollar', '2010*']], ['4799', ['Australia'], ['Million dollar', '2011*']], ['0.32', ['Australia'], ['Percentage of GNI', '2007']], ['0.32', ['Australia'], ['Percentage of GNI', '2008']], ['0.29', ['Australia'], ['Percentage of GNI', '2009']], ['0.32', ['Australia'], ['Percentage of GNI', '2010*']], ['0.35', ['Australia'], ['Percentage of GNI', '2011*']], ['320', ['New Zealand'], ['Million dollar', '2007']], ['348', ['New Zealand'], ['Million dollar', '2008']], ['309', ['New Zealand'], ['Million dollar', '2009']], ['342', ['New Zealand'], ['Million dollar', '2010*']], ['429', ['New Zealand'], ['Million dollar', '2011*']], ['0.27', ['New Zealand'], ['Percentage of GNI', '2007']], ['0.3', ['New Zealand'], ['Percentage of GNI', '2008']], ['0.28', ['New Zealand'], ['Percentage of GNI', '2009']], ['0.26', ['New Zealand'], ['Percentage of GNI', '2010*']], ['0.28', ['New Zealand'], ['Percentage of GNI', '2011*']], ['104206', ['OECD/DAC1'], ['Million dollar', '2007']], ['121954', ['OECD/DAC1'], ['Million dollar', '2008']], ['119778', ['OECD/DAC1'], ['Million dollar', '2009']], ['128465', ['OECD/DAC1'], ['Million dollar', '2010*']], ['133526', ['OECD/DAC1'], ['Million dollar', '2011*']], ['0.27', ['OECD/DAC1'], ['Percentage of GNI', '2007']], ['0.3', ['OECD/DAC1'], ['Percentage of GNI', '2008']], ['0.31', ['OECD/DAC1'], ['Percentage of GNI', '2009']], ['0.32', ['OECD/DAC1'], ['Percentage of GNI', '2010*']], ['0.31', ['OECD/DAC1'], ['Percentage of GNI', '2011*']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_05(self):
        input_path = './tests/data/table_example4.csv'
        expected_labels = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['1647218', ['2003'], ['Short messages/thousands']], ['24.3', ['2003'], ['A Change %']], ['347', ['2003'], [' Short messages/subscription']], ['2314', ['2003'], ['Multimedia messages/thousands']], ['NoValue', ['2003'], ['B Change %']], ['2193498', ['2004'], ['Short messages/thousands']], ['33.2', ['2004'], ['A Change %']], ['439', ['2004'], [' Short messages/subscription']], ['7386', ['2004'], ['Multimedia messages/thousands']], ['219.2', ['2004'], ['B Change %']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_06(self):
        input_path = './tests/data/table_example6.csv'
        expected_labels = [['StubHeader', 'ColHeader'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data']]
        expected_category_table = [['6.5 K', ['Bi6Tl3'], ['Tc']], ['5.5', ['Sb2Tl7'], ['Tc']], ['7.2', ['Na2Pb5'], ['Tc']], ['3.8', ['Hg5Tl7'], ['Tc']], ['1.84', ['Au2Bi'], ['Tc']], ['1.6', ['CuS'], ['Tc']], ['1.3', ['VN'], ['Tc']], ['2.8', ['WC'], ['Tc']], ['2.05', ['W2C'], ['Tc']], ['7.7', ['MoC'], ['Tc']], ['2.4', ['Mo2C'], ['Tc']]]
        self.do_subtable(input_path, 0, expected_labels, expected_category_table)
        expected_labels = [['StubHeader', 'ColHeader'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data']]
        expected_category_table = [['1.4 K', ['TiN'], ['Tc']], ['1.1', ['TiC'], ['Tc']], ['9.2', ['TaC'], ['Tc']], ['10.1', ['NbC'], ['Tc']], ['2.82', ['ZrB'], ['Tc']], ['4.2', ['TaSi'], ['Tc']], ['4.1', ['PbS'], ['Tc']], ['8.4', ['Pb-As alloy'], ['Tc']], ['8.5', ['Pb-Sn-Bi'], ['Tc']], ['9.0', ['Pb-As-Bi'], ['Tc']], ['8.9', ['Pb-Bi-Sb'], ['Tc']]]
        self.do_subtable(input_path, 1, expected_labels, expected_category_table)

    def test_07(self):
        input_path = './tests/data/table_example7.csv'
        expected_labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader & FNref', 'ColHeader & FNref', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader & FNref', 'ColHeader & FNref'], ['FNref', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/'], ['RowHeader & FNref', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader & FNref', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['FNprefix & FNtext', 'Note', '/', '/', '/', '/', '/', '/', '/', '/', '/'], ['FNprefix', 'FNtext', '/', '/', '/', '/', '/', '/', '/', '/', '/'], ['Note', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/'], ['FNprefix & FNtext', '/', '/', '/', '/', '/', '/', '/', '/', '/', '/']]
        expected_category_table = [['3735', ["Norway DAC-countries are members of OECD's Development Assis"], ['Million dollar', '2007']], ['4081', ["Norway DAC-countries are members of OECD's Development Assis"], ['Million dollar', '2009']], ['4006', ["Norway DAC-countries are members of OECD's Development Assis"], ['Million dollar', '2008']], ['4580', ["Norway DAC-countries are members of OECD's Development Assis"], ['Million dollar', '2010 Source: OECD ']], ['4936', ["Norway DAC-countries are members of OECD's Development Assis"], ['Million dollar', '2011 Source: OECD ']], ['0.95', ["Norway DAC-countries are members of OECD's Development Assis"], ['Percentage of GNI', '2007']], ['0.89', ["Norway DAC-countries are members of OECD's Development Assis"], ['Percentage of GNI', '2008']], ['1.06', ["Norway DAC-countries are members of OECD's Development Assis"], ['Percentage of GNI', '2009']], ['1.1', ["Norway DAC-countries are members of OECD's Development Assis"], ['Percentage of GNI', '2010 Source: OECD ']], ['1', ["Norway DAC-countries are members of OECD's Development Assis"], ['Percentage of GNI', '2011 Source: OECD ']], ['2562', ['Denmark'], ['Million dollar', '2007']], ['2810', ['Denmark'], ['Million dollar', '2009']], ['2803', ['Denmark'], ['Million dollar', '2008']], ['2871', ['Denmark'], ['Million dollar', '2010 Source: OECD ']], ['2981', ['Denmark'], ['Million dollar', '2011 Source: OECD ']], ['0.81', ['Denmark'], ['Percentage of GNI', '2007']], ['0.82', ['Denmark'], ['Percentage of GNI', '2008']], ['0.88', ['Denmark'], ['Percentage of GNI', '2009']], ['0.91', ['Denmark'], ['Percentage of GNI', '2010 Source: OECD ']], ['0.86', ['Denmark'], ['Percentage of GNI', '2011 Source: OECD ']], ['2669', ['Australia'], ['Million dollar', '2007']], ['2762', ['Australia'], ['Million dollar', '2009']], ['2954', ['Australia'], ['Million dollar', '2008']], ['3826', ['Australia'], ['Million dollar', '2010 Source: OECD ']], ['4799', ['Australia'], ['Million dollar', '2011 Source: OECD ']], ['0.32', ['Australia'], ['Percentage of GNI', '2007']], ['0.32', ['Australia'], ['Percentage of GNI', '2008']], ['0.29', ['Australia'], ['Percentage of GNI', '2009']], ['0.32', ['Australia'], ['Percentage of GNI', '2010 Source: OECD ']], ['0.35', ['Australia'], ['Percentage of GNI', '2011 Source: OECD ']], ['320', ['New Zealand'], ['Million dollar', '2007']], ['309', ['New Zealand'], ['Million dollar', '2009']], ['348', ['New Zealand'], ['Million dollar', '2008']], ['342', ['New Zealand'], ['Million dollar', '2010 Source: OECD ']], ['429', ['New Zealand'], ['Million dollar', '2011 Source: OECD ']], ['0.27', ['New Zealand'], ['Percentage of GNI', '2007']], ['0.3', ['New Zealand'], ['Percentage of GNI', '2008']], ['0.28', ['New Zealand'], ['Percentage of GNI', '2009']], ['0.26', ['New Zealand'], ['Percentage of GNI', '2010 Source: OECD ']], ['0.28', ['New Zealand'], ['Percentage of GNI', '2011 Source: OECD ']], ['104206', ['OECD/DAC This is a description'], ['Million dollar', '2007']], ['119778', ['OECD/DAC This is a description'], ['Million dollar', '2009']], ['121954', ['OECD/DAC This is a description'], ['Million dollar', '2008']], ['128465', ['OECD/DAC This is a description'], ['Million dollar', '2010 Source: OECD ']], ['133526', ['OECD/DAC This is a description'], ['Million dollar', '2011 Source: OECD ']], ['0.27', ['OECD/DAC This is a description'], ['Percentage of GNI', '2007']], ['0.3', ['OECD/DAC This is a description'], ['Percentage of GNI', '2008']], ['0.31', ['OECD/DAC This is a description'], ['Percentage of GNI', '2009']], ['0.32', ['OECD/DAC This is a description'], ['Percentage of GNI', '2010 Source: OECD ']], ['0.31', ['OECD/DAC This is a description'], ['Percentage of GNI', '2011 Source: OECD ']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_08(self):
        input_path = './tests/data/table_example8.csv'
        expected_labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['1647218', ['2003'], ['', 'Short messages/thousands']],
                                   ['24.3', ['2003'], ['Short messages/thousands', 'Change %']],
                                   ['347', ['2003'], ['', 'Short messages/subscription']],
                                   ['2314', ['2003'], ['', 'Multimedia messages/thousands']],
                                   ['NoValue', ['2003'], ['Multimedia messages/thousands', 'Change %']],
                                   ['2193498', ['2004'], ['', 'Short messages/thousands']],
                                   ['33.2', ['2004'], ['Short messages/thousands', 'Change %']],
                                   ['439', ['2004'], ['', 'Short messages/subscription']],
                                   ['7386', ['2004'], ['', 'Multimedia messages/thousands']],
                                   ['219.2', ['2004'], ['Multimedia messages/thousands', 'Change %']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_09(self):
        input_path = './tests/data/table_example9.csv'
        expected_labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'StubHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'RowHeader', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data']]
        expected_category_table = [['1647218', ['', 'Short messages/thousands'], ['2003']],
                                   ['2193498', ['', 'Short messages/thousands'], ['2004']],
                                   ['24.3', ['Short messages/thousands', 'Change %'], ['2003']],
                                   ['33.2', ['Short messages/thousands', 'Change %'], ['2004']],
                                   ['347', ['', 'Short messages/subscription'], ['2003']],
                                   ['439', ['', 'Short messages/subscription'], ['2004']],
                                   ['2314', ['', 'Multimedia messages/thousands'], ['2003']],
                                   ['7386', ['', 'Multimedia messages/thousands'], ['2004']],
                                   ['NoValue', ['Multimedia messages/thousands', 'Change %'], ['2003']],
                                   ['219.2', ['Multimedia messages/thousands', 'Change %'], ['2004']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_10(self):
        input_path = './tests/data/table_example_footnotes.csv'
        expected_labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader & FNref', 'ColHeader & FNref & FNref', 'ColHeader', 'ColHeader & FNref', 'ColHeader & FNref'], ['RowHeader & FNref', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader & FNref', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader & FNref', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['FNprefix', 'FNtext', '/', '/', '/', '/', '/'], ['FNprefix & FNtext', 'Note', 'Note', '/', '/', '/', '/'], ['FNprefix & FNtext', '/', '/', '/', '/', '/', '/'], ['FNprefix', '/', '/', '/', '/', '/', '/'], ['FNprefix & FNtext', '/', '/', '/', '/', '/', '/'], ['Note', 'Note', '/', '/', '/', '/', '/']]
        expected_category_table = [['3735', [' whataboutthis '], ['Million dollar', '2007']], ['4580', [' whataboutthis '], ['Million dollar', '2010 Test ']], ['4936', [' whataboutthis '], ['Million dollar', '2011 Test   whataboutthis ']], ['0.95', [' whataboutthis '], ['Percentage of GNI', '2007']], ['1.1', [' whataboutthis '], ['Percentage of GNI', '2010 Source: OECD. ']], ['1', [' whataboutthis '], ['Percentage of GNI', '2011 Source: OECD. ']], ['2669', ['2'], ['Million dollar', '2007']], ['3826', ['2'], ['Million dollar', '2010 Test ']], ['4799', ['2'], ['Million dollar', '2011 Test   whataboutthis ']], ['0.32', ['2'], ['Percentage of GNI', '2007']], ['0.32', ['2'], ['Percentage of GNI', '2010 Source: OECD. ']], ['0.35', ['2'], ['Percentage of GNI', '2011 Source: OECD. ']], ['320', ['New Zealand '], ['Million dollar', '2007']], ['342', ['New Zealand '], ['Million dollar', '2010 Test ']], ['429', ['New Zealand '], ['Million dollar', '2011 Test   whataboutthis ']], ['0.27', ['New Zealand '], ['Percentage of GNI', '2007']], ['0.26', ['New Zealand '], ['Percentage of GNI', '2010 Source: OECD. ']], ['0.28', ['New Zealand '], ['Percentage of GNI', '2011 Source: OECD. ']], ['104206', ['OECD/DAC Footnote text.'], ['Million dollar', '2007']], ['128465', ['OECD/DAC Footnote text.'], ['Million dollar', '2010 Test ']], ['133526', ['OECD/DAC Footnote text.'], ['Million dollar', '2011 Test   whataboutthis ']], ['0.27', ['OECD/DAC Footnote text.'], ['Percentage of GNI', '2007']], ['0.32', ['OECD/DAC Footnote text.'], ['Percentage of GNI', '2010 Source: OECD. ']], ['0.31', ['OECD/DAC Footnote text.'], ['Percentage of GNI', '2011 Source: OECD. ']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_11(self):
        input_path = './tests/data/te_01.csv'
        expected_labels = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['"4.64"', ['"This study"'], ['"A"']], ['"2.99"', ['"This study"'], ['"B"']], ['"0.305"', ['"This study"'], ['"C"']], ['"3.83"', ['"This study"'], ['"D"']], ['"9.62"', ['"This study"'], ['"E"']], ['"0.208"', ['"This study"'], ['"F"']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_12(self):
        input_path = './tests/data/te_02.csv'
        expected_labels = [['StubHeader', 'ColHeader'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data']]
        expected_category_table = [['"4.64"', ['"A"'], ['"This study"']], ['"2.99"', ['"B"'], ['"This study"']], ['"0.305"', ['"C"'], ['"This study"']], ['"3.83"', ['"D"'], ['"This study"']], ['"9.62"', ['"E"'], ['"This study"']], ['"0.208"', ['"F"'], ['"This study"']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_13(self):
        input_path = './tests/data/te_04.csv'
        expected_labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['4869', ['1990'], ['School', 'School', 'School']], ['2189', ['1990'], ['Pupils', 'Pre-primary', 'Pre-primary']], ['389410', ['1990'], ['Pupils', 'Grades', '6 Jan']], ['197719', ['1990'], ['Pupils', 'Grades', '9 Jul']], ['NoValue', ['1990'], ['Pupils', 'Additional', 'Additional']], ['592920', ['1990'], ['Pupils', 'Total', 'Total']], ['67427', ['1990'], ['Grade 1', 'Grade 1', 'Grade 1']], ['61054', ['1990'], ['Leaving certificates', 'Leaving certificates', 'Leaving certificates']], ['4861', ['1991'], ['School', 'School', 'School']], ['2181', ['1991'], ['Pupils', 'Pre-primary', 'Pre-primary']], ['389411', ['1991'], ['Pupils', 'Grades', '6 Jan']], ['197711', ['1991'], ['Pupils', 'Grades', '9 Jul']], ['3601', ['1991'], ['Pupils', 'Additional', 'Additional']], ['592921', ['1991'], ['Pupils', 'Total', 'Total']], ['67421', ['1991'], ['Grade 1', 'Grade 1', 'Grade 1']], ['NoValue', ['1991'], ['Leaving certificates', 'Leaving certificates', 'Leaving certificates']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_14(self):
        input_path = './tests/data/te_05.csv'
        expected_labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['0', ['Total'], ['', 'Add']], ['597', ['Total'], ['Total', 'justice']], ['264', ['Total'], ['Police', 'protec-']], ['123', ['Total'], ['Judicial', 'and']], ['210', ['Total'], ['', 'Correc-']], ['23', ['Alabama'], ['', 'Add']], ['420', ['Alabama'], ['Total', 'justice']], ['201', ['Alabama'], ['Police', 'protec-']], ['78', ['Alabama'], ['Judicial', 'and']], ['141', ['Alabama'], ['', 'Correc-']], ['0', ['Alaska'], ['', 'Add']], ['894', ['Alaska'], ['Total', 'justice']], ['318', ['Alaska'], ['Police', 'protec-']], ['263', ['Alaska'], ['Judicial', 'and']], ['313', ['Alaska'], ['', 'Correc-']], ['0', ['Arizona'], ['', 'Add']], ['643', ['Arizona'], ['Total', 'justice']], ['275', ['Arizona'], ['Police', 'protec-']], ['137', ['Arizona'], ['Judicial', 'and']], ['232', ['Arizona'], ['', 'Correc-']]]
        self.do_table(input_path, expected_labels, expected_category_table)

    def test_15(self):
        input_path = './tests/data/te_06.csv'
        expected_labels = [['StubHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data']]
        expected_category_table = [['6.5', ['Bi6Tl3'], ['Tc']], ['x', ['Bi6Tl3'], ['A']], ['5.5', ['Sb2Tl7'], ['Tc']], ['y', ['Sb2Tl7'], ['A']], ['7.2', ['Na2Pb5'], ['Tc']], ['z', ['Na2Pb5'], ['A']], ['3.8', ['Hg5Tl7'], ['Tc']], ['x', ['Hg5Tl7'], ['A']], ['1.84', ['Au2Bi'], ['Tc']], ['x', ['Au2Bi'], ['A']], ['1.6', ['CuS'], ['Tc']], ['x', ['CuS'], ['A']], ['1.3', ['VN'], ['Tc']], ['x', ['VN'], ['A']], ['2.8', ['WC'], ['Tc']], ['x', ['WC'], ['A']], ['2.05', ['W2C'], ['Tc']], ['x', ['W2C'], ['A']], ['7.7', ['MoC'], ['Tc']], ['x', ['MoC'], ['A']], ['2.4', ['Mo2C'], ['Tc']], ['x', ['Mo2C'], ['A']]]
        self.do_subtable(input_path, 0, expected_labels, expected_category_table)
        expected_labels = [['StubHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data'], ['RowHeader', 'Data', 'Data']]
        expected_category_table = [['1.4', ['TiN'], ['Tc']], ['y', ['TiN'], ['A']], ['1.1', ['TiC'], ['Tc']], ['x', ['TiC'], ['A']], ['9.2', ['TaC'], ['Tc']], ['x', ['TaC'], ['A']], ['10.1', ['NbC'], ['Tc']], ['a', ['NbC'], ['A']], ['2.82', ['ZrB'], ['Tc']], ['x', ['ZrB'], ['A']], ['4.2', ['TaSi'], ['Tc']], ['x', ['TaSi'], ['A']], ['4.1', ['PbS'], ['Tc']], ['x', ['PbS'], ['A']], ['8.4', ['Pb-As alloy'], ['Tc']], ['x', ['Pb-As alloy'], ['A']], ['8.5', ['Pb-Sn-Bi'], ['Tc']], ['x', ['Pb-Sn-Bi'], ['A']], ['9.0', ['Pb-As-Bi'], ['Tc']], ['x', ['Pb-As-Bi'], ['A']], ['8.9', ['Pb-Bi-Sb'], ['Tc']], ['x', ['Pb-Bi-Sb'], ['A']]]
        self.do_subtable(input_path, 1, expected_labels, expected_category_table)
        expected_labels = [['StubHeader', 'ColHeader'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data'], ['RowHeader', 'Data']]
        expected_category_table = [['1.1', ['TiO2'], ['Tc']], ['1.2', ['TiO3'], ['Tc']], ['1.3', ['TiO4'], ['Tc']], ['1.4', ['TiO5'], ['Tc']], ['1.5', ['TiO6'], ['Tc']], ['1.6', ['TiO7'], ['Tc']], ['1.7', ['TiO8'], ['Tc']], ['1.8', ['TiO9'], ['Tc']], ['1.9', ['TiO10'], ['Tc']], ['1.10', ['TiO11'], ['Tc']], ['1.11', ['TiO12'], ['Tc']]]
        self.do_subtable(input_path, 2, expected_labels, expected_category_table)

    def test_16(self):
        input_path = './tests/data/te_08.csv'
        expected_labels = [['StubHeader', 'StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        expected_category_table = [['2.431', ['La0.67Ba0.1Ca0.23MnO3', '1'], ['−ΔSM (J kg−1 K−1)']], ['42.37', ['La0.67Ba0.1Ca0.23MnO3', '1'], ['δTFWHM (K)']], ['103.001', ['La0.67Ba0.1Ca0.23MnO3', '1'], ['RCP (J kg−1)']], ['25.41', ['La0.67Ba0.1Ca0.23MnO3', '1'], ['ΔCp H max (J kg−1 K−1)']], ['−23.90', ['La0.67Ba0.1Ca0.23MnO3', '1'], ['ΔCp H min (J kg−1 K−1)']], ['Present', ['La0.67Ba0.1Ca0.23MnO3', '1'], ['Ref.']], ['3.721', ['La0.67Ba0.1Ca0.23MnO3', '2'], ['−ΔSM (J kg−1 K−1)']], ['40.16', ['La0.67Ba0.1Ca0.23MnO3', '2'], ['δTFWHM (K)']], ['149.435', ['La0.67Ba0.1Ca0.23MnO3', '2'], ['RCP (J kg−1)']], ['27.02', ['La0.67Ba0.1Ca0.23MnO3', '2'], ['ΔCp H max (J kg−1 K−1)']], ['−24.90', ['La0.67Ba0.1Ca0.23MnO3', '2'], ['ΔCp H min (J kg−1 K−1)']], ['Present', ['La0.67Ba0.1Ca0.23MnO3', '2'], ['Ref.']], ['4.736', ['La0.67Ba0.1Ca0.23MnO3', '3'], ['−ΔSM (J kg−1 K−1)']], ['40.75', ['La0.67Ba0.1Ca0.23MnO3', '3'], ['δTFWHM (K)']], ['192.992', ['La0.67Ba0.1Ca0.23MnO3', '3'], ['RCP (J kg−1)']], ['28.02', ['La0.67Ba0.1Ca0.23MnO3', '3'], ['ΔCp H max (J kg−1 K−1)']], ['−24.23', ['La0.67Ba0.1Ca0.23MnO3', '3'], ['ΔCp H min (J kg−1 K−1)']], ['Present', ['La0.67Ba0.1Ca0.23MnO3', '3'], ['Ref.']], ['5.742', ['La0.67Ba0.1Ca0.23MnO3', '4'], ['−ΔSM (J kg−1 K−1)']], ['42.32', ['La0.67Ba0.1Ca0.23MnO3', '4'], ['δTFWHM (K)']], ['243.001', ['La0.67Ba0.1Ca0.23MnO3', '4'], ['RCP (J kg−1)']], ['28.19', ['La0.67Ba0.1Ca0.23MnO3', '4'], ['ΔCp H max (J kg−1 K−1)']], ['−23.88', ['La0.67Ba0.1Ca0.23MnO3', '4'], ['ΔCp H min (J kg−1 K−1)']], ['Present', ['La0.67Ba0.1Ca0.23MnO3', '4'], ['Ref.']], ['5.971', ['La0.67Ba0.1Ca0.23MnO3', '5'], ['−ΔSM (J kg−1 K−1)']], ['46.65', ['La0.67Ba0.1Ca0.23MnO3', '5'], ['δTFWHM (K)']], ['278.547', ['La0.67Ba0.1Ca0.23MnO3', '5'], ['RCP (J kg−1)']], ['28.70', ['La0.67Ba0.1Ca0.23MnO3', '5'], ['ΔCp H max (J kg−1 K−1)']], ['−24.39', ['La0.67Ba0.1Ca0.23MnO3', '5'], ['ΔCp H min (J kg−1 K−1)']], ['Present', ['La0.67Ba0.1Ca0.23MnO3', '5'], ['Ref.']], ['2.2', ['La0.7Ca0.3MnO3', '2'], ['−ΔSM (J kg−1 K−1)']], ['NoValue', ['La0.7Ca0.3MnO3', '2'], ['δTFWHM (K)']], ['55', ['La0.7Ca0.3MnO3', '2'], ['RCP (J kg−1)']], ['NoValue', ['La0.7Ca0.3MnO3', '2'], ['ΔCp H max (J kg−1 K−1)']], ['NoValue', ['La0.7Ca0.3MnO3', '2'], ['ΔCp H min (J kg−1 K−1)']], ['19', ['La0.7Ca0.3MnO3', '2'], ['Ref.']], ['2.26', ['La0.6Sr0.2Ba0.2MnO3', '1'], ['−ΔSM (J kg−1 K−1)']], ['NoValue', ['La0.6Sr0.2Ba0.2MnO3', '1'], ['δTFWHM (K)']], ['67', ['La0.6Sr0.2Ba0.2MnO3', '1'], ['RCP (J kg−1)']], ['NoValue', ['La0.6Sr0.2Ba0.2MnO3', '1'], ['ΔCp H max (J kg−1 K−1)']], ['NoValue', ['La0.6Sr0.2Ba0.2MnO3', '1'], ['ΔCp H min (J kg−1 K−1)']], ['34', ['La0.6Sr0.2Ba0.2MnO3', '1'], ['Ref.']], ['1.46', ['La0.60Y0.07Ca0.33MnO3', '3'], ['−ΔSM (J kg−1 K−1)']], ['NoValue', ['La0.60Y0.07Ca0.33MnO3', '3'], ['δTFWHM (K)']], ['140', ['La0.60Y0.07Ca0.33MnO3', '3'], ['RCP (J kg−1)']], ['NoValue', ['La0.60Y0.07Ca0.33MnO3', '3'], ['ΔCp H max (J kg−1 K−1)']], ['NoValue', ['La0.60Y0.07Ca0.33MnO3', '3'], ['ΔCp H min (J kg−1 K−1)']], ['35', ['La0.60Y0.07Ca0.33MnO3', '3'], ['Ref.']], ['4', ['La0.7Sr0.3Mn0.93Fe0.07O3', '5'], ['−ΔSM (J kg−1 K−1)']], ['NoValue', ['La0.7Sr0.3Mn0.93Fe0.07O3', '5'], ['δTFWHM (K)']], ['255', ['La0.7Sr0.3Mn0.93Fe0.07O3', '5'], ['RCP (J kg−1)']], ['NoValue', ['La0.7Sr0.3Mn0.93Fe0.07O3', '5'], ['ΔCp H max (J kg−1 K−1)']], ['NoValue', ['La0.7Sr0.3Mn0.93Fe0.07O3', '5'], ['ΔCp H min (J kg−1 K−1)']], ['36', ['La0.7Sr0.3Mn0.93Fe0.07O3', '5'], ['Ref.']], ['2.68', ['La0.67Sr0.33MnO3', '2'], ['−ΔSM (J kg−1 K−1)']], ['NoValue', ['La0.67Sr0.33MnO3', '2'], ['δTFWHM (K)']], ['85', ['La0.67Sr0.33MnO3', '2'], ['RCP (J kg−1)']], ['NoValue', ['La0.67Sr0.33MnO3', '2'], ['ΔCp H max (J kg−1 K−1)']], ['NoValue', ['La0.67Sr0.33MnO3', '2'], ['ΔCp H min (J kg−1 K−1)']], ['37', ['La0.67Sr0.33MnO3', '2'], ['Ref.']]]
        self.do_table(input_path, expected_labels, expected_category_table)


if __name__ == '__main__':
    unittest.main()

