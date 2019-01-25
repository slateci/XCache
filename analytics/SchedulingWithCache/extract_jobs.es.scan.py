#%% [markdown]
# # Extracts jobs data

#%%
import pandas as pd
from elasticsearch.helpers import scan
import estools

start_date = '2018-09-01 00:00:00'
end_date = '2019-01-01 00:00:00'

print("start:", start_date, "end:", end_date)
start = int(pd.Timestamp(start_date).timestamp()) * 1000
end = int(pd.Timestamp(end_date).timestamp()) * 1000

print("start:", start, "end:", end)

es = estools.get_es_connection()

tasks_query = {
    "_source": ["creationdate"],
    "query": {
        "bool": {
            "must": [
                {"term": {"status": 0}}
            ]
        }
    }
}

scroll = scan(client=es, index="grid_emulation", query=tasks_query)
count = 0
data = {}

for res in scroll:
    data[int(res['_id'])] = [0, 0, 0, 0, '']  # njobs, cores, wall_time, inputfiles, dataset
    count += 1
    if not count % 10000:
        print(count)

print('tasks to process:', count)

# find jobs data.
jobs_query = {
    "_source": ["jeditaskid", "actualcorecount", "wall_time", "ninputdatafiles", "proddblock"],
    "query": {
        "bool": {
            "must": [
                {"term": {"jobstatus": "finished"}},
                {"range": {"modificationtime": {"gte": start, "lt": end}}}
            ]
        }
    }
}


scroll = scan(client=es, index="jobs", query=jobs_query)

count = 0
matching_jobs = 0

for res in scroll:
    r = res['_source']
    # print(r)
    if r['jeditaskid'] in data:
        matching_jobs += 1
        d = data[r['jeditaskid']]
        d[0] += 1
        d[1] += r['actualcorecount']
        d[2] += r['wall_time']
        d[3] += r['ninputdatafiles']
        d[4] = r['proddblock']
        # data[res['_id']] = [0, 0, 0, 0, '']  # njobs, cores, wall_time, inputfiles, dataset
    count += 1
    if not count % 10000:
        print(count)
print('total jobs read:', count)

count = 0
to_store = []
for tid in data:
    row = data[tid]
    print(tid, row)
    if row[0] == 0:
        status = -1
    else:
        status = 1
    to_store.append({
        "_op_type": "update",
        "_id": tid,
        "_index": "grid_emulation",
        "_type": "doc",
        "doc": {
            "jobs": row[0],
            "Scores": row[1],
            "Swall_time": row[2],
            "Sinputfiles": row[3],
            "dataset": row[4],
            "status": status
        }
    })
    count += 1
    if not count % 500:
        print(count)
        res = estools.bulk_index(to_store, es)
        if res:
            del to_store[:]

estools.bulk_index(to_store)
print('final updates:', count)
