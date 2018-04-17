from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

# import numpy as np
import pandas as pd

import cache

start_date = '2018-04-01 00:00:00'
end_date = '2018-05-01 23:59:59'

site = 'WUPPERTAL'

site += '*'
es = Elasticsearch(['atlas-kibana.mwt2.org:9200'], timeout=60)
indices = "traces"


print("start:", start_date, "end:", end_date)
start = int(pd.Timestamp(start_date).timestamp())
end = int(pd.Timestamp(end_date).timestamp())

my_query = {
    "_source": ["transfer_start", "transfer_end", "site", "event", "scope", "filename", "filesize"],
    'query': {
        'bool': {
            'must': [
                {'range': {'transfer_end': {'gte': start, 'lt': end}}},
                {'wildcard': {'site': site}},
                {'term': {'event': 'download'}},
            ]
        }
    }
}


scroll = scan(client=es, index=indices, query=my_query)

count = 0

XC = cache.XCache(10 * 1024 * 1024 * 1024 * 1024)

for res in scroll:
    r = res['_source']

    XC.add_file(r['scope'] + r['filename'], r['filesize'], r['transfer_start'], r['transfer_end'])
    # if count < 2:
    #     print(res)
    if not count % 100000:
        print(count)
    # if count > 5:
    #     break
    count = count + 1

XC.print_cache_state()

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
