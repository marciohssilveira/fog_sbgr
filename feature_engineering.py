import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, ward
from sklearn.preprocessing import StandardScaler

sbgr = pd.read_csv('./data/consolidated_data.csv')

# Create column for fog occurrence
mask = sbgr.filter(like='phenomenon').applymap(lambda L: 'Fog' in L).any(axis=1)
fog = sbgr[mask]

# Create a variable to encapsulate the 12 hour advection of humidity

# Create a variable to encapsulate the 12 hour change in radiation


# _______x_______
# Separating fog types
# Preparing data for clustering

X = fog.drop(['phenomenon_1', 'date_time', 'visibility'], axis=1)

scaler = StandardScaler()
X = scaler.fit_transform(X)

# Visualizing hierarchy
Z = ward(X)
dendrogram(Z)
plt.show()  # 4 clusters are a good split

# Clustering
clustering = KMeans(n_clusters=3)
clustering.fit(X)
fog['label'] = clustering.labels_

# Elbow technique
X2 = fog.drop(['phenomenon_1', 'date_time', 'label', 'visibility'], axis=1)

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
