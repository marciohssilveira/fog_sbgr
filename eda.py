import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sbgr = pd.read_csv('./data/labeled_fog.csv')

# wind rose attempt
sns.set(style='whitegrid')
# plt.figure(figsize=(20, 16))

ax = plt.subplot(111, polar=True)
ax.scatter(x=[np.deg2rad(x) for x in sbgr['direction'].values],
           y=sbgr['rh'], alpha=0.003)
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)

plt.title('Wind Direction (°) vs Relative Humidity %')
plt.show()


# Another way of visualising
