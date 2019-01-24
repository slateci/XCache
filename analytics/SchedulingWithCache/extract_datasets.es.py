# Extracts datasets info

from rucio.client import DIDClient
from rucio.common import exception as rex
import estools

dc = DIDClient()

es = estools.get_es_connection()

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
                    {"term": {"status": 2}},
                    {"term": {"tasktype": "prod"}}
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
            res = estools.bulk_index(data, es)
            if res:
                del data[:]

estools.bulk_index(data, es)
print('final count:', count)
