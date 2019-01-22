#%% [markdown]
# # Extracts jobs data
#

#%%
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from elasticsearch import helpers
from elasticsearch.helpers import scan


def get_es_connection():
    """
    establishes es connection.
    """
    print("make sure we are connected to ES...")
    try:
        es_conn = Elasticsearch([{'host': 'atlas-kibana.mwt2.org', 'port': 9200}])
        print("connected OK!")
    except es_exceptions.ConnectionError as error:
        print('ConnectionError in get_es_connection: ', error)
    except:
        print('Something seriously wrong happened in getting ES connection.')
    else:
        return es_conn


def bulk_index(data, es_conn=None, thread_name=''):
    """
    sends the data to ES for indexing.
    if successful returns True.
    """
    success = False
    if es_conn is None:
        es_conn = get_es_connection()
    try:
        res = helpers.bulk(es_conn, data, raise_on_exception=True, request_timeout=120)
        print(thread_name, "inserted:", res[0], 'errors:', res[1])
        success = True
    except es_exceptions.ConnectionError as error:
        print('ConnectionError ', error)
    except es_exceptions.TransportError as error:
        print('TransportError ', error)
    except helpers.BulkIndexError as error:
        print(error)
    except:
        print('Something seriously wrong happened.')
    return success


es = get_es_connection()

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
            res = bulk_index(data, es)
            if res:
                del data[:]

bulk_index(data)
print('final count:', count)
