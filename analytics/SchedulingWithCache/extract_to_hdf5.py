# Extracts joined data from ES to hdf5

from elasticsearch.helpers import scan
import pandas as pd
import estools

tasks_query = {
    "query": {
        "bool": {
            "must_not": [
                {"term": {"status": 0}},
                {"term": {"status": 2}},
            ]
        }
    }
}

es = estools.get_es_connection()
scroll = scan(client=es, index="grid_emulation", query=tasks_query)
count = 0
data = []

for res in scroll:
    r = res['_source']
    # print(r)
    if r['status'] == -1:
        r['ds_type'] = 'None'
        r['ds_files'] = 0
        r['ds_size'] = 0
    if 'ds_type' not in r:
        print(r)
    data.append([
        int(res['_id']), r['creationdate'], r['endtime'], r['processingtype'], r['tasktype'],
        r['status'], r['Swall_time'], r['jobs'], r['Scores'], r['Sinputfiles'], r['dataset'],
        r['ds_type'], r['ds_files'], r['ds_size']
    ])

    count += 1
    if not count % 10000:
        print(count)

all_tasks = pd.DataFrame(data).sort_values(0)
all_tasks.columns = ['taskid', 'created_at', 'finished_at', 'processing_type',
                     'task_type', 'status', 'Swall_time', 'jobs', 'Scores',
                     'Sinputfiles', 'dataset', 'ds_type', 'ds_files', 'ds_size']

mintid = int(all_tasks.taskid.min())
maxtid = int(all_tasks.taskid.max())
print("tasks:", all_tasks.shape[0], "min", mintid, "max", maxtid)

print(all_tasks.head())
all_tasks.to_hdf('data/tasks.h5', key='tasks', mode='w', complevel=1)
