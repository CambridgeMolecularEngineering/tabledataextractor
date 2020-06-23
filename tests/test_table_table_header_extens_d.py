# -*- coding: utf-8 -*-
"""
Tests the downwards header extension

.. codeauthor: Juraj Mavračić <jm2111@cam.ac.uk>
"""

import unittest
import logging

from tabledataextractor import Table

log = logging.getLogger(__name__)


class TestHeaderExtDown(unittest.TestCase):

    def test_rows_extension(self):
        table = Table('./tests/data/te_03.csv')
        table.print()
        category_table = [['4.64', ['This study'], ['Test2', 'A']], ['2.99', ['This study'], ['Test3', 'B']], ['0.305', ['This study'], ['Test4', 'C']], ['3.83', ['This study'], ['Test5', 'D']], ['9.62', ['This study'], ['Test6', 'E']], ['0.208', ['This study'], ['Test7', 'F']]]
        labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.assertListEqual(category_table, table.category_table)
        self.assertListEqual(labels, table.labels.tolist())

    def test_no_rows_extension(self):
        table = Table('./tests/data/table_example5.csv')
        table.transpose()
        table.print()
        category_table = [['24.3', ['Short messages/thousands', 'Change %'], ['2003', '1647218']], ['33.2', ['Short messages/thousands', 'Change %'], ['2004', '2193498']], ['347', ['Short messages/thousands', ' Short messages/subscription'], ['2003', '1647218']], ['439', ['Short messages/thousands', ' Short messages/subscription'], ['2004', '2193498']], ['2314', ['Short messages/thousands', 'Multimedia messages/thousands'], ['2003', '1647218']], ['7386', ['Short messages/thousands', 'Multimedia messages/thousands'], ['2004', '2193498']], ['NoValue', ['Multimedia messages/thousands', 'Change %'], ['2003', '1647218']], ['219.2', ['Multimedia messages/thousands', 'Change %'], ['2004', '2193498']]]
        labels = [['StubHeader', 'StubHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'StubHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'RowHeader', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data'], ['RowHeader', 'RowHeader', 'Data', 'Data']]
        self.assertListEqual(category_table, table.category_table)
        self.assertListEqual(labels, table.labels.tolist())

    def test_col_extension(self):
        table = Table('./tests/data/te_03.csv')
        table.transpose()
        table.print()
        category_table = [['4.64', ['Test', 'Test2', 'A'], ['This study']], ['2.99', ['Test', 'Test3', 'B'], ['This study']], ['0.305', ['Test', 'Test4', 'C'], ['This study']], ['3.83', ['Test', 'Test5', 'D'], ['This study']], ['9.62', ['Test', 'Test6', 'E'], ['This study']], ['0.208', ['Test', 'Test7', 'F'], ['This study']]]
        labels = [['StubHeader', 'StubHeader', 'StubHeader', 'ColHeader'], ['RowHeader', 'RowHeader', 'RowHeader', 'Data'], ['RowHeader', 'RowHeader', 'RowHeader', 'Data'], ['RowHeader', 'RowHeader', 'RowHeader', 'Data'], ['RowHeader', 'RowHeader', 'RowHeader', 'Data'], ['RowHeader', 'RowHeader', 'RowHeader', 'Data'], ['RowHeader', 'RowHeader', 'RowHeader', 'Data']]
        self.assertListEqual(category_table, table.category_table)
        self.assertListEqual(labels, table.labels.tolist())

    def test_no_col_extension(self):
        table = Table('./tests/data/table_example5.csv')
        table.print()
        category_table = [['1647218', ['2003'], ['', 'Short messages/thousands']], ['24.3', ['2003'], ['Short messages/thousands', 'Change %']], ['347', ['2003'], ['Short messages/thousands', ' Short messages/subscription']], ['2314', ['2003'], ['Short messages/thousands', 'Multimedia messages/thousands']], ['NoValue', ['2003'], ['Multimedia messages/thousands', 'Change %']], ['2193498', ['2004'], ['', 'Short messages/thousands']], ['33.2', ['2004'], ['Short messages/thousands', 'Change %']], ['439', ['2004'], ['Short messages/thousands', ' Short messages/subscription']], ['7386', ['2004'], ['Short messages/thousands', 'Multimedia messages/thousands']], ['219.2', ['2004'], ['Multimedia messages/thousands', 'Change %']]]
        labels = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.assertListEqual(category_table, table.category_table)
        self.assertListEqual(labels, table.labels.tolist())


if __name__ == '__main__':
    unittest.main()
