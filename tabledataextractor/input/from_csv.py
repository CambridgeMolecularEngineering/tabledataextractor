# -*- coding: utf-8 -*-
"""
tabledataextractor.input.from_csv
===================================
Reads a csv formatted table from file.

The file has to be 'utf-8' encoded.
"""


import numpy as np
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def read(file_path):
    array = np.genfromtxt(file_path, delimiter=',', dtype='<U60', invalid_raise=False, encoding='utf-8')
    return array

