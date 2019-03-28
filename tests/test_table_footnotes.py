# -*- coding: utf-8 -*-
"""
Test Footnote() class on some input tables
These tests depend on some of the features of Table() working properly.
Juraj Mavračić (jm2111@cam.ac.uk)
"""

import unittest
import logging

from tabledataextractor import Table
from tabledataextractor.table.algorithms import find_cc4
import numpy as np

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TableF(Table):
    """Derivative of Table used to isolate testing for Footnotes()"""

    def __init__(self, file_path, table_number=1, **kwargs):
        super().__init__(file_path, table_number, **kwargs)

    def _label_sections(self):
        """
        Labelling of all classification table elements.
        """
        cc4 = find_cc4(self)
        log.info("Table Cell CC4 = {}".format(cc4))
        self._cc4 = cc4

        for footnote in self._find_footnotes():
            self._footnotes.append(footnote)
            if self._configs['use_footnotes']:
                self._copy_footnotes(footnote)

    @property
    def labels(self):
        """Cell labels. Python List"""
        temp = np.empty_like(self._pre_cleaned_table, dtype="<U60")
        temp[:, :] = '/'
        temp[self._cc4] = 'CC4'

        for footnote in self.footnotes:
            temp[footnote.prefix_cell[0], footnote.prefix_cell[1]] = 'FNprefix'
            if footnote.text_cell is not None:
                temp[footnote.text_cell[0], footnote.text_cell[1]] = 'FNtext' if temp[footnote.text_cell[0], footnote.text_cell[1]] == '/' else 'FNprefix & FNtext'
            for ref_cell in footnote.reference_cells:
                temp[ref_cell[0], ref_cell[1]] = 'FNref' if temp[ref_cell[0], ref_cell[1]] == '/' else temp[ref_cell[0], ref_cell[1]] + ' & FNref'

        return temp


