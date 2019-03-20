# -*- coding: utf-8 -*-
"""
Exceptions defined for TableDataExtractor.
"""


class TDEError(Exception):
    """
    Base class for exceptions in TableDataExtractor.
    """


class InputError(TDEError):
    """
    Exception raised for errors in the input.
    """
    def __init__(self, message):
        self.message = message


class MIPSError(TDEError):
    """
    Exception raised for failure of the main MIPS algorithm.
    Usually signals that the table is broken or not well structured.
    """
    def __init__(self, message):
        self.message = message

