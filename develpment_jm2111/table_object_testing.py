from tabledataextractor import Table

data_path = 'C:\\Users\\juras\\OneDrive - University Of Cambridge\\Projects\\AmorphousDatabase\\TableDataExtractor\\develpment_jm2111\\data\\'

# table = Table(data_path+'table_example.csv')
# print("Table 1")
# print("=======")
# table.print()
#
# table = Table(data_path+'table_example2.csv')
# print("Table 2")
# print("=======")
# table.print()
#
# table = Table(data_path+'table_example3.csv')
# print("Table 3")
# print("=======")
# table.print()
#
# table = Table(data_path+'table_example4.csv')
# print("Table 4")
# print("=======")
# table.print()
#
# table = Table(data_path+'table_example5.csv')
# print("Table 5")
# print("=======")
# table.print()
#
# table = Table(data_path+'table_example6.csv')
# print("Table 6")
# print("=======")
# table.print()

# table = Table(data_path+'table_official_development_assistance.csv')
# table.print()

# table = Table(data_path+'table_example1.csv')
# table.print()
#
# table = Table(data_path+'development_table.csv')
# table.print()

#
# table = Table(data_path+'table_example2.csv')
# table.print()
#
# for i in range(3,7,1):
#     print(i)

# data_path = 'C:\\Users\\juras\\OneDrive - University Of Cambridge\\Projects\\AmorphousDatabase\\TableDataExtractor\\tests\\data\\'
# table = Table(data_path+'table_example7.csv')
# table.print()
# print(table.labels.tolist())

table = Table(data_path+'table_example.html')
table.print()
print(table.raw_table_empty,"\n")
print(table.pre_cleaned_table_empty)
