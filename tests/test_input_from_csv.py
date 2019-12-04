# -*- coding: utf-8 -*-
"""
tabledataextractor.tests.test_input_from_csv.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test table parsers.
Juraj Mavračić (jm2111@cam.ac.uk)
Ed Beard (ejb207@cam.ac.uk)
"""

import unittest
import logging
import os

from tabledataextractor import Table

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestInputCsv(unittest.TestCase):

    def test_input_with_commas(self):

        path = os.path.join(os.path.dirname(__file__), 'data', 'table_commas.csv')
        table = Table(path)

        # Normal table
        table.print()
        row_0_cell_6 = table.raw_table[0][6]
        self.assertEqual(row_0_cell_6, 'PCE (η, %)')

        row_1_cell_0 = table.raw_table[1][0]
        self.assertEqual(row_1_cell_0, '2H–MoS2 (hydrothermal, 200 °C)')

        row_2_cell_0 = table.raw_table[2][0]
        self.assertEqual(row_2_cell_0, '1T–MoS2 (hydrothermal, 180 °C)')

    def test_input_with_double_quotes(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'table_double_quotes.csv')
        table = Table(path)

        row_1_cell_0 = table.raw_table[1][0]
        self.assertEqual(row_1_cell_0, 'N719 "cell')

        row_3_cell_0 = table.raw_table[3][0]
        self.assertEqual(row_3_cell_0, 'Hy"brid cell')

    def test_input_with_single_quotes(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'table_single_quotes.csv')
        table = Table(path)

        row_1_cell_0 = table.raw_table[1][0]
        self.assertEqual(row_1_cell_0, "N719 'cell")

        row_2_cell_0 = table.raw_table[2][0]
        self.assertEqual(row_2_cell_0, "N74'9 cell")

        row_2_cell_0 = table.raw_table[2][0]
        self.assertEqual(row_2_cell_0, "N74'9 cell")

        row_3_cell_2 = table.raw_table[3][2]
        self.assertEqual(row_3_cell_2, "13'.8")
