# -*- coding: utf-8 -*-
"""
Reads a `csv` formatted table from file. The file has to be 'utf-8' encoded.
"""

import numpy as np
import logging
import csv

log = logging.getLogger(__name__)


def read(file_path):
    """
    :param file_path: Path to `.csv` input file
    :type file_path: str
    :return: numpy.ndarray
    """

    with open(file_path, 'r', encoding='utf-8') as f:
        array = [elem for elem in list(csv.reader(f)) if elem]
        n = len(array[0])
        array = [x for x in array if len(x) == n]  # Only include rows with data for every column
        array = np.asarray(array, dtype='<U60')
    return array

