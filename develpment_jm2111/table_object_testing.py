from tabledataextractor import Table

data_path = 'C:\\Users\\juras\\OneDrive - University Of Cambridge\\Projects\\' \
           'AmorphousDatabase\\TableDataExtractor\\develpment_jm2111\\data\\'

#url = 'https://link.springer.com/article/10.1007%2Fs10853-012-6439-6'
#url = 'https://www.sciencedirect.com/science/article/pii/S0022309317305732'

# Callum's paper, table fails because the data points in the table are not uniquely indexed,
# that wouldn't necessarily be a problem, but only one column is left after proper indexing
#url='https://www.sciencedirect.com/science/article/pii/S0272884214001692?via%3Dihub'

#url = 'https://journals.aps.org/prb/abstract/10.1103/PhysRevB.86.064201#fulltext'
#url = 'https://journals.aps.org/prb/abstract/10.1103/PhysRevB.90.094204#fulltext'
#url = 'https://iopscience.iop.org/article/10.1088/0022-3727/46/32/325302/meta'

# print("Situation where prefixing would potentially destroy the structure:\n")
# table = Table(data_path + 'table_example4_2.csv')
# print(repr(table))
#
# print("Situation where prefixing would be useful:\n")
table = Table(data_path + 'table_example4.csv')
print(repr(table))
#
# table = Table(data_path + 'table_example1.csv')
# print(repr(table))
#
# table = Table(data_path + 'table_example2.csv')
# print(repr(table))
#
# # table = Table(data_path + 'table_example3.csv')
# # print(repr(table))

# table = Table(data_path + 'table_example5.csv')
# print(repr(table))

# table = Table(data_path + 'table_example_11.csv')
# print(repr(table))

# print(table.pre_cleaned_table, "\n")
# print(table.labels)


#table.print()
#table.to_csv(data_path+'J_Mat_Sci_2012_2.csv')



