import pandas as pd

inmet_data = pd.read_csv('./data/dados_A701_H_2006-07-24_2020-07-01.csv', sep=';', skiprows=10)
inmet_data = inmet_data.drop(inmet_data.columns[-1], axis=1)

inmet_data = inmet_data[['Data Medição',
                         'Hora Medição',
                         'PRECIPITAÇÃO TOTAL, HORÁRIO(mm)',
                         'RADIACAO GLOBAL(W/m²)']]

inmet_data.columns = ['date',
                      'time',
                      'precipitation',
                      'radiation']

inmet_data['date_time'] = inmet_data['date'].astype(str) + \
                          ' ' + \
                          inmet_data['time'].apply(lambda x: str(x).zfill(4))

inmet_data = inmet_data[['date_time',
                         'precipitation',
                         'radiation']]

isd_data = pd.read_csv('./data/isd_data.csv')
isd_data.columns = ['date_time',
                    'direction',
                    'speed',
                    'visibility',
                    'phenomenon_1',
                    'phenomenon_2',
                    'phenomenon_3',
                    'coverage_1',
                    'coverage_2',
                    'coverage_3',
                    'coverage_4',
                    'ceiling',
                    'temperature_isd',
                    'dew_isd',
                    'slp',
                    'rh']

isd_data = isd_data[['date_time',
                     'direction',
                     'speed',
                     'visibility',
                     'phenomenon_1',
                     'temperature_isd',
                     'dew_isd',
                     'rh',
                     'slp', ]]

inmet_data['date_time'] = pd.to_datetime(inmet_data['date_time'])

inmet_data.to_csv('./data/inmet_data.csv', index=False)

isd_data['date_time'] = pd.to_datetime(isd_data['date_time'])

data = isd_data.merge(inmet_data, on='date_time', how='left')

data[['precipitation',
      'radiation']] = (data[['precipitation',
                             'radiation']].ffill() + data[['precipitation',
                                                           'radiation']].bfill()) / 2

data.to_csv('./data/consolidated_data.csv', index=False)