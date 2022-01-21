import pandas as pd

data=pd.read_csv("classification_ids2.csv")
print(data)
kkeys={"red":"Cases increasing","green":"Cases under control","yellow":"Cases almost under control"}
data['Change1']=data['Change'].map(kkeys)
print(data)
data.to_csv("classification_ids3.csv")
