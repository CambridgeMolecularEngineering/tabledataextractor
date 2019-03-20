# -*- coding: utf-8 -*-
"""
Inputs from python list object.
"""

import numpy as np
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


def read(plist):
    """
    Creates a numpy array from a Python list. Works if rows are of different length.

    :param plist: Input List
    :type plist: list
    :return: numpy.ndarray
    """
    length = len(sorted(plist, key=len, reverse=True)[0])
    array = np.array([l+[None]*(length-len(l)) for l in plist], dtype='<U60')
    return array

