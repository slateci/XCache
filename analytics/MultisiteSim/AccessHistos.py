import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from cache import load_data

matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('ytick', labelsize=14)

step = 10000

MB = 1024 * 1024
GB = 1024 * MB
TB = 1024 * GB
PB = 1024 * TB

sites = ['MWT2', 'AGLT2', 'NET2', 'SWT2', 'BNL']  # , 'OU_OSCER',  'UTA_SWT2',
# sites = ['AGLT2', 'SWT2']
filetypes = []

periods = ['AUG', 'SEP']  # must be listed in order
kinds = ['prod']  # prod
title = 'Production inputs ' + ','.join(periods) + '\n'

bs = [1, 2, 10, 100, 1000, 10000, 100000]
sites_data = []


def get_type(s):
    f = s.split(":")[1]
    return f.split('.')[0]


for site in sites:
    site_data = load_data([site], periods, kinds)

    # get filetypes
    fts = []
    accpft = []
    totalacc = []
    dt = site_data.groupby(by=get_type)
    for name, group in dt:
        # print(name)  # , group)
        grouped = group.groupby('filename')
        gc = grouped.size().sort_values(ascending=False)  # series
        count, division = np.histogram(gc, bins=bs)
        # print('frequencies:')
        # print(division)
        # print(count)
        totalacc.append([group.shape[0], group.index.unique().shape[0]])
        fts.append(name)
        accpft.append(count)

    accdf = pd.DataFrame(accpft, index=fts, columns=['One', 'Two', '3-10', '11-100',
                                                     '101-1000', '1000-10001']).sort_values("One", ascending=False)

    totdf = pd.DataFrame(totalacc, index=fts, columns=['total', 'unique'])
    totdf['inf. cache hit rate'] = (totdf.total - totdf.unique) / totdf.total
    totdf.sort_values('inf. cache hit rate', ascending=False, inplace=True)

    totdf = totdf[totdf.total / site_data.shape[0] > 0.01]

    print(totdf)

    accdf = accdf[0:5]
    print(accdf)

    # put together in a stacked plot.
    fig, ax = plt.subplots(1, 2, figsize=(15, 8))
    fig.suptitle(title + site, fontsize=18)
    accdf.transpose().plot(ax=ax[0], kind='bar', stacked=False, logy=False, rot=45)

    totdf = totdf.drop(columns=["total", "unique"])
    ax[1].tick_params(axis='x', which='major', labelsize=7)
    totdf.plot(ax=ax[1], kind='bar', rot=45)

    fig.savefig('accesses_per_file_type_' + site + '.png')

    sites_data.append(site_data)
    print('----------------------------')

all_data = pd.concat(sites_data)

# # print(all_data.head())
all_data = all_data.sort_values('transfer_start')

print('---------- Fully merged -----------')
print(all_data.shape[0], 'files\t\t', all_data.index.unique().shape[0], 'unique files')
print(all_data.filesize.sum() / PB, "PB")
print(all_data.filesize.mean() / GB, "GB avg. file size")

fts = []
accpft = []
totalacc = []
dt = all_data.groupby(by=get_type)
for name, group in dt:
    # print(name)  # , group)
    grouped = group.groupby('filename')
    gc = grouped.size().sort_values(ascending=False)  # series
    count, division = np.histogram(gc, bins=bs)
    # print('frequencies:')
    # print(division)
    # print(count)
    fts.append(name)
    accpft.append(count)
    totalacc.append([group.shape[0], group.index.unique().shape[0]])

accdf = pd.DataFrame(accpft, index=fts, columns=['One', 'Two', '3-10', '11-100',
                                                 '101-1000', '1000-10001']).sort_values("One", ascending=False)

accdf = accdf[0:5]
print(accdf)


totdf = pd.DataFrame(totalacc, index=fts, columns=['total', 'unique'])
totdf['inf. cache hit rate'] = (totdf.total - totdf.unique) / totdf.total
totdf.sort_values('inf. cache hit rate', ascending=False, inplace=True)

totdf = totdf[totdf.total / site_data.shape[0] > 0.01]

print(totdf)


# put together in a stacked plot.
fig, ax = plt.subplots(1, 2, figsize=(15, 8))
fig.suptitle(title + ','.join(sites), fontsize=18)
accdf.transpose().plot(ax=ax[0], kind='bar', stacked=False, logy=False, rot=45)

totdf = totdf.drop(columns=["total", "unique"])
ax[1].tick_params(axis='x', which='major', labelsize=7)
totdf.plot(ax=ax[1], kind='bar', rot=45)

fig.savefig('accesses_per_file_type_ALL_sites.png')
