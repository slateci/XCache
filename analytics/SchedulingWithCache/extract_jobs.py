#%% [markdown]
# # Extracts jobs data
#

#%%
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd

es = Elasticsearch(['atlas-kibana.mwt2.org:9200'], timeout=60)

#%% [markdown]
# ### load tasks data

#%%
type = 'managed'
period = 'AUG'
tasks = pd.read_hdf('analytics/SchedulingWithCache/data/' + type + '_' + period + '.h5', key='prod', mode='r')

print("tasks:", tasks.shape[0])

#%% [markdown]
# ### loops over all tasks, finds jobs, finds wall time, cores for all jobs.
#

#%%
count = 0
full_data = []
for task in tasks.itertuples():
    if count > 3:
        break
    if not count % 1000:
        print(count)
    count += 1
    jobs_query = {
        "size": 1,
        "_source": ["actualcorecount", "wall_time", "ninputdatafiles", "proddblock"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"jeditaskid": task.taskid}},
                    {"term": {"jobstatus": "finished"}}
                ]
            }
        },
        "aggs": {
            "cores": {"sum": {"field": "actualcorecount"}},
            "wtime": {"sum": {"field": "wall_time"}},
            "nfiles": {"sum": {"field": "ninputdatafiles"}}
        }
    }
    res = es.search(body=jobs_query, index="jobs")

    requests = []
    job_count = 0
    cores = 0
    wall_time = 0
    ninputfiles = 0
    dataset = ''
    for res in scroll:
        r = res['_source']
        cores += r['actualcorecount']
        wall_time += r['wall_time']
        ninputfiles += r['ninputdatafiles']
        job_count += 1
    full_data.append([int(task.taskid), task.created, task.finished, job_count, cores, wall_time, ninputfiles, r['proddblock']])
    print('tid:', task.taskid, '\tjobs:', job_count, '\tcores:', cores, '\tnfiles:', ninputfiles)

#%%
print(full_data)

filled_tasks = pd.DataFrame(full_data)
filled_tasks.columns = ['taskid', 'created', 'finished', 'jobs', 'cores', 'wall_time', 'inputfiles', 'dataset']
filled_tasks.sort_values('created', inplace=True)
print(filled_tasks.head())
print("tasks:", filled_tasks.shape[0])


#%%
print(filled_tasks.head())
filled_tasks.to_hdf('analytics/SchedulingWithCache/data/' + type + '_' + period + '_filled.h5', key="filled", mode='w', complevel=1)
