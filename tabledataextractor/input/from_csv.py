# -*- coding: utf-8 -*-
"""
Reads a `csv` formatted table from file. The file has to be 'utf-8' encoded.
"""

import numpy as np
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


def read(file_path):
    """
    :param file_path: Path to `.csv` input file
    :type file_path: str
    :return: numpy.ndarray
    """
    array = np.genfromtxt(file_path, delimiter=',', dtype='<U60', invalid_raise=False, encoding='utf-8')
    return array

