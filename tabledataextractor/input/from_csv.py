# -*- coding: utf-8 -*-
"""
tabledataextractor.input.from_csv.py

Reads a csv formatted table.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""


import numpy as np
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def read(file_path):
    array = np.genfromtxt(file_path,delimiter=',',dtype=str, invalid_raise=False)
    return array

