# -*- coding: utf-8 -*-
"""
TableDataExtractor
Extracts and indexes data from tables.
Algorithm from David W. Embley et. Al., DOI: 10.1007/s10032-016-0259-1
jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""

import logging

__title__ = 'TableDataExtractor'
__version__ = '1.5.8'
__author__ = 'Juraj Mavračić'
__email__ = 'jm2111@cam.ac.uk'
__license__ = 'proprietary'  # ?
__copyright__ = 'Copyright 2018 Juraj Mavracic'

# log = logging.getLogger(__name__)
# log.addHandler(logging.NullHandler())

# all messages with effective level higher or equal to warning will be shown
# in every module/file set:
#     log = logging.getLogger(__name__)
#     log.setLevel(logging.DEBUG)
# to change the effective level of the module logger
logging.basicConfig(level=logging.WARNING, format='%(levelname)-10s in %(filename)-20s--> %(message)s', handlers=[logging.FileHandler("log.txt", mode='w')])

log = logging.getLogger(__name__)


from tabledataextractor.table.table import Table, TrivialTable

