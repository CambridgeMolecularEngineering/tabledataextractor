from tabledataextractor.input import from_html
from tabledataextractor.output.print import print_table
from tabledataextractor.output.to_csv import write_to_csv
from bs4 import BeautifulSoup
from pprint import pprint

data_path = 'C:\\Users\\juras\\OneDrive - University Of Cambridge\\Projects\\AmorphousDatabase\\TableDataExtractor\\develpment_jm2111\\data\\'

url='https://www.sciencedirect.com/science/article/pii/S0272884214001692?via%3Dihub'
table = from_html.read_url(url)

#pprint(table)

print_table(table)

#write_to_csv(table,data_path+'one_column_example.csv')