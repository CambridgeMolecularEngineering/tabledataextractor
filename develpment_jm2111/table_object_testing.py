from tabledataextractor import Table

data_path = 'C:\\Users\\juras\\OneDrive - University Of Cambridge\\Projects\\' \
            'AmorphousDatabase\\TableDataExtractor\\develpment_jm2111\\data\\'

url = 'https://link.springer.com/article/10.1007%2Fs10853-012-6439-6'
#url = 'https://www.sciencedirect.com/science/article/pii/S0022309317305732'
#url='https://www.sciencedirect.com/science/article/pii/S0272884214001692?via%3Dihub'

table = Table(url,1)
table.print()
#table.to_csv(data_path+'J_Mat_Sci_2012_2.csv')



