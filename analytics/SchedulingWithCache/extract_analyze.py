#%% [markdown]
# # analyze extracted info

#%%
import pandas as pd

#%%
task_type = 'prod'
# task_type = 'anal'

data = pd.read_hdf('analytics/SchedulingWithCache/data/tasks.h5', key='tasks', mode='r')

data = data[data.task_type == task_type]
data = data[data.ds_files > 0]
data['files_processed'] = data.Sinputfiles / data.ds_files

#%%
print("tasks:", data.shape[0])
gpt = data.groupby('processing_type')
print('unique datasets:', data.dataset.nunique())
all = pd.DataFrame(
    dict(
        tasks=gpt.size(),
        datasets=gpt.dataset.count(),
        unique_datasets=gpt.dataset.nunique(),
        jobs=gpt.jobs.sum(),
        input_files=gpt.Sinputfiles.sum(),
        files_processed=gpt.files_processed.mean()
    )
)
all = all[['tasks', 'datasets', 'unique_datasets', 'jobs', 'input_files', 'files_processed']]
all['dataset_reuse'] = all.datasets / all.unique_datasets
all['file_reuse'] = all.dataset_reuse * all.files_processed
all

#%%
# print(data.head())

#%%
unfound = data[(data.ds_type == 0) & (data.dataset)]
print('tasks where dataset deleted:', unfound.shape[0])
gun = unfound.groupby('processing_type')

unf = pd.DataFrame(
    dict(
        tasks=gun.size(),
        unique_datasets=gun.dataset.nunique(),
        jobs=gun.jobs.sum(),
        input_files=gun.Sinputfiles.sum()
    )
)
unf = unf[['tasks', 'unique_datasets', 'jobs', 'input_files']]
unf


#%%
found = data[(data.ds_type != 0) & (data.ds_files > 0)]
print('tasks where dataset found:', found.shape[0])
grfo = found.groupby('processing_type')

fou = pd.DataFrame(
    dict(
        tasks=grfo.size(),
        datasets=grfo.dataset.count(),
        unique_datasets=grfo.dataset.nunique(),
        jobs=grfo.jobs.sum(),
        input_files=grfo.Sinputfiles.sum(),
        input_data=grfo.ds_size.sum() / 1024 / 1024 / 1024 / 1024 / 1024,
        perc_files_used=grfo.files_processed.mean()
    )
)
fou = fou[['tasks', 'datasets', 'unique_datasets', 'jobs', 'input_files', 'input_data', 'perc_files_used']]
fou

#%% [markdown]
# # overlays

#%%
print(found[found.processing_type == 'overlay'].tail())

#%%
fig, ax = plt.subplots()
data.hist('jobs', ax=ax, bins=100, bottom=0.9)
ax.set_yscale('log')
