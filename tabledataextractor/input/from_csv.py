# -*- coding: utf-8 -*-
"""
Reads a `csv` formatted table from file. The file has to be 'utf-8' encoded.
"""

import numpy as np
import logging
import csv

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


def read(file_path):
    """
    :param file_path: Path to `.csv` input file
    :type file_path: str
    :return: numpy.ndarray
    """

    with open(file_path, 'r') as f:
        array = list(csv.reader(f))
        array = np.asarray(array, dtype='<U60')
    return array

