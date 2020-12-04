# Extracts trace data from Elasticsearch and saves it in HDF5 files
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd

# select sites and time periods
start_date = '2020-10-01 00:00:00'
end_date = '2020-11-01 00:00:00'
site = 'AGLT2'

print("start:", start_date, "end:", end_date)
start = pd.Timestamp(start_date).timestamp()
end = pd.Timestamp(end_date).timestamp()
print("start:", start, "end:", end)

# select kind of traces to export and name your dataset

dataset = 'prod_AUG'
my_query = {
    "_source": ["timeStart", "timeEnd", "localSite", "eventType", "scope", "filename", "filesize"],
    'query': {
        'bool': {
            'must': [
                {'range': {'timeStart': {'gte': start, 'lt': end}}},
                {'exists': {"field": "filename"}},
                {'wildcard': {'localSite': site + '*'}},
                # {'wildcard': {'filename': 'EVNT*'}},
                # {'wildcard': {'event': 'get_sm*'}},
                {'term': {'eventType': 'get_sm'}}
                # {'term': {'eventType': 'get_sm_a'}},
                # {'term': {'eventType': 'download'}},
            ]
        }
    }
}


es = Elasticsearch(['atlas-kibana.mwt2.org:9200'],
                   scheme="https",
                   http_auth=("rucio_reader", "u8i9o0p-"), timeout=30, max_retries=10, retry_on_timeout=True
                   )
# Does export
scroll = scan(client=es, index="rucio_traces", query=my_query)
count = 0
requests = []
for res in scroll:
    r = res['_source']
    requests.append([r['scope'] + ':' + r['filename'],
                     r['filesize'], r['timeStart']])

    if not count % 1000:
        print(count)
    count = count + 1

all_accesses = pd.DataFrame(requests).sort_values(2)
all_accesses.columns = ['filename', 'filesize', 'transfer_start']
all_accesses.set_index('filename', drop=True, inplace=True)
all_accesses.to_parquet(site + '_' + dataset + '.parquet')
print('Done.')
