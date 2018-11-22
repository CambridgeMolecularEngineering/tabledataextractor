from tabledataextractor import Table

# ======================================
# Random testing
# ======================================

# Callum's paper, table fails because the data points in the table are not uniquely indexed,
# that wouldn't necessarily be a problem, but only one column is left after proper indexing
# url='https://www.sciencedirect.com/science/article/pii/S0272884214001692?via%3Dihub'

# url = 'https://journals.aps.org/prb/abstract/10.1103/PhysRevB.86.064201#fulltext'
# url = 'https://journals.aps.org/prb/abstract/10.1103/PhysRevB.90.094204#fulltext'
# url = 'https://iopscience.iop.org/article/10.1088/0022-3727/46/32/325302/meta'

# ======================================
# Testing of duplicate label prefixing
# ======================================

data_path = 'C:\\Users\\juras\\OneDrive - University Of Cambridge\\Projects\\' \
           'AmorphousDatabase\\TableDataExtractor\\development_jm2111\\data\\'

table = Table(data_path + 'table_example.csv')
print(repr(table))

table = Table(data_path + 'table_example1.csv')
print(repr(table))

table = Table(data_path + 'table_example2.csv')
print(repr(table))

table = Table(data_path + 'table_example3.csv')
print(repr(table))

table = Table(data_path + 'table_example4.csv')
print(repr(table))

table = Table(data_path + 'table_example4_2.csv')
print(repr(table))

table = Table(data_path + 'table_example4_3.csv')
print(repr(table))

table = Table(data_path + 'table_example5.csv')
print(repr(table))

table = Table(data_path + 'table_example6.csv')
print(repr(table))

table = Table(data_path + 'table_example_8.html')
print(repr(table))

table = Table(data_path + 'table_example9.html')
print(repr(table))

table = Table(data_path + 'table_example_10.html')
print(repr(table))

table = Table(data_path + 'table_example_10.csv')
print(repr(table))

table = Table(data_path + 'table_example_11.csv')
print(repr(table))

table = Table(data_path + 'table_official_development_assistance.csv')
print(repr(table))



