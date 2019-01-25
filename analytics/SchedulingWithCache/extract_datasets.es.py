# Extracts datasets info

from rucio.client import DIDClient
from rucio.common import exception as rex
import estools

dc = DIDClient()

es = estools.get_es_connection()


def get_ds_info(scope, name):
    res = dc.get_metadata(scope, name)
    # print(res['length'], res['datatype'], res['bytes'])
    ds_files = res['length']
    ds_type = res['datatype']
    ds_size = res['bytes']
    return (ds_files, ds_size, ds_type)


def get_container_info(scope, name):
    cont = dc.list_content(scope, name)
    ds_files = 0
    ds_size = 0
    ds_type = ""
    for ds in cont:
        print(ds['scope'], ds['name'], ds['type'])
        if ds['type'] == 'CONTAINER':
            (fs, size, dtype) = get_container_info(ds['scope'], ds['name'])
        else:
            (fs, size, dtype) = get_ds_info(ds['scope'], ds['name'])
        ds_files += fs
        ds_size += size
        ds_type = dtype
    return (ds_files, ds_size, ds_type)


def main():
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
            ds_files = 0
            ds_size = 0
            ds_type = ''
            if dataset is not None:
                if not ':' in dataset:
                    print('* no Scope: \n', dataset)
                    status = -2
                else:
                    (scope, name) = dataset.split(':')
                    name = name.rstrip('/')
                    try:
                        res = dc.get_did(scope, name)
                        if res['type'] == 'DATASET':
                            ds_files, ds_size, ds_type = get_ds_info(scope, name)
                        elif res['type'] == 'CONTAINER':
                            ds_files, ds_size, ds_type = get_container_info(scope, name)
                        else:
                            print("NOT A DATASET OR CONTAINER!")
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
                    "ds_files": ds_files,
                    "ds_size": ds_size,
                    "ds_type": ds_type,
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


main()
