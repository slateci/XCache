#%% [markdown]
# # Extracts trace data from Elasticsearch and saves it in HDF5 files

#%%
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd

#%% [markdown]
# ### select sites and time periods

#%%
start_date = '2018-08-01 00:00:00'
end_date = '2018-09-01 00:00:00'
site = 'AGLT2'

print("start:", start_date, "end:", end_date)
start = int(pd.Timestamp(start_date).timestamp())
end = int(pd.Timestamp(end_date).timestamp())

#%% [markdown]
# ### select kind of traces to export and name your dataset

#%%
dataset = 'prod_AUG'
my_query = {
    "_source": ["time_start", "time_end", "site", "event", "scope", "filename", "filesize"],
    'query': {
        'bool': {
            'must': [
                {'range': {'time_start': {'gte': start, 'lt': end}}},
                {'exists': {"field": "filename"}},
                {'wildcard': {'site': site + '*'}},
                # {'wildcard': {'filename': 'EVNT*'}},
                #                 {'wildcard': {'event': 'get_sm*'}},
                {'term': {'event': 'get_sm'}}
                # {'term': {'event': 'get_sm_a'}},
                # {'term': {'event': 'download'}},
            ]
        }
    }
}


es = Elasticsearch(['atlas-kibana.mwt2.org:9200'], timeout=60)

#%% [markdown]
# ### Does export

#%%
scroll = scan(client=es, index="traces", query=my_query)
count = 0
requests = []
for res in scroll:
    r = res['_source']
    requests.append([r['scope'] + ':' + r['filename'], r['filesize'], r['time_start']])

    if not count % 100000:
        print(count)
    count = count + 1

# all_accesses = pd.DataFrame(requests).sort_values(2)
# all_accesses.columns = ['filename', 'filesize', 'transfer_start']
# all_accesses.set_index('filename', drop=True, inplace=True)
# all_accesses.to_hdf(site + '_' + dataset + '.h5', key=site, mode='w', complevel=1)
print('Done.')
