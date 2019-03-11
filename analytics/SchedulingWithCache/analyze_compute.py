#%% [markdown]
# # analyze extracted compute info

#%%
import pandas as pd

#%%
data = pd.read_hdf('analytics/SchedulingWithCache/data/compute.h5', mode='r')
print(data)

#%%
print("CEs:", data.shape[0])
gpt = data.groupby('cloud')
all = pd.DataFrame(
    dict(
        CEs=gpt.size(),
        cores=gpt.cores.sum()
    )
)
all = all[['CEs', 'cores']]
all

#%%
fig, ax = plt.subplots()
all.plot.bar(ax=ax)

#%%
cloud_weights = data.groupby('cloud').sum()['cores']
print(cloud_weights)

cloud_weights /= cloud_weights.sum()
for cl, clv in data.groupby('cloud'):
    site_weights[cl] = clv['cores']
    site_weights[cl] /= site_weights[cl].sum()
print(cloud_weights,  site_weights)
