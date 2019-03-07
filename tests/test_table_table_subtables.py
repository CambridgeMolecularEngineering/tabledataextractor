# -*- coding: utf-8 -*-
"""
Tests the subtables.

.. codeauthor: Juraj Mavračić (jm2111@cam.ac.uk)
"""

import unittest
import logging

from tabledataextractor import Table

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestSubtables(unittest.TestCase):

    def test_default_config_1(self):
        """Three subtables are expected"""
        table = Table("./tests/data/te_06.csv")

        pre_cleaned_table = [['Material', 'Tc', 'A'], ['Bi6Tl3', '6.5', 'x'], ['Sb2Tl7', '5.5', 'y'], ['Na2Pb5', '7.2', 'z'], ['Hg5Tl7', '3.8', 'x'], ['Au2Bi', '1.84', 'x'], ['CuS', '1.6', 'x'], ['VN', '1.3', 'x'], ['WC', '2.8', 'x'], ['W2C', '2.05', 'x'], ['MoC', '7.7', 'x'], ['Mo2C', '2.4', 'x']]
        category_table = [['6.5', ['Bi6Tl3'], ['Tc']], ['x', ['Bi6Tl3'], ['A']], ['5.5', ['Sb2Tl7'], ['Tc']], ['y', ['Sb2Tl7'], ['A']], ['7.2', ['Na2Pb5'], ['Tc']], ['z', ['Na2Pb5'], ['A']], ['3.8', ['Hg5Tl7'], ['Tc']], ['x', ['Hg5Tl7'], ['A']], ['1.84', ['Au2Bi'], ['Tc']], ['x', ['Au2Bi'], ['A']], ['1.6', ['CuS'], ['Tc']], ['x', ['CuS'], ['A']], ['1.3', ['VN'], ['Tc']], ['x', ['VN'], ['A']], ['2.8', ['WC'], ['Tc']], ['x', ['WC'], ['A']], ['2.05', ['W2C'], ['Tc']], ['x', ['W2C'], ['A']], ['7.7', ['MoC'], ['Tc']], ['x', ['MoC'], ['A']], ['2.4', ['Mo2C'], ['Tc']], ['x', ['Mo2C'], ['A']]]
        self.assertListEqual(pre_cleaned_table, table.subtables[0].pre_cleaned_table.tolist())
        self.assertListEqual(category_table, table.subtables[0].category_table)

        pre_cleaned_table = [['Material', 'Tc', 'A'], ['TiN', '1.4', 'y'], ['TiC', '1.1', 'x'], ['TaC', '9.2', 'x'], ['NbC', '10.1', 'a'], ['ZrB', '2.82', 'x'], ['TaSi', '4.2', 'x'], ['PbS', '4.1', 'x'], ['Pb-As alloy', '8.4', 'x'], ['Pb-Sn-Bi', '8.5', 'x'], ['Pb-As-Bi', '9.0', 'x'], ['Pb-Bi-Sb', '8.9', 'x']]
        category_table = [['1.4', ['TiN'], ['Tc']], ['y', ['TiN'], ['A']], ['1.1', ['TiC'], ['Tc']], ['x', ['TiC'], ['A']], ['9.2', ['TaC'], ['Tc']], ['x', ['TaC'], ['A']], ['10.1', ['NbC'], ['Tc']], ['a', ['NbC'], ['A']], ['2.82', ['ZrB'], ['Tc']], ['x', ['ZrB'], ['A']], ['4.2', ['TaSi'], ['Tc']], ['x', ['TaSi'], ['A']], ['4.1', ['PbS'], ['Tc']], ['x', ['PbS'], ['A']], ['8.4', ['Pb-As alloy'], ['Tc']], ['x', ['Pb-As alloy'], ['A']], ['8.5', ['Pb-Sn-Bi'], ['Tc']], ['x', ['Pb-Sn-Bi'], ['A']], ['9.0', ['Pb-As-Bi'], ['Tc']], ['x', ['Pb-As-Bi'], ['A']], ['8.9', ['Pb-Bi-Sb'], ['Tc']], ['x', ['Pb-Bi-Sb'], ['A']]]
        self.assertListEqual(pre_cleaned_table, table.subtables[1].pre_cleaned_table.tolist())
        self.assertListEqual(category_table, table.subtables[1].category_table)

        pre_cleaned_table = [['Material', 'Tc'], ['TiO2', '1.1'], ['TiO3', '1.2'], ['TiO4', '1.3'], ['TiO5', '1.4'], ['TiO6', '1.5'], ['TiO7', '1.6'], ['TiO8', '1.7'], ['TiO9', '1.8'], ['TiO10', '1.9'], ['TiO11', '1.10'], ['TiO12', '1.11']]
        category_table = [['1.1', ['TiO2'], ['Tc']], ['1.2', ['TiO3'], ['Tc']], ['1.3', ['TiO4'], ['Tc']], ['1.4', ['TiO5'], ['Tc']], ['1.5', ['TiO6'], ['Tc']], ['1.6', ['TiO7'], ['Tc']], ['1.7', ['TiO8'], ['Tc']], ['1.8', ['TiO9'], ['Tc']], ['1.9', ['TiO10'], ['Tc']], ['1.10', ['TiO11'], ['Tc']], ['1.11', ['TiO12'], ['Tc']]]
        self.assertListEqual(pre_cleaned_table, table.subtables[2].pre_cleaned_table.tolist())
        self.assertListEqual(category_table, table.subtables[2].category_table)

    def test_default_config_1_transposed(self):
        """Three subtables are expected"""
        table = Table("./tests/data/te_06.csv")
        table.transpose()

        pre_cleaned_table = [['Material', 'Bi6Tl3', 'Sb2Tl7', 'Na2Pb5', 'Hg5Tl7', 'Au2Bi', 'CuS', 'VN', 'WC', 'W2C', 'MoC', 'Mo2C'], ['Tc', '6.5', '5.5', '7.2', '3.8', '1.84', '1.6', '1.3', '2.8', '2.05', '7.7', '2.4'], ['A', 'x', 'y', 'z', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
        category_table = [['6.5', ['Tc'], ['Bi6Tl3']], ['5.5', ['Tc'], ['Sb2Tl7']], ['7.2', ['Tc'], ['Na2Pb5']], ['3.8', ['Tc'], ['Hg5Tl7']], ['1.84', ['Tc'], ['Au2Bi']], ['1.6', ['Tc'], ['CuS']], ['1.3', ['Tc'], ['VN']], ['2.8', ['Tc'], ['WC']], ['2.05', ['Tc'], ['W2C']], ['7.7', ['Tc'], ['MoC']], ['2.4', ['Tc'], ['Mo2C']], ['x', ['A'], ['Bi6Tl3']], ['y', ['A'], ['Sb2Tl7']], ['z', ['A'], ['Na2Pb5']], ['x', ['A'], ['Hg5Tl7']], ['x', ['A'], ['Au2Bi']], ['x', ['A'], ['CuS']], ['x', ['A'], ['VN']], ['x', ['A'], ['WC']], ['x', ['A'], ['W2C']], ['x', ['A'], ['MoC']], ['x', ['A'], ['Mo2C']]]
        self.assertListEqual(pre_cleaned_table, table.subtables[0].pre_cleaned_table.tolist())
        self.assertListEqual(category_table, table.subtables[0].category_table)

        pre_cleaned_table = [['Material', 'TiN', 'TiC', 'TaC', 'NbC', 'ZrB', 'TaSi', 'PbS', 'Pb-As alloy', 'Pb-Sn-Bi', 'Pb-As-Bi', 'Pb-Bi-Sb'], ['Tc', '1.4', '1.1', '9.2', '10.1', '2.82', '4.2', '4.1', '8.4', '8.5', '9.0', '8.9'], ['A', 'y', 'x', 'x', 'a', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
        category_table = [['1.4', ['Tc'], ['TiN']], ['1.1', ['Tc'], ['TiC']], ['9.2', ['Tc'], ['TaC']], ['10.1', ['Tc'], ['NbC']], ['2.82', ['Tc'], ['ZrB']], ['4.2', ['Tc'], ['TaSi']], ['4.1', ['Tc'], ['PbS']], ['8.4', ['Tc'], ['Pb-As alloy']], ['8.5', ['Tc'], ['Pb-Sn-Bi']], ['9.0', ['Tc'], ['Pb-As-Bi']], ['8.9', ['Tc'], ['Pb-Bi-Sb']], ['y', ['A'], ['TiN']], ['x', ['A'], ['TiC']], ['x', ['A'], ['TaC']], ['a', ['A'], ['NbC']], ['x', ['A'], ['ZrB']], ['x', ['A'], ['TaSi']], ['x', ['A'], ['PbS']], ['x', ['A'], ['Pb-As alloy']], ['x', ['A'], ['Pb-Sn-Bi']], ['x', ['A'], ['Pb-As-Bi']], ['x', ['A'], ['Pb-Bi-Sb']]]
        self.assertListEqual(pre_cleaned_table, table.subtables[1].pre_cleaned_table.tolist())
        self.assertListEqual(category_table, table.subtables[1].category_table)

        pre_cleaned_table = [['Material', 'TiO2', 'TiO3', 'TiO4', 'TiO5', 'TiO6', 'TiO7', 'TiO8', 'TiO9', 'TiO10', 'TiO11', 'TiO12'], ['Tc', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '1.10', '1.11']]
        category_table = [['1.1', ['Tc'], ['TiO2']], ['1.2', ['Tc'], ['TiO3']], ['1.3', ['Tc'], ['TiO4']], ['1.4', ['Tc'], ['TiO5']], ['1.5', ['Tc'], ['TiO6']], ['1.6', ['Tc'], ['TiO7']], ['1.7', ['Tc'], ['TiO8']], ['1.8', ['Tc'], ['TiO9']], ['1.9', ['Tc'], ['TiO10']], ['1.10', ['Tc'], ['TiO11']], ['1.11', ['Tc'], ['TiO12']]]
        self.assertListEqual(pre_cleaned_table, table.subtables[2].pre_cleaned_table.tolist())
        self.assertListEqual(category_table, table.subtables[2].category_table)

    def test_default_config_2(self):
        """No subtables are expected"""
        table = Table("./tests/data/te_07.csv")
        self.assertTrue(not table.subtables)


if __name__ == '__main__':
    unittest.main()