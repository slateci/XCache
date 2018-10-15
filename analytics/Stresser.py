import matplotlib.pyplot as plt
import numpy as np
import requests
import json
import pandas as pd

# service = "http://192.170.227.234:80"
service = "http://localhost:80"

sites = ['AGLT2', 'MWT2']
dataset = 'AUG'

GB = 1024 * 1024 * 1024
TB = 1024 * GB
PB = 1024 * TB


# ### Import data

all_accesses = []
for si, site in enumerate(sites):
    print('Loading:', site)
    all_accesses.append(pd.read_hdf(site + '_' + dataset + '.h5', key=site, mode='r'))
    all_accesses[si]['site'] = 'xc_' + site
    # print(all_accesses[si].head())
    print(all_accesses[si].filesize.count(), "files")
    print(all_accesses[si].index.unique().shape[0], " unique files")
    print(all_accesses[si].filesize.sum() / PB, "PB")
    print(all_accesses[si].filesize.mean() / GB, "GB avg. file size")
    print('----------------------------')

all_data = pd.concat(all_accesses).sort_values('transfer_start')

print('---------- merged data -----------')
print(all_data.shape[0], 'files\t\t', all_data.index.unique().shape[0], 'unique files')
print(all_data.filesize.sum() / PB, "PB")
print(all_data.filesize.mean() / GB, "GB avg. file size")

# ### running requests

print('---------- start requests ----------')
acs = []
dac = []
accesses = [0, 0, 0, 0]
dataaccc = [0, 0, 0, 0]
count = 0
payload = []
with requests.Session() as session:
    for index, row in all_data.iterrows():
        if count > 3000000000:
            break
        fs = row['filesize']
        payload.append({'filename': index, 'site': row['site'], 'filesize': fs, 'time': row['transfer_start']})
        # print(payload)
        try:
            if count % 100 and count > 0:
                r = session.post(service + '/simulate', json=payload)
                if r.status_code != 200:
                    print(r)
                accs = r.json()
                for i, j in enumerate(accs['counts']):
                    accesses[i] += int(j)
                    dataaccc[i] += accs['sizes'][i]
                payload = []
        except requests.exceptions.RequestException as e:
            print(e)
        if not count % 5000 and count > 0:
            # print(count, accesses, dataaccc)
            acs.append(accesses.copy())
            dac.append(dataaccc.copy())
            pacce = []
            pdata = []
            for i in range(len(accesses)):
                pacce.append(accesses[i] / sum(accesses))
                pdata.append(dataaccc[i] / sum(dataaccc))
            print(count, pacce, pdata)
        count += 1

print('final: ', accesses, dataaccc)

accdf = pd.DataFrame(acs)
dacdf = pd.DataFrame(dac)

dacdf = dacdf / (1024 * 1024 * 1024 * 1024)


# ### ploting results

accdf.columns = ['level 1', 'level 2', 'level 3', 'origin']
dacdf.columns = ['level 1', 'level 2', 'level 3', 'origin']

fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(8, 10))

# plt.subplot(211)
accdf.plot(ax=axs[0])
axs[0].set_ylabel('hits')
axs[0].set_xlabel('reqeusts [x1000]')
axs[0].legend()

dacdf.plot(ax=axs[1])
axs[1].set_ylabel('data delivered [TB]')
axs[1].set_xlabel('reqeusts [x1000]')
axs[1].legend()

# plt.show()

fig.savefig('filling_up.png')


# ### Network states

res = requests.get(service + '/status')
status = json.loads(res.json())
# print(status)
tp = []
for site in status:
    tp.append([site[0], site[1]['requests_received'], site[1]['files_delivered'], site[1]['data_delivered'] / (1024 * 1024 * 1024 * 1024)])

sites = pd.DataFrame(tp)
sites.columns = ['xcache', 'requests', 'hits', 'data delivered']
sites = sites[sites.requests != 0]
sites.head(20)

fig, ax = plt.subplots(figsize=(8, 8))

sites.plot(x="xcache", y=["requests", "hits", "data delivered"], kind="bar", ax=ax, secondary_y='data delivered')
fig.savefig('xcache_sites.png')
