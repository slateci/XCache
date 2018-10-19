import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from cache import XCacheSite

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
dataset = 'AUG'
title = ','.join(sites)

bs = [1, 2, 10, 100, 1000, 10000, 100000]
sites_data = []


def get_type(s):
    f = s.split(":")[1]
    return f.split('.')[0]


for site in sites:
    site_data = pd.read_hdf("../data/" + dataset + '/' + site + '_' + dataset + '.h5', key=site, mode='r')
    print(site)
    site_data['site'] = 'xc_' + site
    print(site_data.shape[0], "accesses\t",)
    print(site_data.index.unique().shape[0], " unique files")
    print(site_data.filesize.sum() / PB, "PB")
    print(site_data.filesize.mean() / GB, "GB avg. file size")

    gc = site_data.groupby('filename').size().sort_values(ascending=False)  # series

    count, division = np.histogram(gc, bins=bs)
    print('frequencies:')
    print(division)
    print(count)
    print('accesses can not be cached:', count[0] / site_data.shape[0] * 100, "%")
    print('percentage of files that should not be cached:', count[0] / site_data.index.unique().shape[0] * 100, "%")

    print('avg accesses per file type')
    # print('more then 1 access: ')
    mt1 = gc[gc > 1].groupby(by=get_type).size().sort_values(ascending=False)
    # print('single access: ')
    sa = gc[gc == 1].groupby(by=get_type).size().sort_values(ascending=False)

    print(mt1.to_frame(name='multiple').merge(sa.to_frame(name='single'), left_index=True, right_index=True))
    # print(pd.concat([mt1, sa]))

    sites_data.append(site_data)
    # print(gc.groupby(gc).count())

    # fig, ax = plt.subplots(figsize=(8, 8))
    # title = site + ' accesses'
    # fig.suptitle(title, fontsize=18)
    # gc.plot.hist(ax=ax, logx=True, logy=True)
    # fig.savefig('accesses_' + title.replace(' ', '_') + '.png')
    print('----------------------------')

all_data = pd.concat(sites_data)

# print(all_data.head())
all_data = all_data.sort_values('transfer_start')

print('---------- merged data -----------')
print(all_data.shape[0], 'files\t\t', all_data.index.unique().shape[0], 'unique files')
print(all_data.filesize.sum() / PB, "PB")
print(all_data.filesize.mean() / GB, "GB avg. file size")

gc = all_data.groupby('filename').size().sort_values(ascending=False)  # series

count, division = np.histogram(gc, bins=bs)
print('frequencies:')
print(division)
print(count)
print('can not be cached:', count[0] / all_data.shape[0] * 100, "%")
print('percentage of files that should not be cached:', count[0] / all_data.index.unique().shape[0] * 100, "%")

print('------------ overlap matrix ------------')
for i in range(len(sites)):
    for j in range(len(sites)):
        if j <= i:
            continue
        print()
        u1 = sites_data[i].index.unique().to_series()
        u2 = sites_data[j].index.unique().to_series()
        # print(u1)
        (l, r) = u1.align(u2, join='inner')
        print(sites[i], l.shape[0] / u1.shape[0],  sites[j], l.shape[0] / u2.shape[0], 'overlaping in absolute: ', l.shape[0])
# print(all_data.head())
# plt.hist(gc, log=True, bins=bs)
# plt.show()

# gc.plot(kind="hist", ax=ax, bins=20, loglog=True)  # , bins=20, logx=True, logy=True
# fig.savefig('accesses_' + '_'.join(sites) + '.png')
# plt.show()
# single = gc[gc[0] == 1]
# print(single.shape)
# split in quarters of accesses. number of files, size. per site. in total

# files used at more than one site
