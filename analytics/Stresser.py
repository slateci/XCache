import requests
import matplotlib.pyplot as plt

import pandas as pd

sites = ['AGLT2']  # , 'MWT2']
dataset = 'AUG'

GB = 1024 * 1024 * 1024
TB = 1024 * GB
PB = 1024 * TB

all_accesses = []
for si, site in enumerate(sites):
    print('Loading:', site)
    all_accesses.append(pd.read_hdf(site + '_' + dataset + '.h5', key=site, mode='r'))
    all_accesses[si]['site'] = 'xc_' + site
    # print(all_accesses[si].head())
    print(all_accesses[si].filesize.count(), "files")
    print(all_accesses[si].filesize.sum() / PB, "PB")
    print(all_accesses[si].filesize.mean() / GB, "GB avg. file size")

all_data = pd.concat(all_accesses).sort_values('transfer_start')

print('---------- data merged -----------')
print(all_data.shape[0], 'files')
print(all_data.filesize.sum() / PB, "PB")
print(all_data.filesize.mean() / GB, "GB avg. file size")
# print(all_data.head(100))

print('---------- start requests ----------')

accesses = [0, 0, 0, 0]
count = 0
for index, row in all_data.iterrows():
    if count > 3000:
        break
    payload = {'filename': index, 'site': row['site'], 'filesize': row['filesize'], 'time': row['transfer_start']}
    # print(payload)
    r = requests.get('http://localhost:8080/simulate', params=payload)
    if r.status_code != 200:
        print(r, r.content)
        break
    accesses[int(r.content[-1])] += 1

    if not count % 1000:
        print(count, 'accesses finished.')
    count += 1

print(accesses)
asdf


data = (25, 32, 34, 20, 25)

ind = np.arange(len(accesses))  # the x locations for the groups
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(ind - width / 2, accesses, width, color='SkyBlue', label='cache hits')
rects2 = ax.bar(ind + width / 2, data, width, color='IndianRed', label='data delivered from cache')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Scores')
ax.set_title('Scores by group and gender')
ax.set_xticks(ind)
ax.set_xticklabels(('L1', 'L2', 'L3'))
ax.legend()
plt.show()
