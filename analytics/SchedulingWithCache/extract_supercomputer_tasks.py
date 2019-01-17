#%% [markdown]
# # Extracts tasks data
#

#%%
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd

es = Elasticsearch(['atlas-kibana.mwt2.org:9200'], timeout=60)

#%% [markdown]
# ### select time period

#%%
start_date = '2018-08-01 00:00:00'
end_date = '2019-01-01 00:00:00'

type = 'Titan'
period = 'ALL'

print("start:", start_date, "end:", end_date)
start = int(pd.Timestamp(start_date).timestamp()) * 1000
end = int(pd.Timestamp(end_date).timestamp()) * 1000

print("start:", start, "end:", end)

#%% [markdown]
# ### finds wall time, cores for all jobs.
#

#%%
task_query = {
    "_source": [],
    "query": {
        "bool": {
            "must": [
                {"term": {"status": "done"}},
                {"range": {"endtime": {"gte": start, "lt": end}}},
                {"wildcard": {"site": "*Titan*"}}
            ]
        }
    }
}

scroll = scan(client=es, index="tasks", query=task_query)
count = 0
requests = []
for res in scroll:
    requests.append([res['_id']])
    print(count, res['_id'])
    count = count + 1


#%%
all_tasks = pd.DataFrame(requests).sort_values(0)
all_tasks.columns = ['taskid']
mintid = int(all_tasks.taskid.min())
maxtid = int(all_tasks.taskid.max())
print("tasks:", all_tasks.shape[0], "min", mintid, "max", maxtid)


#%%
print(all_tasks.head())
all_tasks.to_hdf('tasks_' + type + '_' + period + '.h5', key=type, mode='w', complevel=1)
