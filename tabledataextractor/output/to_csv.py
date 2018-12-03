# -*- coding: utf-8 -*-
"""
Outputs the table to cvs.
"""

import logging
import numpy as np
import os

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def write_to_csv(table, file_path):
    """
    Writes a numpy array table to a .csv file
    Overrides existing files.

    :param file_path: Output location
    :type file_path: str
    :return:
    """
    if os.path.exists(file_path):
        log.info("File: {} overwritten.".format(file_path))
    np.savetxt(file_path,table,delimiter=',',fmt='%-s', newline='\n', header='', footer='', comments='# ')
