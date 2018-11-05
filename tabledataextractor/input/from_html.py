# -*- coding: utf-8 -*-
"""
tabledataextractor.input.from_html.py

Reads an html formatted table.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""


import numpy as np
import re
from bs4 import BeautifulSoup
import logging


def makelist(html_table):
    """Creates a python list from an html file"""
    list = []
    rows = html_table.findAll('tr')
    for row in rows:
        list.append([])
        # look for rows as well as header rows
        cols = row.findAll(re.compile('(td)|(th)'))
        for col in cols:
            strings = [str(s) for s in col.findAll(text=True)]
            text = ''.join(strings)
            list[-1].append(text)
    return list

def makearray(list):
    length = len(sorted(list,key=len, reverse=True)[0])
    array = np.array([l+[None]*(length-len(l)) for l in list],dtype=str)
    return array

def read(file_path):
    file = open(file_path, encoding='UTF-8')
    html_table = BeautifulSoup(file, features='lxml')
    list = makelist(html_table)
    array = makearray(list)
    return array

