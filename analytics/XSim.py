import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

import pandas as pd

from cache import XCache, set_skip_tag, clairvoyant

load_from_disk = True

start_date = '2018-04-01 00:00:00'
end_date = '2018-05-01 23:59:59'

site = 'AGLT2'

es = Elasticsearch(['atlas-kibana.mwt2.org:9200'], timeout=60)
indices = "traces"

print("start:", start_date, "end:", end_date)
start = int(pd.Timestamp(start_date).timestamp())
end = int(pd.Timestamp(end_date).timestamp())

my_query = {
    "_source": ["time_start", "time_end", "site", "event", "scope", "filename", "filesize"],
    'query': {
        'bool': {
            'must': [
                {'range': {'time_start': {'gte': start, 'lt': end}}},
                {'exists': {"field": "filename"}},
                {'wildcard': {'site': site + '*'}},
                {'wildcard': {'event': 'get*'}},
                # {'term': {'event': 'get_sm'}},
                # {'term': {'event': 'download'}},
            ]
        }
    }
}

# "transfer_start", "transfer_end",

if load_from_disk:
    XCache.all_accesses = pd.read_hdf(site + '.h5', key=site, mode='r')
else:
    scroll = scan(client=es, index=indices, query=my_query)
    count = 0
    requests = []
    for res in scroll:
        r = res['_source']
        # requests.append([r['scope'] + r['filename'], r['filesize'], r['time_start'], r['time_end']])
        requests.append([r['scope'] + ':' + r['filename'], r['filesize'], r['time_start']])

        # if count < 2:
        #     print(res)
        if not count % 100000:
            print(count)
        # if count > 100000:
        #     break
        count = count + 1

    XCache.all_accesses = pd.DataFrame(requests).sort_values(2)
    XCache.all_accesses.columns = ['filename', 'filesize', 'transfer_start']
    XCache.all_accesses.set_index('filename', drop=True, inplace=True)
    XCache.all_accesses.to_hdf(site + '.h5', key=site, mode='w', complevel=1)

# logging.basicConfig(
#     format='[%(levelname)s] (%(threadName)-10s) %(message)s',
# )

logging.getLogger('cache').setLevel(logging.DEBUG)

logging.debug(str(XCache.all_accesses.shape[0]) + ' requests loaded.')
# XCache.all_accesses = XCache.all_accesses[:100000]
clairvoyant()
# set_skip_tag()

for i in [10, 20, 30, 40, 50, 100, 10000]:
    # for i in [5, 10, 20, 30, 10000]:
    XC = XCache(site, size=i * XCache.TB, algo='Clairvoyant')  #
    XC.run()
    XC.store_result()
