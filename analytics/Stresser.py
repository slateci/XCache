import matplotlib.pyplot as plt

import requests
import json
import pandas as pd

#service = "http://192.170.227.234:80"
service = "http://localhost:80"

sites = ['AGLT2', 'MWT2']
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
dataaccc = [0, 0, 0, 0]
count = 0
payload = []
for index, row in all_data.iterrows():
    if count > 31000:
        break
    fs = row['filesize']
    payload.append({'filename': index, 'site': row['site'], 'filesize': fs, 'time': row['transfer_start']})
    # print(payload)
    try:
        if count % 100 == 1:
            r = requests.post(service + '/simulate', json=payload)
            if r.status_code != 200:
                print(r)
            accs = r.json()
            for i, j in enumerate(accs['counts']):
                accesses[i] += int(j)
                dataaccc[i] += accs['sizes'][i]
            payload = []
    except requests.exceptions.RequestException as e:
        print(e)

    if not count % 1000:
        print(count, 'accesses finished.', accesses, dataaccc)
    count += 1

print('final: ', accesses, dataaccc)

res = requests.get(service + '/status')
status = json.loads(res.json())
# print(status)
for site in status:
    print(site[0])
    print(site[1])

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
