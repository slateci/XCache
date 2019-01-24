import os
import requests
import pandas as pd

import conf


def load_compute():
    filename = conf.BASE_DIR + 'data/compute.h5'
    exists = os.path.isfile(filename)
    if exists:
        CEs = pd.read_hdf(filename, key='AGIS', mode='r')
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

        all_sites = sites.join(capacity, how='inner')

        print('mean cores per tier:\n', all_sites.groupby(['tier'])['cores'].mean())
        print('sum of cores per tier:\n', all_sites.groupby(['tier'])['cores'].sum())
        print('tier 0\n', all_sites[all_sites.tier == 0])
        print('tier 1\n', all_sites[all_sites.tier == 1])
        print('tier 2\n', all_sites[all_sites.tier == 2])
        # print('tier 3\n', sites[sites.tier == 3].head(100))
        # print(all_sites)

        CEs = all_sites[(all_sites.tier != 3) & (all_sites.cores > 200)]
        print('CEs to use:\n', CEs)

        CEs.to_hdf(filename, key="AGIS", mode='w')
    print('CEs loaded:', CEs.shape[0])
    CEs = CEs.reset_index()
    return CEs


def load_data_old():

    data = pd.DataFrame()
    for jtype in conf.KINDS:
        for period in conf.PERIODS:
            pdata = pd.read_hdf(conf.BASE_DIR + 'data/full_' + jtype + '_' + period + '.h5', key=jtype, mode='r')
            print(period, pdata.shape[0])
            data = pd.concat([data, pdata])
    print('---------- merged data -----------')
    print('total tasks:', data.shape[0])
    # print(data.head())
    data = data.sort_values('created_at')
    data.created_at = (data.created_at / 1000.0).astype(int)
    data.finished_at = (data.finished_at / 1000.0).astype(int)

    print('problematic tasks:', data[(data.inputfiles > 0) & (data.files_in_ds == 0)].shape[0])
    print('excluding tasks with > 64 avg cores (Supercomputers):', data[data.cores / data.jobs > 32].shape[0])
    data = data[data.cores / data.jobs <= 64]
    return data


def load_data(ntasks=None):

    data = pd.read_hdf(conf.BASE_DIR + 'data/tasks.h5', key='tasks', mode='r')

    print('---------- data -----------')
    print('total tasks:', data.shape[0])
    # print(data.head())
    data = data.sort_values('created_at')
    data.created_at = (data.created_at / 1000.0).astype(int)
    data.finished_at = (data.finished_at / 1000.0).astype(int)

    print('problematic tasks:', data[(data.Sinputfiles > 0) & (data.ds_files == 0)].shape[0])
    print('excluding tasks with > 64 avg cores (Supercomputers):', data[data.Scores / data.jobs > 32].shape[0])
    data = data[data.Scores / data.jobs <= 64]
    return data