class TestFootnote(unittest.TestCase):

    def test_table_use_footnotes(self):
        table = TableF("./tests/data/table_example_footnotes.csv", use_footnotes=True, use_spanning_cells=False)
        table.print()

        print(table.footnotes[0])
        self.footnote_1(table.footnotes[0])
        print(table.footnotes[1])
        self.footnote_2(table.footnotes[1])
        print(table.footnotes[2])
        self.footnote_3(table.footnotes[2])
        print(table.footnotes[3])
        self.footnote_4(table.footnotes[3])
        print(table.footnotes[4])
        self.footnote_5(table.footnotes[4])

        self.table_update(table.pre_cleaned_table.tolist())

    def footnote_1(self, fn):
        self.assertEqual("c", fn.prefix)
        self.assertEqual("Footnote text.", fn.text)
        self.assertListEqual(['OECD/DAC c'], fn.references)

    def footnote_2(self, fn):
        self.assertEqual("*", fn.prefix)
        self.assertEqual("Test", fn.text)
        self.assertListEqual(['2010*', '2011* a.'], fn.references)

    def footnote_3(self, fn):
        self.assertEqual("†)", fn.prefix)
        self.assertEqual("Source: OECD.", fn.text)
        self.assertListEqual(['2010†)', '2011†)'], fn.references)

    def footnote_4(self, fn):
        self.assertEqual("2", fn.prefix)
        self.assertEqual("", fn.text)
        self.assertListEqual(['New Zealand 2'], fn.references)

    def footnote_5(self, fn):
        self.assertEqual("a.", fn.prefix)
        self.assertEqual("whataboutthis", fn.text)
        self.assertListEqual(['2011 Test  a.', 'a.'], fn.references)

    def table_update(self, pre_cleaned_table):
        """Tests if the table has been correctly updated with the footnotes"""
        expected = [['1 Official development assistance', '', '', '', '', '', ''],
                    ['Country', 'Million dollar', 'Million dollar', 'Million dollar', 'Percentage of GNI', 'Percentage of GNI', 'Percentage of GNI'],
                    ['', '2007', '2010 Test ', '2011 Test   whataboutthis ', '2007', '2010 Source: OECD. ', '2011 Source: OECD. '],
                    [' whataboutthis ', '3735', '4580', '4936', '0.95', '1.1', '1'],
                    ['2', '2669', '3826', '4799', '0.32', '0.32', '0.35'],
                    ['New Zealand ', '320', '342', '429', '0.27', '0.26', '0.28'],
                    ['OECD/DAC Footnote text.', '104206', '128465', '133526', '0.27', '0.32', '0.31'],
                    ['c', 'Footnote text.', '', '', '', '', ''],
                    ['* Test', 'This is now just a note', ' because the footnote text was found on the left', '', '', '', ''],
                    ['†) Source: OECD.', '', '', '', '', '', ''],
                    ['2', '', '', '', '', '', ''],
                    ['a.whataboutthis', '', '', '', '', '', ''],
                    ['0.32 This should not be recognized as a footnote', 'This should not be recognized as a footnote.', '', '', '', '', '']]
        self.assertListEqual(expected, pre_cleaned_table)

    def test_table_dont_use_footnotes(self):
        table = TableF("./tests/data/table_example_footnotes.csv", use_footnotes=False, use_spanning_cells=False)
        table.print()

        print(table.footnotes[0])
        self.footnote_1b(table.footnotes[0])
        print(table.footnotes[1])
        self.footnote_2b(table.footnotes[1])
        print(table.footnotes[2])
        self.footnote_3b(table.footnotes[2])
        print(table.footnotes[3])
        self.footnote_4b(table.footnotes[3])
        print(table.footnotes[4])
        self.footnote_5b(table.footnotes[4])

        self.table_no_update(table.pre_cleaned_table.tolist())

    def footnote_1b(self, fn):
        self.assertEqual("c", fn.prefix)
        self.assertEqual("Footnote text.", fn.text)
        self.assertListEqual(['OECD/DAC c'], fn.references)

    def footnote_2b(self, fn):
        self.assertEqual("*", fn.prefix)
        self.assertEqual("Test", fn.text)
        self.assertListEqual(['2010*', '2011* a.'], fn.references)

    def footnote_3b(self, fn):
        self.assertEqual("†)", fn.prefix)
        self.assertEqual("Source: OECD.", fn.text)
        self.assertListEqual(['2010†)', '2011†)'], fn.references)

    def footnote_4b(self, fn):
        self.assertEqual("2", fn.prefix)
        self.assertEqual("", fn.text)
        self.assertListEqual(['New Zealand 2'], fn.references)

    def footnote_5b(self, fn):
        self.assertEqual("a.", fn.prefix)
        self.assertEqual("whataboutthis", fn.text)
        self.assertListEqual(['2011* a.', 'a.'], fn.references)

    def table_no_update(self, pre_cleaned_table):
        """Tests if the table has been correctly updated with the footnotes"""
        expected = [['1 Official development assistance', '', '', '', '', '', ''],
                    ['Country', 'Million dollar', 'Million dollar', 'Million dollar', 'Percentage of GNI', 'Percentage of GNI', 'Percentage of GNI'],
                    ['', '2007', '2010*', '2011* a.', '2007', '2010†)', '2011†)'],
                    ['a.', '3735', '4580', '4936', '0.95', '1.1', '1'],
                    ['2', '2669', '3826', '4799', '0.32', '0.32', '0.35'],
                    ['New Zealand 2', '320', '342', '429', '0.27', '0.26', '0.28'],
                    ['OECD/DAC c', '104206', '128465', '133526', '0.27', '0.32', '0.31'],
                    ['c', 'Footnote text.', '', '', '', '', ''],
                    ['* Test', 'This is now just a note', ' because the footnote text was found on the left', '', '', '', ''],
                    ['†) Source: OECD.', '', '', '', '', '', ''],
                    ['2', '', '', '', '', '', ''],
                    ['a.whataboutthis', '', '', '', '', '', ''],
                    ['0.32 This should not be recognized as a footnote', 'This should not be recognized as a footnote.', '', '', '', '', '']]
        self.assertListEqual(expected, pre_cleaned_table)


if __name__ == '__main__':
    unittest.main()
