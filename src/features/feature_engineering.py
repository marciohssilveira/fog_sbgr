import pandas as pd
import numpy as np

class Features:
    def __init__(self):
        pass

    def unify_data(self):
        isd_data = pd.read_csv('data/interim/SBGR_isd_data.csv')
        inmet_data = pd.read_csv('data/interim/SAO PAULO - MIRANTE_inmet_data.csv')

        isd_data['DATE'] = pd.to_datetime(isd_data['DATE'])
        inmet_data['DATE'] = pd.to_datetime(inmet_data['DATE'])

        data = isd_data.merge(inmet_data, on='DATE', how='left')

        data[['precipitation',
            'radiation']] = (data[['precipitation',
                                    'radiation']].ffill() + data[['precipitation',
                                                                'radiation']].bfill()) / 2
        data['precipitation'] = np.around(data['precipitation'])
        data['radiation'] = np.around(data['radiation'])

        data.to_csv('data/interim/unified_data.csv', index=False)

    def rolling_windows(self):
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