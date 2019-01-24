.. TableDataExtractor documentation master file, created by
   sphinx-quickstart on Thu Nov  8 14:26:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TableDataExtractor!
==============================================

Usage::

   from tabledataextractor import Table
   table = Table('https://link.springer.com/article/10.1007%2Fs10853-012-6439-6',3)
   print(table)

::

                            Ti–O          Ti–Ti1     Ti–Ti2     O–O
    96-Atom model I         1.92          3.08       3.48       2.85
    96-Atom model II        1.91          3.07       3.53       2.83
    192-Atom model          1.94          3.13       3.59       2.74
    RMC + Expt. [4]         1.96          3.00       3.55       2.67
    Rutile (this study)     1.97, 2.00    2.99       3.60       2.56, 2.80
    Rutile (Expt. [28])     1.95, 1.98    2.96       3.57       2.53, 2.78
    Anatase (this study)    1.96, 2.00    3.07       3.83       2.49, 2.82
    Anatase (Expt. [28])    1.94, 1.96    3.03       3.78       2.45, 2.80


    StubHeader  ColHeader  ColHeader  ColHeader  ColHeader
    RowHeader   Data       Data       Data       Data
    RowHeader   Data       Data       Data       Data
    RowHeader   Data       Data       Data       Data
    RowHeader   Data       Data       Data       Data
    RowHeader   Data       Data       Data       Data
    RowHeader   Data       Data       Data       Data
    RowHeader   Data       Data       Data       Data
    RowHeader   Data       Data       Data       Data


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   table_object
   cell_parser
   input
   output
   examples
   external





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
