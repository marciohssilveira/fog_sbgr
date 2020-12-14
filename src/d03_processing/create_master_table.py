import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler


class Features:
    def __init__(self, data_isd, data_inmet):
        self.data_isd = data_isd
        self.data_inmet = data_inmet

    def create(self):
        data = self.unify_data(self.data_isd, self.data_inmet)
        data = self.remove_outliers(data)
        data.to_csv('data/02_intermediate/consolidated.csv', index=True)
        data = self.rolling_windows(data)
        data = self.normalize_data(data)
        data.to_csv('data/03_processed/min_max_scaled.csv', index=False)
        return data

    def unify_data(self, data_isd, data_inmet):
        data_isd.index = pd.to_datetime(data_isd.index)
        data_inmet.index = pd.to_datetime(data_inmet.index)
        unified_data = data_isd.join(data_inmet)
        return unified_data

    def remove_outliers(self, data):
        """
        Remove outliers only on selected columns based on how the data is structured
        """
        variables = ['precipitation', 'radiation',
                     'temperature', 'dew', 'slp', 'rh']
        for variable in variables:
            data[variable] = (pd.to_numeric(data[variable]).ffill() + pd.to_numeric(data[variable]).bfill()) / 2
            data[variable] = np.around(data[variable], decimals=1)
        return data

    def rolling_windows(self, data):
        data.index = pd.to_datetime(data.index)
        variables = ['precipitation', 'radiation']
        for variable in variables:
            for hours in range(3, 19, 3):
                column_name = f'{variable}_{hours}'
                data[column_name] = abs(np.around(data[variable].rolling(
                    window=hours, min_periods=1).sum(), decimals=1))
        return data

    # def extract_fog(self, data):
    #     data['fog'] = np.where(data['phenomenon'] == 'FG', 1, 0)
    #     data.drop('phenomenon', axis=1, inplace=True)
    #     return data

    def normalize_data(self, data):
        data.drop('phenomenon', axis=1, inplace=True)
        columns = data.columns
        transformed_data = MinMaxScaler().fit_transform(data)
        transformed_data = pd.DataFrame(transformed_data, columns=columns)
        return transformed_data
