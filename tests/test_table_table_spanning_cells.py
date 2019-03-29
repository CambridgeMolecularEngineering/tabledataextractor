# -*- coding: utf-8 -*-
"""
Tests the spanning cells extension

.. codeauthor: Juraj Mavračić (jm2111@cam.ac.uk)
"""

import unittest
import logging

from tabledataextractor import Table

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestSpanningCells(unittest.TestCase):

    def test_default_config(self):
        table = Table("./tests/data/te_04.csv")
        table.print()
        pre_cleaned_table = [['Pupils in comprehensive schools and with leaving certificate', '', '', '', '', '', '', '', ''],
                             ['Year', 'School', 'Pupils', 'Pupils', 'Pupils', 'Pupils', 'Pupils', 'Grade 1','Leaving certificates'],
                             ['Year', 'School', 'Pre-primary', 'Grades', 'Grades', 'Additional', 'Total', 'Grade 1', 'Leaving certificates'],
                             ['Year', 'School', 'Pre-primary', '6 Jan', '9 Jul', 'Additional', 'Total', 'Grade 1', 'Leaving certificates'],
                             ['1990', '4869', '2189', '389410', '197719', '', '592920', '67427', '61054'],
                             ['1991', '4861', '2181', '389411', '197711', '3601', '592921', '67421', '']]
        category_table = [['4869', ['1990'], ['School', 'School', 'School']], ['2189', ['1990'], ['Pupils', 'Pre-primary', 'Pre-primary']], ['389410', ['1990'], ['Pupils', 'Grades', '6 Jan']], ['197719', ['1990'], ['Pupils', 'Grades', '9 Jul']], ['', ['1990'], ['Pupils', 'Additional', 'Additional']], ['592920', ['1990'], ['Pupils', 'Total', 'Total']], ['67427', ['1990'], ['Grade 1', 'Grade 1', 'Grade 1']], ['61054', ['1990'], ['Leaving certificates', 'Leaving certificates', 'Leaving certificates']], ['4861', ['1991'], ['School', 'School', 'School']], ['2181', ['1991'], ['Pupils', 'Pre-primary', 'Pre-primary']], ['389411', ['1991'], ['Pupils', 'Grades', '6 Jan']], ['197711', ['1991'], ['Pupils', 'Grades', '9 Jul']], ['3601', ['1991'], ['Pupils', 'Additional', 'Additional']], ['592921', ['1991'], ['Pupils', 'Total', 'Total']], ['67421', ['1991'], ['Grade 1', 'Grade 1', 'Grade 1']], ['', ['1991'], ['Leaving certificates', 'Leaving certificates', 'Leaving certificates']]]
        labels = [['TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle', 'TableTitle'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'], ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.assertListEqual(pre_cleaned_table, table._pre_cleaned_table.tolist())
        self.assertListEqual(category_table, table.category_table)
        self.assertListEqual(labels, table.labels.tolist())

    def test_specific_config(self):
        table = Table("./tests/data/te_04.csv", use_title_row=False, use_prefixing=False)
        table.print()
        pre_cleaned_table = [['Pupils in comprehensive schools and with leaving certificate', 'Pupils in comprehensive schools and with leaving certificate', 'Pupils in comprehensive schools and with leaving certificate', 'Pupils in comprehensive schools and with leaving certificate', 'Pupils in comprehensive schools and with leaving certificate', 'Pupils in comprehensive schools and with leaving certificate', 'Pupils in comprehensive schools and with leaving certificate', 'Pupils in comprehensive schools and with leaving certificate', 'Pupils in comprehensive schools and with leaving certificate'],
                             ['Year', 'School', 'Pupils', 'Pupils', 'Pupils', 'Pupils', 'Pupils', 'Grade 1','Leaving certificates'],
                             ['Year', 'School', 'Pre-primary', 'Grades', 'Grades', 'Additional', 'Total', 'Grade 1', 'Leaving certificates'],
                             ['Year', 'School', 'Pre-primary', '6 Jan', '9 Jul', 'Additional', 'Total', 'Grade 1', 'Leaving certificates'],
                             ['1990', '4869', '2189', '389410', '197719', '', '592920', '67427', '61054'],
                             ['1991', '4861', '2181', '389411', '197711', '3601', '592921', '67421', '']]
        category_table = [['4869', ['1990'], ['Pupils in comprehensive schools and with leaving certificate', 'School', 'School', 'School']], ['2189', ['1990'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Pre-primary', 'Pre-primary']], ['389410', ['1990'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Grades', '6 Jan']], ['197719', ['1990'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Grades', '9 Jul']], ['', ['1990'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Additional', 'Additional']], ['592920', ['1990'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Total', 'Total']], ['67427', ['1990'], ['Pupils in comprehensive schools and with leaving certificate', 'Grade 1', 'Grade 1', 'Grade 1']], ['61054', ['1990'], ['Pupils in comprehensive schools and with leaving certificate', 'Leaving certificates', 'Leaving certificates', 'Leaving certificates']], ['4861', ['1991'], ['Pupils in comprehensive schools and with leaving certificate', 'School', 'School', 'School']], ['2181', ['1991'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Pre-primary', 'Pre-primary']], ['389411', ['1991'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Grades', '6 Jan']], ['197711', ['1991'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Grades', '9 Jul']], ['3601', ['1991'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Additional', 'Additional']], ['592921', ['1991'], ['Pupils in comprehensive schools and with leaving certificate', 'Pupils', 'Total', 'Total']], ['67421', ['1991'], ['Pupils in comprehensive schools and with leaving certificate', 'Grade 1', 'Grade 1', 'Grade 1']], ['', ['1991'], ['Pupils in comprehensive schools and with leaving certificate', 'Leaving certificates', 'Leaving certificates', 'Leaving certificates']]]
        labels = [['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                  ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                  ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                  ['StubHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader', 'ColHeader'],
                  ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data'],
                  ['RowHeader', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data', 'Data']]
        self.assertListEqual(pre_cleaned_table, table._pre_cleaned_table.tolist())
        self.assertListEqual(category_table, table.category_table)
        self.assertListEqual(labels, table.labels.tolist())


if __name__ == '__main__':
    unittest.main()

