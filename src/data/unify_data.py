
import pandas as pd

isd_data = pd.read_csv('data/interim/SBGR_isd_data.csv')
inmet_data = pd.read_csv('data/interim/SAO PAULO - MIRANTE_inmet_data.csv')

isd_data['DATE'] = pd.to_datetime(isd_data['DATE'])
inmet_data['DATE'] = pd.to_datetime(inmet_data['DATE'])

data = isd_data.merge(inmet_data, on='DATE', how='left')

data[['precipitation',
      'radiation']] = (data[['precipitation',
                             'radiation']].ffill() + data[['precipitation',
                                                           'radiation']].bfill()) / 2

data.to_csv('data/interim/unified_data.csv', index=False)
