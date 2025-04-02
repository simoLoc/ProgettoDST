import pandas as pd

dataset = pd.read_csv("dataset/dataset_7k_completopulito.csv", sep = ";", encoding='ISO-8859-1')

# print(dataset.head())

# Rimozione delle righe duplicate
df = dataset.drop_duplicates()

print(len(df))

print(df.info())

# Rimozione delle righe con i valori 'non presente'
df = df[~df.apply(lambda row: row.astype(str).str.contains("non presente")).any(axis=1)]

print(len(df))

# Rimozione delle righe con valori di channel e title nulli
df = df.dropna(subset=['trigger_channel', 'trigger_title', 'action_channel', 'action_title'])

print(len(df))

df.to_csv("dataset/dataset_6k.csv", index=False, sep=";", encoding='ISO-8859-1')