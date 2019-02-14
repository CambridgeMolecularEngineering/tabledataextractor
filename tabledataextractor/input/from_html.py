# -*- coding: utf-8 -*-
"""
Reads an html formatted table.
"""


import numpy as np
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.ie.options import Options as IeOptions
import copy
import logging
from tabledataextractor.exceptions import InputError

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)


def makearray(html_table):
    """
    Creates a numpy array from an html file, taking rowspan and colspan into account.

    Modified from:
        John Ricco, https://johnricco.github.io/2017/04/04/python-html/, *Using Python to scrape HTML tables with merged cells*

    Added functionality for duplicating cell content for cells with rowspan/colspan.
    The table has to be n*m, rectangular, with the same number of columns in every row.
    """
    n_cols = 0
    n_rows = 0

    for row in html_table.findAll("tr"):
        col_tags = row.find_all(["td", "th"])
        if len(col_tags) > 0:
            n_rows += 1
            if len(col_tags) > n_cols:
                n_cols = len(col_tags)

    # according to numpy documentation fill_value should be of type Union[int, float, complex]
    # however, 'str' works just fine
    array = np.full((n_rows,n_cols), fill_value="", dtype='<U60')

    # list to store rowspan values
    skip_index = [0 for i in range(0, n_cols)]

    # iterating over each row in the table
    row_counter = 0
    for row in html_table.findAll("tr"):

        # skip row if it's empty
        if len(row.find_all(["td", "th"])) == 0:
            continue

        else:

            # get all the cells containing data in this row
            columns = row.find_all(["td", "th"])
            col_dim = []
            row_dim = []
            col_dim_counter = -1
            row_dim_counter = -1
            col_counter = -1
            this_skip_index = copy.deepcopy(skip_index)

            for col in columns:

                # determine all cell dimensions
                colspan = col.get("colspan")
                if not colspan:
                    col_dim.append(1)
                else:
                    col_dim.append(int(colspan))
                col_dim_counter += 1

                rowspan = col.get("rowspan")
                if not rowspan:
                    row_dim.append(1)
                else:
                    row_dim.append(int(rowspan))
                row_dim_counter += 1

                # adjust column counter
                if col_counter == -1:
                    col_counter = 0
                else:
                    col_counter = col_counter + col_dim[col_dim_counter - 1]

                while skip_index[col_counter] > 0:
                    col_counter += 1

                # get cell contents
                cell_data = col.get_text()

                # insert data into cell
                array[row_counter, col_counter] = cell_data

                # Insert data into neighbouring rowspan/colspan cells
                if colspan:
                    for spanned_col in range(col_counter+1, col_counter + int(colspan)):
                        array[row_counter, spanned_col] = cell_data
                if rowspan:
                    for spanned_row in range(row_counter+1, row_counter + int(rowspan)):
                        array[spanned_row, col_counter] = cell_data

                #record column skipping index
                if row_dim[row_dim_counter] > 1:
                    this_skip_index[col_counter] = row_dim[row_dim_counter]

        # adjust row counter
        row_counter += 1

        # adjust column skipping index
        skip_index = [i - 1 if i > 0 else i for i in this_skip_index]

    return array


def read_file(file_path,table_number=1):
    """Method used to read an .html file and return a numpy array"""
    file = open(file_path, encoding='UTF-8')
    html_soup = BeautifulSoup(file, features='lxml')
    file.close()
    html_table = html_soup.find_all("table")[table_number-1]
    array = makearray(html_table)
    return array


def configure_selenium(browser='Firefox'):
    if browser == 'Firefox':
        options = FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options, executable_path=r'C:\Users\juras\System\geckodriver\geckodriver.exe')
        return driver
    else:
        return None


def read_url(url, table_number=1):
    """
    Reads in a table from an URL and returns a numpy array.

    :param url: Url of the page where the table is located
    :type url: str
    :param table_number: Number of Table on the web page.
    :type table_number: int
    """

    if not isinstance(table_number, int):
        msg = 'Table number is not valid.'
        log.critical(msg)
        raise TypeError(msg)

    # first try the requests package, if it fails do the selenium, which is much slower
    try:
        html_file = requests.get(url)
        html_soup = BeautifulSoup(html_file.text, features='lxml')
        html_table = html_soup.find_all("table")[table_number - 1]
        array = makearray(html_table)
        log.info("Package 'requests' was used.")
        return array
    except Exception:
        driver = configure_selenium()
        driver.get(url)
        html_file = driver.page_source
        html_soup = BeautifulSoup(html_file, features='lxml')
        try:
            html_table = html_soup.find_all("table")[table_number-1]
        except IndexError:
            raise InputError("table_number={} is out of range".format(table_number))
        else:
            array = makearray(html_table)
            log.info("Package 'selenium' was used.")
            return array
