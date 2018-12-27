import requests
import pandas as pd
import os

MB = 1024 * 1024
GB = 1024 * MB
TB = 1024 * GB
PB = 1024 * TB
LWM = 0.90
HWM = 0.95


def load_compute():
    exists = os.path.isfile('data/compute.h5')
    if exists:
        CEs = pd.read_hdf('compute.h5', key='AGIS', mode='r')
    else:
        # get AGIS info
        sites = []
        r = requests.get('http://atlas-agis-api.cern.ch/request/site/query/list/?json&vo_name=atlas&state=ACTIVE')
        res = r.json()
        for s in res:
            sites.append([s['name'], s['tier_level'], s['cloud']])
        print('Sites loaded.')

        sites = pd.DataFrame(sites)
        sites.columns = ['name', 'tier', 'cloud']
        print('All sites in AGIS:', sites.shape[0])

        # Get capacity
        r = requests.get('http://adc-mon.cern.ch/resources/latest.results_utilization_by_site.json')
        res = r.json()
        capacity = []
        for site in res:
            capacity.append([site, res[site]['runningWeek']])
        print('Capacities loaded.')

        capacity = pd.DataFrame(capacity)
        capacity.columns = ['name', 'cores']
        # print(capacity)

        # merging
        sites.set_index('name', drop=True, inplace=True)
        capacity.set_index('name', drop=True, inplace=True)

        all = sites.join(capacity, how='inner')

        print('mean cores per tier:\n', all.groupby(['tier'])['cores'].mean())
        print('sum of cores per tier:\n', all.groupby(['tier'])['cores'].sum())
        print('tier 0\n', all[all.tier == 0])
        print('tier 1\n', all[all.tier == 1])
        print('tier 2\n', all[all.tier == 2])
        # print('tier 3\n', sites[sites.tier == 3].head(100))
        # print(all)

        CEs = all[(all.tier != 3) & (all.cores > 200)]
        print('CEs to use:\n', CEs)

        CEs.to_hdf('data/compute.h5', key="AGIS", mode='w')
    print('CEs loaded:', CEs.shape[0])
    return CEs


def load_data(sites, periods, kinds, skipFiles=[]):

    all_data = pd.DataFrame()
    counts = []
    for site in sites:
        for month in periods:
            for kind in kinds:
                site_data = pd.read_hdf("../data/" + month + '/' + site + '_' + kind + '_' + month + '.h5', key=site, mode='r')
                site_data = site_data.astype({"transfer_start": float})
                site_data['site'] = 'xc_' + site
                nfiles = site_data.filesize.count()
                print(site, month, kind, nfiles)
                ufiles = site_data.index.unique().shape[0]
                totsize = site_data.filesize.sum() / PB
                avgfilesize = site_data.filesize.mean() / GB
                all_data = pd.concat([all_data, site_data])
                counts.append([site, month, kind, nfiles, ufiles, totsize, avgfilesize])

    df = pd.DataFrame(counts, columns=['site', 'month', 'kind', 'files', 'unique files', 'total size [PB]', 'avg. filesize [GB]'])
    print(df)

    if len(counts) == 1:
        return all_data

    print('---------- merged data -----------')
    print(all_data.shape[0], 'files\t', all_data.index.unique().shape[0], 'unique\t',
          all_data.filesize.sum() / PB, "PB\t", all_data.filesize.mean() / GB, "GB avg. file size")
    all_data = all_data.sort_values('transfer_start')

    if len(skipFiles) == 0:
        return all_data

    for rem in skipFiles:
        print('removing: ', rem)
        all_data = all_data[~all_data.index.str.contains(rem)]

    print('---------- after removing files not to cache -----------')
    print(all_data.shape[0], 'files\t', all_data.index.unique().shape[0], 'unique\t',
          all_data.filesize.sum() / PB, "PB\t", all_data.filesize.mean() / GB, "GB avg. file size")

    return all_data
