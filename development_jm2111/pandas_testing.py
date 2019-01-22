import pandas as pd
import numpy as np
from pandas import MultiIndex

# Conversion of DataFrame into Category Table, brute force
#index = df.index      # these are the levels and labels of the index
#columns = df.columns  # these are the levels and labels of the columns
def find_multiindex_level(row_number,column_number,df):
    result_index = []
    if hasattr(df.index,'labels'):
        for i,labels in enumerate(df.index.labels):
            result_index.append(df.index.levels[i][labels[row_number]])
    else:
        result_index.append(df.index[row_number])
    result_column = []
    if hasattr(df.columns,'labels'):
        for i,labels in enumerate(df.columns.labels):
            result_column.append(df.columns.levels[i][labels[column_number]])
    else:
        result_column.append(df.columns[column_number])
    return result_index,result_column

def print_category_table(df):
    values = df.values  # data is converted to numpy array
    print("{:11s} {:10s} {:36s} {:20s}".format("Cell_ID","Data","Row Categories","Column Categories"))
    for i,row in enumerate(values):
        for j,cell in enumerate(row):
            categories = find_multiindex_level(i,j,df)
            print("{:3} {:3} {:15}   {:35}  {:40}".format(i,j,str(cell),''.join(str(categories[0])),''.join(str(categories[1]))))

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
print_category_table(df); print("\n")
print("Index: ", df.index, "\n")

# Data as it should be, the compounds in the first are indexes
data_columns = ['NAsAs', 'Atomic pair']
data_rows = [['8.2 (2)', 'Ca-Ca'], ['8.4(±0.5)', 'Ca-Mg'], ['8.4', 'Ca-Cu']]
df = pd.DataFrame(columns=data_columns, data=data_rows, index=compounds)
df.index.name = columns[0]
print(df, "\n")
print_category_table(df); print("\n")

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
print_category_table(df); print("\n")

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
print_category_table(df); print("\n")

# Creating DataFrames automatically from html --> doesn't really work with MultiIndex
df = pd.read_html('https://link.springer.com/article/10.1007%2Fs10853-012-6439-6', index_col=0, na_values='–')[1]
print(df.to_string(), "\n")
print_category_table(df); print("\n")

# Creating DataFrames automatically from csv --> works with MultiIndex
df = pd.read_csv('./data/table_example.csv', delimiter=',', header=[0, 1], na_values='–',index_col=[0,1])
print(df, "\n")
print_category_table(df); print("\n")

# Main primary Embley et Al table, the name 'Denmark' has been purposefully removed
df = pd.read_csv('./data/table_example3.csv', delimiter=',', header=[0,1,2], na_values='',index_col=[0])
print(df.to_string(), "\n")
print_category_table(df); print("\n")

# Test how labels are duplicated, based on Fig. 9 in Embley et. Al.
# they ARE appended by an integer, but not prefixed by the stuff we want, see next example
df = pd.read_csv('./data/table_example4.csv', delimiter=',', header=[0], na_values='',index_col=[0])
print(df.to_string(), "\n")
print_category_table(df); print("\n")

# if we add an aditional line with the closest unique label, everything is prefixed correctly
# we can choose which one of those examples we want
df = pd.read_csv('./data/table_example5.csv', delimiter=',', header=[0,1], na_values='',index_col=[0])
print(df.to_string(), "\n")
print_category_table(df); print("\n")

# A complicated example from Embley et. Al., Figure 11
# once the headers and data is separated the indexing is automatic:
df = pd.read_csv('./data/table_example2.csv', delimiter=',', header=[0, 1, 2])
print(df.to_string(), "\n")
print_category_table(df); print("\n")


# Two tables in one will not work, not even if indexes are specified separately, because the data will not
# be separate
# Two tables need to be created from one
df = pd.read_csv('./data/table_example6.csv', delimiter=',', index_col=[0],usecols=[0,1])
print(df.to_string(), "\n")
print_category_table(df); print("\n")
# when the second table is input, Pandas will still automatically add a suffix to the duplicate column labels
df = pd.read_csv('./data/table_example6.csv', delimiter=',', index_col=[0],usecols=[2,3])
print(df.to_string(), "\n")
print_category_table(df); print("\n")


# TODO Building a category table from the DataFrame, using loops over columns and row indexes, should be easier

# TODO Make the print_category_table() function output better formatting

































