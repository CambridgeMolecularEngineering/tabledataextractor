# -*- coding: utf-8 -*-
"""
TableDataExtractor
Extracts and standardizes data from tables.
Algorithm from David W. Embley et. Al., DOI: 10.1007/s10032-016-0259-1
jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""

import logging

__title__ = 'TableDataExtractor'
__version__ = '1.5.9'
__author__ = 'Juraj Mavračić'
__email__ = 'jm2111@cam.ac.uk'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2019 Juraj Mavracic'

# global logging set-up, change the logging level here for development
logging.basicConfig(level=logging.INFO, format='%(levelname)-10s in %(filename)-20s--> %(message)s', handlers=[logging.FileHandler("tde_log.txt", mode='w')])

from tabledataextractor.table.table import Table, TrivialTable

