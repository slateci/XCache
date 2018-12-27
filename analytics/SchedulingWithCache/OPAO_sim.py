'''
Simulates scheduling in a realistic ATLAS computing grid.
All CEs are connected to a local XCache.
Job durations are input data are taken from historical data. 
'''

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

import OPAO_utils as ou
import compute
from cache import XCacheSite

matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('ytick', labelsize=14)

# load computing grid.
grid = compute.Grid()

grid.stats()
# loop through jobs.
# "randomly" assign to sites.

step = 10000


sites = ['MWT2', 'AGLT2', 'NET2', 'SWT2', 'BNL']  # , 'OU_OSCER',  'UTA_SWT2',
periods = ['AUG', 'SEP', 'OCT', 'NOV']  # must be listed in order
kinds = ['prod']
skipFiles = []  # ':AOD.']

label = 'US_2x40TB_2x500TB_Int2'
output = label + '_' + '_'.join(kinds) + '_' + '_'.join(periods) + '_' + '_'.join(sites)
title = label + '\n' + ','.join(kinds) + ' ' + ' '.join(periods) + '\n' + ','.join(sites)

all_data = ou.load_data(sites, periods, kinds, skipFiles)

# all_data = all_data[:100000]

# create caching network
all_sites = {}


print('---------- start requests ----------')
acs = []
dac = []
accesses = [0, 0, 0]
dataaccc = [0, 0, 0]
count = 0

for index, row in all_data.iterrows():

    count += 1

    if count > 200000000:
        break

    if not count % step and count > 0:
        # print(count, accesses, dataaccc)
        acs.append(accesses.copy())
        dac.append(dataaccc.copy())
        pacce = []
        pdata = []
        for i in range(len(accesses)):
            pacce.append(accesses[i] / sum(accesses))
            pdata.append(dataaccc[i] / sum(dataaccc))
        print(count, pacce, pdata)

    if row.site not in all_sites:
        continue

    fs = row.filesize
    ts = row.transfer_start
    l0 = all_sites[row.site]
    found = l0.add_request(index, fs, ts)
    if found:
        accesses[0] += 1
        dataaccc[0] += fs
        continue

    l1 = all_sites[l0.upstream]
    found = l1.add_request(index, fs, ts)
    if found:
        accesses[1] += 1
        dataaccc[1] += fs
        continue

    l2 = all_sites[l1.upstream]
    found = l2.add_request(index, fs, ts)
    if found:
        accesses[2] += 1
        dataaccc[2] += fs
        continue

    l3 = all_sites[l2.upstream]
    found = l3.add_request(index, fs, ts)
    if found:
        accesses[3] += 1
        dataaccc[3] += fs
        continue


print('final: ', accesses, dataaccc)


accdf = pd.DataFrame(acs)
dacdf = pd.DataFrame(dac)

dacdf = dacdf / TB


# ### ploting results

accdf.columns = ['level 1', 'level 2',  'origin']
dacdf.columns = ['level 1', 'level 2',  'origin']

fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 10))
fig.suptitle(title, fontsize=18)

accdf.plot(ax=axs[0][0])
axs[0][0].set_ylabel('hits')
axs[0][0].set_xlabel('requests [x' + str(step) + ']')
axs[0][0].legend()

dacdf.plot(ax=axs[1][0])
axs[1][0].set_ylabel('data delivered [TB]')
axs[1][0].set_xlabel('requests [x' + str(step) + ']')
axs[1][0].legend()

accdf = accdf.div(accdf.sum(axis=1), axis=0)
dacdf = dacdf.div(dacdf.sum(axis=1), axis=0)

accdf.plot(ax=axs[0][1])
axs[0][1].set_ylabel('hits [%]')
axs[0][1].set_xlabel('requests [x' + str(step) + ']')
axs[0][1].grid(axis='y')
axs[0][1].legend()

dacdf.plot(ax=axs[1][1])
axs[1][1].set_ylabel('data delivered [%]')
axs[1][1].set_xlabel('requests [x' + str(step) + ']')
axs[1][1].grid(axis='y')
axs[1][1].legend()

# plt.show()

fig.savefig('filling_up_' + output + '.png')


# Network states

tp = []
st = pd.DataFrame()
for site in all_sites:
    s = all_sites[site]
    si = [site.replace('xc_', ''), s.requests, s.hits, s.data_asked_for / TB, s.data_from_cache / TB]
    if s.requests > 0 and site != 'Origin':
        st = pd.concat([st, s.get_servers_stats()])
    tp.append(si)
    if s.requests > 0:
        s.plot_throughput()

print(st.groupby(['site']).mean())

sites = pd.DataFrame(tp)
sites.columns = ['xcache', 'requests', 'hits', 'data asked for', 'delivered from cache']
sites = sites[sites.requests != 0]
sites.set_index('xcache', drop=True, inplace=True)
print(sites.head(20))

fig, ax = plt.subplots(figsize=(8, 8))
fig.suptitle(title, fontsize=18)
sites.plot(kind="bar", ax=ax, secondary_y=['data asked for', 'delivered from cache'])
ax.right_ax.set_ylabel('[TB]')
fig.savefig('xcache_sites_' + output + '.png')
