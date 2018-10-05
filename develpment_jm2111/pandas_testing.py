import pandas as pd


columns = ['Sample', 'NAsAs', 'Atomic pair']
rows = [['Ca50Mg20Cu25Zn5', '8.2 (2)', 'Ca-Ca'],['TiO2', '8.4(±0.5)', 'Ca-Mg'],['Ca50Mg20Cu25Zn5', '8.4', 'Ca-Cu']]
compounds = list(zip(rows[0],rows[1],rows[2]))[0]
data = [columns] + rows

print("rows:     ", rows)
print("compounds:", compounds)
print("data:     ", data,"\n")

# if the whole table is passed into the DF as data, there is no distinction between the cells
df = pd.DataFrame(data=data)
print(df)
print("Index: ", df.index, "\n")

# TODO Input the data as it should be, naming the indexes, the compounds in the first column should be indexes
df = pd.DataFrame(columns=columns,data=rows)
print(df)
print("Index: ", df.index, "\n")