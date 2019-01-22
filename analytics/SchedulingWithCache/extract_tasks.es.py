#%% [markdown]
# # Extracts tasks data
#
#%%
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from elasticsearch import helpers
from elasticsearch.helpers import scan
import pandas as pd


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

es = get_es_connection()
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
        res = bulk_index(data, es)
        if res:
            del data[:]
    count = count + 1

bulk_index(data, es)
print('final count:', count)
