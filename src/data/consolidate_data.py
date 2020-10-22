



# isd_data = pd.read_csv('./data/isd_data.csv')
# isd_data.columns = ['date_time',
#                     'direction',
#                     'speed',
#                     'visibility',
#                     'phenomenon_1',
#                     'phenomenon_2',
#                     'phenomenon_3',
#                     'coverage_1',
#                     'coverage_2',
#                     'coverage_3',
#                     'coverage_4',
#                     'ceiling',
#                     'temperature_isd',
#                     'dew_isd',
#                     'slp',
#                     'rh']

# isd_data = isd_data[['date_time',
#                         'direction',
#                         'speed',
#                         'visibility',
#                         'phenomenon_1',
#                         'temperature_isd',
#                         'dew_isd',
#                         'rh',
#                         'slp', ]]

# inmet_data['date_time'] = pd.to_datetime(inmet_data['date_time'])

# inmet_data.to_csv('./data/inmet_data.csv', index=False)

# isd_data['date_time'] = pd.to_datetime(isd_data['date_time'])

# data = isd_data.merge(inmet_data, on='date_time', how='left')

# data[['precipitation',
#         'radiation']] = (data[['precipitation',
#                                 'radiation']].ffill() + data[['precipitation',
#                                                             'radiation']].bfill()) / 2

# data.to_csv('./data/consolidated_data.csv', index=False)