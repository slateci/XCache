#%% [markdown]
# # analyze extracted info

#%%
import pandas as pd

#%%
type = 'prod'  # anal
period = 'AUG'
data = pd.read_hdf('analytics/SchedulingWithCache/data/full_' + type + '_' + period + '.h5', key=type, mode='r')

#%%
print("tasks:", data.shape[0])
print('unique datasets:', data.dataset.nunique())
print('unique datasets per processing type:')
gr = data.groupby('processing_type').dataset.nunique()
print(gr)

#%%
print(data.head())

#%%
unfound = data[data.datatype == 0]
print('tasks where dataset deleted:', unfound.shape[0])
gr = unfound.groupby('processing_type')
print('unique datasets:\n', gr.dataset.nunique())
print('tasks:\n', gr.dataset.count())

#%%
found = data[data.datatype != 0]
found['files_processed'] = found.inputfiles / found.files_in_ds * 100
print('tasks where dataset found:', found.shape[0])
gr1 = found.groupby('processing_type')
print('unique datasets:\n', gr1.dataset.nunique())
print('tasks:\n', gr1.dataset.count())

print('perc. files used:', gr1.files_processed.mean())

#%% [markdown]
# # overlays

#%%
print(found[found.processing_type == 'overlay'].tail())
