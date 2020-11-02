import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler


class Features:
    def __init__(self):
        pass

    def unify_data(self):
        isd_data = pd.read_csv('data/interim/SBGR_isd_data.csv')
        inmet_data = pd.read_csv(
            'data/interim/SAO PAULO - MIRANTE_inmet_data.csv')

        isd_data['DATE'] = pd.to_datetime(isd_data['DATE'])
        inmet_data['DATE'] = pd.to_datetime(inmet_data['DATE'])

        data = isd_data.merge(inmet_data, on='DATE', how='left')
        data.to_csv('data/interim/unified_data.csv', index=False)

    def remove_outliers(self):
        data = pd.read_csv('data/interim/unified_data.csv')
        variables = ['precipitation', 'radiation',
                     'temperature', 'dew', 'slp', 'rh']
        data[variables] = (data[variables].ffill() +
                           data[variables].bfill()) / 2
        data[variables] = np.around(data[variables], decimals=1)
        data.to_csv('data/interim/unified_data.csv', index=False)

    def rolling_windows(self):
        data = pd.read_csv('data/interim/unified_data.csv')
        variables = ['precipitation', 'radiation']
        for variable in variables:
            for hours in range(3, 19, 3):
                column_name = f'{variable}_{hours}'
                data[column_name] = abs(np.around(data[variable].rolling(
                    window=hours, min_periods=1).sum(), decimals=1))
        data.to_csv('data/interim/unified_data_rolling.csv', index=False)

    def extract_fog(self):
        data = pd.read_csv('data/interim/unified_data_rolling.csv')
        data['fog'] = np.where(data['phenomenon'] == 'FG', 1, 0)
        data.drop('phenomenon', axis=1, inplace=True)
        data.to_csv('data/interim/fog.csv', index=False)

    def normalize_data(self):
        data = pd.read_csv('data/interim/fog.csv', index_col='DATE')
        scaler = MinMaxScaler()
        columns = data.columns
        data = pd.DataFrame(scaler.fit_transform(data), columns=columns)
        data.to_csv('data/processed/fog_min_max_scaled.csv', index=False)


