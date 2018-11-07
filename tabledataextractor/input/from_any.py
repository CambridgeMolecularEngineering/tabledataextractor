# -*- coding: utf-8 -*-
"""
tabledataextractor.input.from_any.py

Analyzes the input and calls the appropriate input module.

jm2111@cam.ac.uk
~~~~~~~~~~~~~~~~~
"""

from django.core.validators import URLValidator
import os.path
from tabledataextractor.input import from_html
from tabledataextractor.input import from_csv
from tabledataextractor.input import from_list
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def url(name):
    try:
        URLValidator()(name)
        return True
    except:
        return False

def html(name):
    if os.path.isfile(name) and name.endswith(".html"):
        return True
    else:
        return False

def csv(name):
    if os.path.isfile(name) and name.endswith(".csv"):
        return True
    else:
        return False


def create_table(name_key, table_number):
    """
    Checks the input and calls the appropriate modules.
    Returns a numpy array with the raw table
    :param input: Any
    :return:
    """

    if isinstance(name_key,list):
        log.info("Input is list type.")
        return from_list.read(name_key)

    if url(name_key):
        log.info("Url: {}".format(name_key))
        return from_html.read_url(name_key, table_number)

    if html(name_key):
        log.info("HTML File: {}".format(name_key))
        return from_html.read_file(name_key, table_number)

    if csv(name_key):
        log.info("CSV File: {}".format(name_key))
        return from_csv.read(name_key)


