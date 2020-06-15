import pandas as pd

sbgr_data = pd.read_csv('data/sbgr_data.csv', index_col='DATE')


def make_shift(df, column):
    shifts = list(range(1, 13))
    shift = pd.concat([df[column].shift(i) for i in shifts], axis=1)
    shift.columns = [f'{column}_t-{str(i)}' for i in shifts]
    return shift


shiftable_columns = ['direction', 'speed', 'visibility', 'ceiling', 'temperature', 'dew', 'slp']


shifted_dict = {}
for column in shiftable_columns:
    shifted_dict[column] = make_shift(sbgr_data, column)


shifted_df = pd.concat(list(shifted_dict.values()), axis=1)