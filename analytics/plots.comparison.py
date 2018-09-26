import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


site = 'MWT2'
title = ' August AOD* files '
directory = 'MWT2/August/AOD/'
algo1 = 'LRU'
# title = ' FS'
# title = ' LRU (files larger than 1GB not cached)'
# title = + ' LRU (files smaller than 100kB not cached)'
algo2 = 'Clairvoyant'
# title = + ' LRU prod only'

results1 = [
    # [site + '_128_LRU_results.h5', '128GB'],
    # [site + '_256_LRU_results.h5', '256GB'],
    # [site + '_512_LRU_results.h5', '512GB'],
    # [site + '_1_LRU_results.h5', '1TB'],
    # [site + '_2_LRU_results.h5', '2'],
    # [site + '_5_LRU_results.h5', '5'],
    # [site + '_10_LRU_results.h5', '10'],
    # [site + '_20_LRU_results.h5', '20'],
    # [site + '_30_LRU_results.h5', '30'],
    # [site + '_40_LRU_results.h5', '40'],
    [site + '_50_LRU_results.h5', '50'],
    [site + '_100_LRU_results.h5', '100'],
    [site + '_200_LRU_results.h5', '200'],
    [site + '_400_LRU_results.h5', '400'],
    [site + '_800_LRU_results.h5', '800TB'],
    [site + '_10000_LRU_results.h5', 'Inf']
]

results2 = [
    # [site + '_128_Clairvoyant_results.h5', '128GB'],
    # [site + '_256_Clairvoyant_results.h5', '256GB'],
    # [site + '_512_Clairvoyant_results.h5', '512GB'],
    # [site + '_1_Clairvoyant_results.h5', '1TB'],
    # [site + '_2_Clairvoyant_results.h5', '2TB'],
    # [site + '_5_Clairvoyant_results.h5', '5TB'],
    # [site + '_10_Clairvoyant_results.h5', '10TB'],
    # [site + '_20_Clairvoyant_results.h5', '20TB'],
    # [site + '_30_Clairvoyant_results.h5', '30TB'],
    # [site + '_40_Clairvoyant_results.h5', '40TB'],
    [site + '_50_Clairvoyant_results.h5', '50TB'],
    [site + '_100_Clairvoyant_results.h5', '100TB'],
    [site + '_200_Clairvoyant_results.h5', '200TB'],
    [site + '_400_Clairvoyant_results.h5', '400TB'],
    [site + '_800_Clairvoyant_results.h5', '800TB'],
    [site + '_10000_Clairvoyant_results.h5', 'Inf']
]

# results = [
#     [site+ '_5_FS_results.h5', '5TB'],
#     [site+ '_10_FS_results.h5', '10TB'],
#     [site+ '_20_FS_results.h5', '20TB'],
#     [site+ '_30_FS_results.h5', '30TB'],
#     [site+ '_40_FS_results.h5', '40TB'],
#     [site+ '_50_FS_results.h5', '50TB'],
#     [site+ '_10000_FS_results.h5', 'Inf']
# ]

df1 = None
df2 = None

for r in results1:
    rdf = pd.read_hdf(directory + r[0])
    rdf.columns = [r[1]]
    # print(rdf)
    if df1 is None:
        df1 = rdf
    else:
        df1 = df1.join(rdf)

for r in results2:
    rdf = pd.read_hdf(directory + r[0])
    rdf.columns = [r[1]]
    # print(rdf)
    if df2 is None:
        df2 = rdf
    else:
        df2 = df2.join(rdf)

# print(df1)
# print(df2)

rt1 = df1.transpose()
rt1['cache hit rate'] = rt1['cache hits'] / rt1['total accesses'] * 100
rt1['cache data delivery'] = rt1['delivered from cache'] / rt1['delivered data'] * 100
print(rt1)

rt2 = df2.transpose()
rt2['cache hit rate'] = rt2['cache hits'] / rt2['total accesses'] * 100
rt2['cache data delivery'] = rt2['delivered from cache'] / rt2['delivered data'] * 100
print(rt2)

lab = rt1.index
ind = np.arange(len(lab))

plt.figure(figsize=(18, 8))
plt.suptitle(site + ' ' + title, fontsize=16)

ax1 = plt.subplot(231)
ax1.plot(ind, rt1["cache hit rate"], '--bo', label=algo1)
ax1.plot(ind, rt2["cache hit rate"], '-r+', label=algo2)
ax1.set_ylabel('accesses from cache [%]')
ax1.legend()
ax1.grid(axis='y', linestyle='-', linewidth=.5)
plt.xticks(ind, lab)
plt.xlabel('cache size')

ax2 = plt.subplot(232)
ax2.plot(ind, rt1["cache data delivery"], '--bo', label=algo1)
ax2.plot(ind, rt2["cache data delivery"], '-r+', label=algo2)
ax2.set_ylabel('data from cache [%]')
ax2.legend()
ax2.grid(axis='y', linestyle='-', linewidth=.5)
plt.xticks(ind, lab)
plt.xlabel('cache size')

ax3 = plt.subplot(233)
# ax2 = plt.twinx()
ax3.plot(ind, rt1["cleanups"], '--bo', label=algo1)
ax3.plot(ind, rt2["cleanups"], '-r+', label=algo2)
ax3.set_ylabel('cleanups')
ax3.legend()
ax3.grid(axis='y', linestyle='-', linewidth=.5)
plt.xticks(ind, lab)
plt.xlabel('cache size')

ax4 = plt.subplot(234)
ax4.plot(ind, rt1["files in cache"], '--bo', label=algo1)
ax4.plot(ind, rt2["files in cache"], '-r+', label=algo2)
ax4.set_ylabel('files in cache')
ax4.legend()
ax4.grid(axis='y', linestyle='-', linewidth=.5)
plt.xticks(ind, lab)
plt.xlabel('cache size')


ax5 = plt.subplot(235)
ax5.plot(ind, rt1["avg. accesses of cached files"], '--bo', label=algo1)
ax5.plot(ind, rt2["avg. accesses of cached files"], '-r+', label=algo2)
ax5.set_ylabel('avg. accesses of cached files')
ax5.legend()
ax5.grid(axis='y', linestyle='-', linewidth=.5)
plt.xticks(ind, lab)
plt.xlabel('cache size')

plt.savefig(algo1 + '_' + algo2 + '_analysis.png')
plt.show()
#         plt.yscale('log', nonposy='clip')
#         plt.xscale('log', nonposy='clip')
#         plt.hist(df['filesize'], 200)
