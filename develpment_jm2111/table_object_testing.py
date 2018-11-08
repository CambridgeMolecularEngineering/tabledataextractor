from tabledataextractor import Table
from pprint import pprint

data_path = 'C:\\Users\\juras\\OneDrive - University Of Cambridge\\Projects\\AmorphousDatabase\\TableDataExtractor\\develpment_jm2111\\data\\'

url = 'https://link.springer.com/article/10.1007%2Fs10853-012-6439-6'

#url = 'agkhkhasdkgh'

# table = Table(url,2)
# table.print()
# table.to_csv(data_path+'J_Mat_Sci_2012_2.csv')
# print("'{}'".format(table.raw_table[3,3]))

# table = Table(data_path+'table_example1.csv')
# table.print()


test = [['Test','a','b','c','d'],
        ['A','1','2','3','4'],
        ['B','5','6','7','8']]

print(type(test))
table = Table(test)
table.print()

pprint(test)


