#%% [markdown]
# # Extracts jobs data

#%%

from elasticsearch.helpers import scan
import estools


es = estools.get_es_connection()

data = []
count = 0

while True:
    # get data with status = 0 (only task info present)
    tasks_query = {
        "size": 100,
        "sort": [
            {"creationdate": {"order": "asc"}}
        ],
        "_source": ["creationdate"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"status": 0}}
                ]
            }
        }
    }

    res = es.search(body=tasks_query, index="grid_emulation")

    if res['hits']['total'] == 0:
        break
    else:
        print('remaining:', res['hits']['total'])

    for doc in res['hits']['hits']:
        tid = doc['_id']

        # find jobs data.
        jobs_query = {
            "size": 1,
            "_source": ["proddblock"],
            "query": {
                "bool": {
                    "must": [
                        {"term": {"jeditaskid": tid}},
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
        status = 2
        if job_count == 0:
            print("task has no jobs?")
            status = -1
            cores = 0
            wall_time = 0
            ninputfiles = 0
            dataset = ''
        else:
            cores = res['aggregations']['cores']['value']
            wall_time = res['aggregations']['wtime']['value']
            ninputfiles = res['aggregations']['nfiles']['value']
            dataset = res['hits']['hits'][0]['_source']['proddblock']

        data.append({
            "_op_type": "update",
            "_id": tid,
            "_index": "grid_emulation",
            "_type": "doc",
            "doc": {
                "jobs": job_count,
                "Scores": cores,
                "Swall_time": wall_time,
                "Sinputfiles": ninputfiles,
                "dataset": dataset,
                "status": status
            }
        })

        count = count + 1

        # print('tid:', tid, '\tjobs:', job_count, '\tcores:', cores, '\tnfiles:', ninputfiles)

        if not count % 100:
            print(count)
            res = estools.bulk_index(data, es)
            if res:
                del data[:]

estools.bulk_index(data)
print('final count:', count)
