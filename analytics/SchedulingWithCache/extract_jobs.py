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
type = 'prod'  # anal
period = 'OCT'
tasks = pd.read_hdf('analytics/SchedulingWithCache/data/tasks_' + type + '_' + period + '.h5', key=type, mode='r')

print("tasks:", tasks.shape[0])

#%% [markdown]
# ### loops over all tasks, finds jobs, finds wall time, cores for all jobs.
#

#%%
count = 0
full_data = []
for task in tasks.itertuples():
    # if count > 100:
    #     break
    if not count % 1000:
        print(count)
    count += 1
    jobs_query = {
        "size": 1,
        "_source": ["proddblock"],
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
    job_count = res['hits']['total']
    if job_count == 0:
        continue
    cores = res['aggregations']['cores']['value']
    wall_time = res['aggregations']['wtime']['value']
    ninputfiles = res['aggregations']['nfiles']['value']
    dataset = res['hits']['hits'][0]['_source']['proddblock']
    full_data.append([int(task.taskid), task.created_at, task.finished_at,
                      task.processing_type, job_count, cores, wall_time, ninputfiles, dataset])
    print('tid:', task.taskid, '\tjobs:', job_count, '\tcores:', cores, '\tnfiles:', ninputfiles, '\ttype:', task.processing_type)

#%%
filled_tasks = pd.DataFrame(full_data)
filled_tasks.columns = ['taskid', 'created_at', 'finished_at', 'processing_type', 'jobs', 'cores', 'wall_time', 'inputfiles', 'dataset']
filled_tasks.sort_values('created_at', inplace=True)

#%%
print(filled_tasks.head())
filled_tasks.to_hdf('analytics/SchedulingWithCache/data/jobs_' + type + '_' + period + '.h5', key=type, mode='w', complevel=1)
