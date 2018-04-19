from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

# import numpy as np
import pandas as pd

import cache

start_date = '2018-04-01 00:00:00'
end_date = '2018-05-01 23:59:59'

site = 'MWT2'

site += '*'
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
                {'wildcard': {'site': site}},
                {'wildcard': {'event': 'get*'}},
                # {'term': {'event': 'download'}},
            ]
        }
    }
}

# "transfer_start", "transfer_end",

scroll = scan(client=es, index=indices, query=my_query)

count = 0

XC = cache.XCache()

for res in scroll:
    r = res['_source']

    # XC.add_file(r['scope'] + r['filename'], r['filesize'], r['transfer_start'], r['transfer_end'])
    # XC.add_file(r['scope'] + r['filename'], r['filesize'], r['time_start'], r['time_end'])
    XC.insert_file(r['scope'] + r['filename'], r['filesize'], r['time_start'], r['time_end'])

    # if count < 2:
    #     print(res)
    if not count % 100000:
        print(count)
    # if count > 100000:
        # break
    count = count + 1

TB = 1024 * 1024 * 1024 * 1024

clairvoyant = True

XC.set_name('5TB cache')
XC.set_size(5 * TB)
XC.replay_cache(clairvoyant)
XC.print_cache_state()
XC.plot_cache_state()

XC.set_name('10TB cache')
XC.set_size(10 * TB)
XC.replay_cache(clairvoyant)
XC.print_cache_state()
XC.plot_cache_state()

XC.set_name('20TB cache')
XC.set_size(20 * TB)
XC.replay_cache(clairvoyant)
XC.print_cache_state()
XC.plot_cache_state()

XC.set_name('30TB cache')
XC.set_size(30 * TB)
XC.replay_cache(clairvoyant)
XC.print_cache_state()
XC.plot_cache_state()

XC.set_name('inf. cache')
XC.set_size(4000 * TB)
XC.replay_cache(clairvoyant)
XC.print_cache_state()
# XC.plot_cache_state()

# dfs = []
# for dest, data in allData.items():
#     ts = pd.to_datetime(data[0], unit='ms')
#     df = pd.DataFrame({dest: data[1]}, index=ts)
#     df.sort_index(inplace=True)
#     df.index = df.index.map(lambda t: t.replace(second=0))
#     df = df[~df.index.duplicated(keep='last')]
#     dfs.append(df)
#     # print(df.head(2))

# print(count, "\nData loaded.")
