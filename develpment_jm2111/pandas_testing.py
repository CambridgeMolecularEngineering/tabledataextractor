import pandas as pd
import numpy as np
from pandas import MultiIndex
from sqlalchemy import create_engine


columns = ['Sample', 'NAsAs', 'Atomic pair']
rows = [['Ca50Mg20Cu25Zn5', '8.2 (2)', 'Ca-Ca'], ['TiO2', '8.4(±0.5)', 'Ca-Mg'], ['Ca50Mg20Cu25Zn5', '8.4', 'Ca-Cu']]
compounds = list(zip(rows[0], rows[1], rows[2]))[0]
data = [columns] + rows

print("rows:     ", rows)
print("compounds:", compounds)
print("data:     ", data, "\n")

# if the whole table is passed into the DF as data, there is no distinction between the cells
df = pd.DataFrame(data=data)
print(df)
print("Index: ", df.index, "\n")

# Data as it should be, the compounds in the first are indexes
data_columns = ['NAsAs', 'Atomic pair']
data_rows = [['8.2 (2)', 'Ca-Ca'], ['8.4(±0.5)', 'Ca-Mg'], ['8.4', 'Ca-Cu']]
df = pd.DataFrame(columns=data_columns, data=data_rows, index=compounds)
df.index.name = columns[0]
print(df, "\n")

# More complicated table, with MultiIndex
data_rows = [['4.64', '2.99', '0.305', '3.83', '9.62', '0.208'],
             ['4.67', '2.97', '0.305', '3.80', '9.67', '0.207'],
             ['4.63', '2.98', '0.305', '-', '-', '-'],
             ['-', '-', '-', '3.76', '9.85', '0.202'],
             ['4.594', '2.958', '0.305', '3.785', '9.514', '0.207']]
index_col: MultiIndex = pd.MultiIndex.from_tuples(
    [('Rutile', 'a = b (Å)'), ('Rutile', 'c (Å)'), ('Rutile', 'u'), ('Anatase', 'a = b (Å)'), ('Anatase', 'c (Å)'),
     ('Anatase', 'u')])
index_row = pd.MultiIndex.from_tuples(
    [('Computational', 'This study'), ('Computational', 'GGA'), ('Computational', 'GGA'), ('Computational', 'HF'),
     ('Experimental', 'Expt.')])
data_columns = ['a = b (Å)', 'c (Å)', 'u', 'a = b (Å)', 'c (Å)', 'u']
df = pd.DataFrame(columns=index_col, data=data_rows, index=index_row)
print(df, "\n")

# More complicated table, with difficult MultiIndex
data_rows = [['1.4', '18.3', '62', '18.3', '', '5.96'],
             ['', '25', '50', '25', '', '6.00'],
             ['9', '43', '48', '', '', '5.40'],
             ['2.7', '27.4', '47.9', '19.2', '2.7', '5.82']]
index_row = ['CMPD','CPMD + VASP','DFTB','DFTB + VASP']
index_col = pd.MultiIndex.from_tuples([('TiOx fraction (%)','TiO4'),('TiOx fraction (%)','TiO5'),('TiOx fraction (%)','TiO6'),('TiOx fraction (%)','TiO7'),('TiOx fraction (%)','TiO8'),('Mean CN','')])
df = pd.DataFrame(columns=index_col, data=data_rows, index=index_row)
df.index.name = 'Simulation approach'
df.replace('',np.nan,inplace=True)  # interpretation of empty cells
df = df.astype(float)  # convert all data to float
print(df, "\n")

# Creating DataFrames automatically from html --> doesn't really work with MultiIndex
df = pd.read_html('https://link.springer.com/article/10.1007%2Fs10853-012-6439-6', index_col=0, na_values='–')[1]
print(df.to_string(), "\n")

# Creating DataFrames automatically from csv --> works with MultiIndex
df = pd.read_csv('./data/table_example.csv', delimiter=',', header=[0, 1], na_values='–',index_col=[0,1])
print(df, "\n")

# A complicated example from Embley et. Al., Figure 11
# once the headers and data is separated the indexing is automatic:
df = pd.read_csv('./data/table_example2.csv', delimiter=',', header=[0, 1, 2])
print(df.to_string(), "\n")

# TODO Convert above DataFrame into database that can be queried -> into a category table
# TODO Try the main primary Embley et Al table --> try the indexing from the "raw" table, without the factorization, if first todo works

# engine = create_engine('sqlite:///:memory:')
# df.to_sql('test', engine)





























