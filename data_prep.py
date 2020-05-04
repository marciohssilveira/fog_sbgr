import pandas as pd

sbgr_data = pd.read_csv('data/sbgr_data.csv', index_col='DATE')

fog_sbgr = sbgr_data[sbgr_data['visibility'] < 1000]

# Try to use some time shift to create a "rate" for the variables


def make_shift(df, column):
    shifts = list(range(1, 13))
    shift = pd.concat([df[column].shift(i) for i in shifts], axis=1)
    shift.columns = [f'{column}_t-{str(i)}' for i in shifts]
    return shift


teste = make_shift(sbgr_data, 'ceiling')