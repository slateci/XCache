#! /usr/bin/python
import logging

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from cache import XCacheSite

matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('ytick', labelsize=14)

step = 10000

MB = 1024 * 1024
GB = 1024 * MB
TB = 1024 * GB
PB = 1024 * TB

site = 'MWT2'
dataset = 'AUG'

site_data = pd.read_hdf("../data/" + dataset + '/' + site + '_' + dataset + '.h5', key=site, mode='r')
print(site_data.shape[0], 'files\t\t', site_data.index.unique().shape[0], 'unique files')
print(site_data)
site_data.reset_index(level=0, inplace=True)

print(site_data[site_data.filename.str.contains(".15231333.", regex=False)].filename)
sel = site_data[site_data.filename.str.contains(".15231333.", regex=False)]
print(sel.shape)
# site_data = site_data[~site_data.index.str.contains('panda')]
