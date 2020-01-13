# -*- coding: utf-8 -*-
"""
tabledataextractor.tests.test_input_from_csv.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test csv table output parser
Ed Beard (ejb207@cam.ac.uk)
"""


import unittest
import logging
import os

from tabledataextractor import Table
from tabledataextractor.output.to_csv import write_to_csv


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestOutputCsv(unittest.TestCase):

    def do_conversion(self, filename):
        """ Helper function to convert from input to output"""

        # Paths to csv files
        in_path = os.path.join(os.path.dirname(__file__), 'data', filename)
        out_path = os.path.join(os.path.dirname(__file__), 'data', 'temp_' + filename)

        # Load input csv as tde_table and string
        with open(in_path, 'r', encoding='utf-8') as f:
            in_string = f.read()
        table = Table(in_path)

        # Output csv and import as string
        write_to_csv(table.raw_table, out_path)
        with open(in_path, 'r', encoding='utf-8') as f:
            out_string = f.read()
        os.remove(out_path)

        self.assertEqual(in_string, out_string)

    def test_table_example1(self):
        self.do_conversion('table_example1.csv')

    def test_table_double_quotes(self):
        self.do_conversion('table_double_quotes.csv')

    def test_all_example_tables(self):
        for file in os.listdir(os.path.join(os.path.dirname(__file__), 'data')):
            self.do_conversion(file)






