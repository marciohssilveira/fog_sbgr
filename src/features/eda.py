import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


fog = pd.read_csv('./data/labeled_fog.csv', index_col='DATE')
fog.index = pd.to_datetime(fog.index)

hourly_count = fog.pivot_table(values='temperature', index=fog.index.hour, aggfunc=np.count_nonzero)
monthly_count = fog.pivot_table(values='temperature', index=fog.index.month, aggfunc=np.count_nonzero)
yearly_count = fog.pivot_table(values='temperature', index=fog.index.year, aggfunc=np.count_nonzero)

hourly_count_label = fog.pivot_table(values='temperature', index=fog.index.hour, columns='label', aggfunc=np.count_nonzero)
monthly_count_label = fog.pivot_table(values='temperature', index=fog.index.month, columns='label', aggfunc=np.count_nonzero)
yearly_count_label = fog.pivot_table(values='temperature', index=fog.index.year, columns='label', aggfunc=np.count_nonzero)

hourly_mean_temperature = fog.pivot_table(values='temperature', index=fog.index.hour, columns='label', aggfunc=np.mean)
hourly_mean_visibility = fog.pivot_table(values='visibility', index=fog.index.hour, columns='label', aggfunc=np.mean)
