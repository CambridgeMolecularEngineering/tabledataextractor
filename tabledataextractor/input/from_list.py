# -*- coding: utf-8 -*-
"""
tabledataextractor.input.from_list
=====================================
"""

import numpy as np
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def read(plist):
    """Creates a numpy array from a list. Works if rows are of different length"""
    length = len(sorted(plist,key=len, reverse=True)[0])
    array = np.array([l+[None]*(length-len(l)) for l in plist],dtype='<U60')
    return array