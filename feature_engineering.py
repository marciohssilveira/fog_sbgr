import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, ward
from sklearn.preprocessing import StandardScaler

sbgr = pd.read_csv('./data/sbgr_data.csv')
"""
Dataset columns:
['direction', 'speed', 'visibility', 
'phenomenon_1', 'phenomenon_2', 'phenomenon_3', 
'coverage_1', 'coverage_2', 'coverage_3', 'coverage_4', 
'ceiling', 'temperature', 'dew', 'slp', 'rh']
"""


# Create column for fog occurrence
mask = sbgr.filter(like='phenomenon').applymap(lambda L: 'Fog' in L).any(axis=1)
fog = sbgr[mask]

# Drop some columns
fog.drop(['phenomenon_1', 'phenomenon_2', 'phenomenon_3',
          'coverage_2', 'coverage_3', 'coverage_4'], axis=1, inplace=True)

# Fill missing values
fog['coverage_1'] = fog['coverage_1'].fillna(0)  # the absence of coverage means 0 oktas
fog['ceiling'] = fog['ceiling'].fillna(5000)  # the absence of ceiling means above 5000 feet
fog['temperature'] = fog['temperature'].fillna(method='ffill')
fog['dew'] = fog['dew'].fillna(method='ffill')
fog['slp'] = fog['slp'].fillna(method='ffill')
fog['rh'] = fog['rh'].fillna(method='ffill')

# Create a variable to encapsulate the 12 hour advection of humidity


# Separating fog types
# Preparing data for clustering

X = fog.drop(['DATE'], axis=1)

scaler = StandardScaler()
X = scaler.fit_transform(X)

# Visualizing hierarchy
Z = ward(X)
dendrogram(Z)
plt.show() # 4 clusters are a good split

# Clustering
clustering = KMeans(n_clusters=3)
clustering.fit(X)
fog['label'] = clustering.labels_


# Elbow technique
X2 = fog.drop(['DATE', 'label'], axis=1)

inertias = []
for k in range(1, 11):
    model = KMeans(n_clusters=k).fit(X2)
    inertias.append(model.inertia_)

# Plotting
plt.plot(range(1, 11), inertias, 'bx-')
plt.xlabel('Values of K')
plt.ylabel('Inertia')
plt.title('The Elbow Method using Inertia')
plt.show()

fog.to_csv('./data/labeled_fog.csv', index=False)