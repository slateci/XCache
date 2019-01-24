#%% [markdown]
# # Extracts tasks data
#
#%%
from elasticsearch.helpers import scan
import pandas as pd
import estools


#%%
start_date = '2018-08-01 00:00:00'
end_date = '2019-01-01 00:00:00'

print("start:", start_date, "end:", end_date)
start = int(pd.Timestamp(start_date).timestamp()) * 1000
end = int(pd.Timestamp(end_date).timestamp()) * 1000

print("start:", start, "end:", end)


#%%
task_query = {
    "_source": ["endtime", "creationdate", "processingtype", "tasktype", "site"],
    'query': {
        'bool': {
            'must': [
                {'term': {'status': 'done'}},
                {'range': {'endtime': {'gte': start, 'lt': end}}}
            ],
            'should': [
                {'term': {'tasktype': 'anal'}},
                {'term': {'tasktype': 'prod'}}
            ],
            'must_not': [
                {"wildcard": {"site": "NERSC*"}},
                {"wildcard": {"site": "*Titan*"}},
                {"wildcard": {"site": "ALCF*"}}
            ]
        }
    }
}

es = estools.get_es_connection()
scroll = scan(client=es, index="tasks", query=task_query)
count = 0
data = []

for res in scroll:
    r = res['_source']
    doc = {"_index": "grid_emulation", "_type": "doc", "_id": res['_id']}
    doc['creationdate'] = r['creationdate']
    doc['endtime'] = r['endtime']
    doc['processingtype'] = r['processingtype']
    doc['tasktype'] = r['tasktype']
    doc['site'] = r['site']
    doc['status'] = 0
    data.append(doc)

    if not count % 500:
        print(count)
        res = estools.bulk_index(data, es)
        if res:
            del data[:]
    count = count + 1

estools.bulk_index(data, es)
print('final count:', count)
