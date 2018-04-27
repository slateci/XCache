from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import seaborn as sns
import matplotlib.pylab as plt
import numpy as np
import pandas as pd

load_from_disk = True

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
    all_accesses = pd.read_hdf(site + '.h5', key=site, mode='r')
else:
    scroll = scan(client=es, index=indices, query=my_query)
    count = 0
    requests = []
    for res in scroll:
        r = res['_source']
        # requests.append([r['scope'] + r['filename'], r['filesize'], r['time_start'], r['time_end']])
        requests.append([r['scope'] + r['filename'], r['filesize'], r['time_start']])

        # if count < 2:
        #     print(res)
        if not count % 100000:
            print(count)
        # if count > 100000:
        #     break
        count = count + 1

    all_accesses = pd.DataFrame(requests).sort_values(2)
    all_accesses.columns = ['filename', 'filesize', 'transfer_start']
    all_accesses.set_index('filename', drop=True, inplace=True)
    all_accesses.to_hdf(site + '.h5', key=site, mode='w', complevel=1)

print(all_accesses.shape[0], ' requests loaded.')

all_accesses.drop('transfer_start', axis=1, inplace=True)

all_grouped = all_accesses.groupby('filename')
reduced = all_grouped.agg(['mean', 'count'])

x = np.log(reduced.filesize['mean'] / 1024 / 1024)
y = np.log(reduced.filesize['count'])
with sns.axes_style("white"):
    sns.jointplot(x=x, y=y, kind="hex", color="k")

# mybins = np.logspace(0, np.log(100), 100)
# x = reduced.filesize['mean'] / 1024 / 1024
# y = reduced.filesize['count']
# g = sns.JointGrid(x=x, y=y)  # , xlim=[1,100],ylim=[0.01,100])
# g.plot_marginals(sns.distplot, hist=True, kde=True, color='blue', bins=mybins)
# g.plot_joint(plt.scatter, color='black', edgecolor='black')
# ax = g.ax_joint
# ax.set_xscale('log')
# ax.set_yscale('log')
# g.ax_marg_x.set_xscale('log')
# g.ax_marg_y.set_yscale('log')

# x = reduced.filesize['mean'] / 1024 / 1024
# y = reduced.filesize['count']
# sns.jointplot(x=x, y=y, color="k")
# ax = plt.gca()
# ax.set_xscale('log')
# ax.set_yscale('log')

plt.show()

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
