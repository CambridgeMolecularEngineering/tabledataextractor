# -*- coding: utf-8 -*-
"""
tabledataextractor.input.from_list.py

Reads in a Python list.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""

import numpy as np
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def read(list):
    """Creates a numpy array from a list. Works if rows are of different length"""
    length = len(sorted(list,key=len, reverse=True)[0])
    array = np.array([l+[None]*(length-len(l)) for l in list],dtype=str)
    return array