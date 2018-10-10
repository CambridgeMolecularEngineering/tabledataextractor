# -*- coding: utf-8 -*-
"""
tabledataextractor.table.table

Raw, processed and final table objects.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""

import logging
from tabledataextractor.input import from_csv
from tabledataextractor.output.print import print_table

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


class Table():

    def __init__(self,file_path):
        log.info('Initialization of table: "{}"'.format(file_path))
        self.file_path = file_path
        self.raw_table = from_csv.read(file_path)

    def print(self):
        log.info("Printing of table: {}".format(self.file_path))
        print_table(self.raw_table)



