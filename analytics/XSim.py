import threading
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

# import numpy as np
import pandas as pd

from cache import XCache

load_from_disk = False

start_date = '2018-04-01 00:00:00'
end_date = '2018-05-01 23:59:59'

site = 'MWT2'

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

        # XC.add_file(r['scope'] + r['filename'], r['filesize'], r['transfer_start'], r['transfer_end'])
        # requests.append([r['scope'] + r['filename'], r['filesize'], r['time_start'], r['time_end']])
        requests.append([r['scope'] + r['filename'], r['filesize'], r['time_start']])

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

logging.basicConfig(
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
)

logging.getLogger('cache').setLevel(logging.DEBUG)

logging.debug(str(XCache.all_accesses.shape[0]) + ' requests loaded.')
# XC.clairvoyant()

XC_5 = XCache('5TB cache ' + site, size=5 * XCache.TB)
XC_10 = XCache('10TB cache ' + site, size=10 * XCache.TB)
XC_20 = XCache('20TB cache ' + site, size=20 * XCache.TB)
XC_30 = XCache('30TB cache ' + site, size=30 * XCache.TB)
XC_inf = XCache('inf. cache ' + site, size=5000 * XCache.TB)


XC_5.start()
XC_10.start()
XC_20.start()
XC_30.start()
XC_inf.start()

XC_5.join()
XC_10.join()
XC_20.join()
XC_30.join()
XC_inf.join()

XC_5.print_cache_state()
XC_5.plot_cache_state()
XC_10.print_cache_state()
XC_10.plot_cache_state()
XC_20.print_cache_state()
XC_20.plot_cache_state()
XC_30.print_cache_state()
XC_30.plot_cache_state()
XC_inf.print_cache_state()
XC_inf.plot_cache_state()


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
