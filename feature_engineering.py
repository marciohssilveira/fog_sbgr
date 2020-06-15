import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, ward
from sklearn.preprocessing import StandardScaler

sbgr = pd.read_csv('./data/sbgr_data.csv')
"""
Dataset columns:
['direction', 'speed', 'visibility', 
'phenomenon_1', 'phenomenon_2', 'phenomenon_3', 
'coverage_1', 'coverage_2', 'coverage_3', 'coverage_4', 
'ceiling', 'temperature', 'dew', 'slp']
"""


# Create a column for relative humidity
def calculate_rh(temperature, dew):
    """
    Receives air temperature (t) and dew point (d) and returns relative humidity
    RH = 100*(EXP((17.625*TD)/(243.04+TD))/EXP((17.625*T)/(243.04+T)))
    """
    rh_list = []
    for t, d in zip(temperature, dew):
        rh = 100 * ((math.exp((17.625 * d) / (243.04 + d))) / (math.exp((17.625 * t) / (243.04 + t))))
        rh_list.append(rh)
    return rh_list


sbgr['rh'] = calculate_rh(sbgr['temperature'], sbgr['dew'])

# Create column for fog occurrence
mask = sbgr['phenomenon_1'] == 'Fog'
sbgr['is_fog'] = np.where(mask, 1, 0)


# Drop unused columns
sbgr = sbgr.drop(['DATE', 'phenomenon_1', 'phenomenon_2', 'phenomenon_3', 'ceiling',
                  'coverage_1', 'coverage_2', 'coverage_3', 'coverage_4', 'dew'], axis=1)

# Create columns to infer the added humidity in the last 12 houres
# shifts = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# shift = pd.concat([(sbgr['rh'].shift(i) - sbgr['rh'].shift(i+1)) for i in shifts], axis=1)
# shift.columns = ['rh-'+str(i) for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
#
# for index, row in shift.iterrows():
#     print(row)
#     added_rh = []
#     removed_rh = []
#     for step in row.values:
#         if step > 0:
#             added_rh.append(step)
#         elif step < 0:
#             removed_rh.append(step)
#         print(added_rh.sum())
#         print(removed_rh.sum())
#
#
#
# plt.scatter(sbgr['rh'], sbgr['visibility'])
# plt.show()
#
# sbgr = pd.concat([sbgr, shift], axis=1)

sbgr.dropna(inplace=True)

sbgr.to_csv('./data/labeled_fog.csv', index=False)

