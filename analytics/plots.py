import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

site = 'MWT2'
r = pd.read_hdf(site + '_results.h5')
print(r)
rt = r.transpose()
# rt = rt.reindex(["1/2", "1", "2", "3", "Inf"])
print(rt)

plt.figure(figsize=(12, 12))
plt.suptitle(site, fontsize=18)

ax1 = plt.subplot(221)
lab = rt.index
ind = np.arange(len(lab))
ax1.plot(ind, rt["cache hits"], '--bo')
ax1.set_ylabel('cache hits', color='b')
ax2 = plt.twinx()
ax2.plot(ind, rt["cleanups"], '-r+')
ax2.set_ylabel('cleanups', color='r')
plt.xticks(ind, lab)
plt.xlabel('cache size - base is 10TB')

plt.show()
#         plt.yscale('log', nonposy='clip')
#         plt.xscale('log', nonposy='clip')
#         plt.hist(df['filesize'], 200)
