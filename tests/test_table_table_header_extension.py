# -*- coding: utf-8 -*-
"""
Tests the header extension.

.. codeauthor: Juraj Mavračić (jm2111@cam.ac.uk)
"""

import unittest
import logging

from tabledataextractor import Table

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestHeaderExtension(unittest.TestCase):

    def test_default_config_1(self):
        print("Default config parameters:")
        table = Table("./tests/data/te_05.csv")
        table.print()
        category_table = [['0', ['Total'], ['State', 'Add']], ['597', ['Total'], ['Total', 'justice']], ['264', ['Total'], ['Police', 'protec-']], ['123', ['Total'], ['Judicial', 'and']], ['210', ['Total'], ['Judicial', 'Correc-']], ['23', ['Alabama'], ['State', 'Add']], ['420', ['Alabama'], ['Total', 'justice']], ['201', ['Alabama'], ['Police', 'protec-']], ['78', ['Alabama'], ['Judicial', 'and']], ['141', ['Alabama'], ['Judicial', 'Correc-']], ['0', ['Alaska'], ['State', 'Add']], ['894', ['Alaska'], ['Total', 'justice']], ['318', ['Alaska'], ['Police', 'protec-']], ['263', ['Alaska'], ['Judicial', 'and']], ['313', ['Alaska'], ['Judicial', 'Correc-']], ['0', ['Arizona'], ['State', 'Add']], ['643', ['Arizona'], ['Total', 'justice']], ['275', ['Arizona'], ['Police', 'protec-']], ['137', ['Arizona'], ['Judicial', 'and']], ['232', ['Arizona'], ['Judicial', 'Correc-']]]
        self.assertListEqual(category_table, table.category_table)

    def test_default_config_1_off(self):
        print("Header extension turned off:")
        table = Table("./tests/data/te_05.csv", use_header_extension=False)
        table.print()
        category_table = [['0', ['Total'], ['Add']], ['597', ['Total'], ['justice']], ['264', ['Total'], ['protec-']], ['123', ['Total'], ['and']], ['210', ['Total'], ['Correc-']], ['23', ['Alabama'], ['Add']], ['420', ['Alabama'], ['justice']], ['201', ['Alabama'], ['protec-']], ['78', ['Alabama'], ['and']], ['141', ['Alabama'], ['Correc-']], ['0', ['Alaska'], ['Add']], ['894', ['Alaska'], ['justice']], ['318', ['Alaska'], ['protec-']], ['263', ['Alaska'], ['and']], ['313', ['Alaska'], ['Correc-']], ['0', ['Arizona'], ['Add']], ['643', ['Arizona'], ['justice']], ['275', ['Arizona'], ['protec-']], ['137', ['Arizona'], ['and']], ['232', ['Arizona'], ['Correc-']]]
        self.assertListEqual(category_table, table.category_table)

    def test_default_config_2(self):
        print("Default config parameters:")
        table = Table("./tests/data/table_example1.csv")
        table.print()
        category_table = [['4.64', ['Computational', 'This study'], ['Rutile', 'a = b (A)']], ['2.99', ['Computational', 'This study'], ['Rutile', 'c (A)']], ['0.305', ['Computational', 'This study'], ['Rutile', 'u']], ['3.83', ['Computational', 'This study'], ['Anatase', 'a = b (A)']], ['9.62', ['Computational', 'This study'], ['Anatase', 'c (A)']], ['0.208', ['Computational', 'This study'], ['Anatase', 'u']], ['4.67', ['Computational', 'GGA [25]'], ['Rutile', 'a = b (A)']], ['2.97', ['Computational', 'GGA [25]'], ['Rutile', 'c (A)']], ['0.305', ['Computational', 'GGA [25]'], ['Rutile', 'u']], ['3.80', ['Computational', 'GGA [25]'], ['Anatase', 'a = b (A)']], ['9.67', ['Computational', 'GGA [25]'], ['Anatase', 'c (A)']], ['0.207', ['Computational', 'GGA [25]'], ['Anatase', 'u']], ['4.63', ['Computational', 'GGA [26]'], ['Rutile', 'a = b (A)']], ['2.98', ['Computational', 'GGA [26]'], ['Rutile', 'c (A)']], ['0.305', ['Computational', 'GGA [26]'], ['Rutile', 'u']], ['""', ['Computational', 'GGA [26]'], ['Anatase', 'a = b (A)']], ['""', ['Computational', 'GGA [26]'], ['Anatase', 'c (A)']], ['""', ['Computational', 'GGA [26]'], ['Anatase', 'u']], ['""', ['Computational', 'HF [27]'], ['Rutile', 'a = b (A)']], ['""', ['Computational', 'HF [27]'], ['Rutile', 'c (A)']], ['""', ['Computational', 'HF [27]'], ['Rutile', 'u']], ['3.76', ['Computational', 'HF [27]'], ['Anatase', 'a = b (A)']], ['9.85', ['Computational', 'HF [27]'], ['Anatase', 'c (A)']], ['0.202', ['Computational', 'HF [27]'], ['Anatase', 'u']], ['4.594', ['Experimental', 'Expt. [23]'], ['Rutile', 'a = b (A)']], ['2.958', ['Experimental', 'Expt. [23]'], ['Rutile', 'c (A)']], ['0.305', ['Experimental', 'Expt. [23]'], ['Rutile', 'u']], ['3.785', ['Experimental', 'Expt. [23]'], ['Anatase', 'a = b (A)']], ['9.514', ['Experimental', 'Expt. [23]'], ['Anatase', 'c (A)']], ['0.207', ['Experimental', 'Expt. [23]'], ['Anatase', 'u']]]
        self.assertListEqual(category_table, table.category_table)

    def test_default_config_2_off(self):
        print("Default config parameters:")
        table = Table("./tests/data/table_example1.csv", use_header_extension=False)
        table.print()
        category_table = [['4.64', ['This study'], ['Rutile', 'a = b (A)']], ['2.99', ['This study'], ['Rutile', 'c (A)']], ['0.305', ['This study'], ['Rutile', 'u']], ['3.83', ['This study'], ['Anatase', 'a = b (A)']], ['9.62', ['This study'], ['Anatase', 'c (A)']], ['0.208', ['This study'], ['Anatase', 'u']], ['4.67', ['GGA [25]'], ['Rutile', 'a = b (A)']], ['2.97', ['GGA [25]'], ['Rutile', 'c (A)']], ['0.305', ['GGA [25]'], ['Rutile', 'u']], ['3.80', ['GGA [25]'], ['Anatase', 'a = b (A)']], ['9.67', ['GGA [25]'], ['Anatase', 'c (A)']], ['0.207', ['GGA [25]'], ['Anatase', 'u']], ['4.63', ['GGA [26]'], ['Rutile', 'a = b (A)']], ['2.98', ['GGA [26]'], ['Rutile', 'c (A)']], ['0.305', ['GGA [26]'], ['Rutile', 'u']], ['""', ['GGA [26]'], ['Anatase', 'a = b (A)']], ['""', ['GGA [26]'], ['Anatase', 'c (A)']], ['""', ['GGA [26]'], ['Anatase', 'u']], ['""', ['HF [27]'], ['Rutile', 'a = b (A)']], ['""', ['HF [27]'], ['Rutile', 'c (A)']], ['""', ['HF [27]'], ['Rutile', 'u']], ['3.76', ['HF [27]'], ['Anatase', 'a = b (A)']], ['9.85', ['HF [27]'], ['Anatase', 'c (A)']], ['0.202', ['HF [27]'], ['Anatase', 'u']], ['4.594', ['Expt. [23]'], ['Rutile', 'a = b (A)']], ['2.958', ['Expt. [23]'], ['Rutile', 'c (A)']], ['0.305', ['Expt. [23]'], ['Rutile', 'u']], ['3.785', ['Expt. [23]'], ['Anatase', 'a = b (A)']], ['9.514', ['Expt. [23]'], ['Anatase', 'c (A)']], ['0.207', ['Expt. [23]'], ['Anatase', 'u']]]
        self.assertListEqual(category_table, table.category_table)


if __name__ == '__main__':
    unittest.main()