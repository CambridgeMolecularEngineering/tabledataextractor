# -*- coding: utf-8 -*-
"""
tabledataextractor.input.from_csv
===================================
Reads a csv formatted table.
"""


import numpy as np
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def read(file_path):
    array = np.genfromtxt(file_path, delimiter=',', dtype='<U60', invalid_raise=False, encoding='bytes')
    return array

