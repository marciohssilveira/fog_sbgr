import pandas as pd
import numpy as np

data = pd.read_csv('data/interim/unified_data.csv')


# Create column for accumulated precipitation in the last 18 hours
# Create column for accumulated precipitation in the last 12 hours
# Create column for accumulated precipitation in the last 6 hours
# Create column for accumulated precipitation in the last 3 hours
# Create column for accumulated radiation in the last 18 hours

def rolling_column(data, variable, hours):
    column_name = f'{variable}_{hours}'
    data[column_name] = np.around(data[variable].rolling(window=hours, min_periods=1).sum(), decimals=1)

for i in range(3, 19, 3):
    rolling_column(data, 'precipitation', i)

rolling_column(data, 'radiation', 18)