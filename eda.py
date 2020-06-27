import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


fog = pd.read_csv('./data/labeled_fog.csv')

print(fog.info())

fog['DATE'] = pd.to_datetime(fog['DATE'])

fog.groupby(pd.Grouper(key='DATE', freq='h'))['temperature'].mean()