# Extracts datasets info

import pandas as pd
from rucio.client import DIDClient
from rucio.common import exception as rex

from elasticsearch import Elasticsearch, exceptions as es_exceptions
from elasticsearch import helpers

dc = DIDClient()


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
    except e as error:
        print('Something seriously wrong happened.', e)
    return success


es = get_es_connection()

count = 0
data = []

while True:
    # get data with status = 2 (job info present)
    tasks_query = {
        "size": 100,
        "_source": ["dataset"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"status": 2}}
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
        dataset = doc['_source']['dataset']
        # print(tid, dataset)
        count += 1
        status = -5
        files = 0
        datatype = ''
        ds_size = 0
        if dataset is not None:

            if not ':' in dataset:
                print('* no Scope: \n', dataset)
                status = -2
            else:
                (scope, name) = dataset.split(':')
                try:
                    # gen = dc.list_files(scope, name)
                    # for f in gen:
                    #     print(f['guid'], f['bytes'])
                    res = dc.get_metadata(scope, name)
                    # print(res['length'], res['datatype'], res['bytes'])
                    files = res['length']
                    datatype = res['datatype']
                    ds_size = res['bytes']
                    status = 3
                except rex.DataIdentifierNotFound as dide:
                    status = -3
                    # print(dide)
                except rex.RucioException as rue:
                    status = -4
                    print(rue)
                except:
                    status = -5

        data.append({
            "_op_type": "update",
            "_id": tid,
            "_index": "grid_emulation",
            "_type": "doc",
            "doc": {
                "ds_files": files,
                "ds_type": datatype,
                "ds_size": ds_size,
                "status": status
            }
        })

        if not count % 100:
            print(count)
            # print(data)
            res = bulk_index(data, es)
            if res:
                del data[:]

bulk_index(data, es)
print('final count:', count)
