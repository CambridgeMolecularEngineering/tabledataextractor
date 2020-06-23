# -*- coding: utf-8 -*-
"""
Analyzes the input and calls the appropriate input module.
"""

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import os.path
from tabledataextractor.input import from_html
from tabledataextractor.input import from_csv
from tabledataextractor.input import from_list
import logging

log = logging.getLogger(__name__)


def url(name):
    """
    Returns `True` if input is `URL`.
    Uses ``django.core.validators.URLValidator``.

    :param name: Input string
    :type name: str
    """
    try:
        URLValidator()(name)
        return True
    except ValidationError:
        return False


def html(name):
    """
    Returns `True` if input is `html` file.

    :param name: Input string
    :type name: str
    """
    if os.path.isfile(name) and name.endswith(".html"):
        return True
    else:
        return False


def csv(name):
    """
    Returns `True` if input is `csv` file.

    :param name: Input string
    :type name: str
    """
    if os.path.isfile(name) and name.endswith(".csv"):
        return True
    else:
        return False


def create_table(name_key, table_number=1):
    """
    Checks the input and calls the appropriate modules for conversion.
    Returns a numpy array with the raw table.

    :param name_key: Path to `.html` or `.cvs` file, `URL` or `python list` that is used as input
    :type name_key: str | list
    :param table_number: Number of the table that we want to input if there are several at the given address/path
    :type table_number: int
    :return: table as numpy.array
    """

    if isinstance(name_key, list):
        log.info("Input is list type.")
        if len(name_key) > 0:
            return from_list.read(name_key)
        else:
            msg = 'Input is invalid. ' \
                  'Supported are: path to .html or .cvs file, URL or multidimensional python list object'
            log.critical(msg)
            raise TypeError(msg, str(name_key))

    elif url(name_key):
        log.info("Url: {}".format(name_key))
        return from_html.read_url(name_key, table_number)

    elif html(name_key):
        log.info("HTML File: {}".format(name_key))
        return from_html.read_file(name_key, table_number)

    elif csv(name_key):
        log.info("CSV File: {}".format(name_key))
        return from_csv.read(name_key)

    else:
        msg = 'Input is invalid. Supported are: path to .html or .cvs file, URL or multidimensional python list object'
        log.critical(msg)
        raise TypeError(msg, str(name_key))


