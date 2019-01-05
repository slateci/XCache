'''
Simulates scheduling in a realistic ATLAS computing grid.
All CEs are connected to a local XCache.
Job durations are input data are taken from historical data. 
'''

import pandas as pd

import OPAO_utils as ou
import compute
from cache import XCacheSite


# load computing grid.
grid = compute.Grid()

# loop through jobs.
# "randomly" assign to sites.

PERIODS = ['SEP', 'OCT', 'NOV']  # must be listed in order
KINDS = ['prod']  # anal
DONT_CACHE = []
data = ou.load_data(PERIODS, KINDS)

data = data[101:1000]

# creating jobs
counter = 0
for task in data.itertuples():
    grid.add_task(task)
    counter += 1
    if not counter % 500:
        print('creating tasks:', counter)
print('total tasks created:', counter)

grid.process_jobs()
grid.plot_stats()

#     fs = row.filesize
#     ts = row.transfer_start
#     l0 = all_sites[row.site]
#     found = l0.add_request(index, fs, ts)
#     if found:
#         accesses[0] += 1
#         dataaccc[0] += fs
#         continue

#     l1 = all_sites[l0.upstream]
#     found = l1.add_request(index, fs, ts)
#     if found:
#         accesses[1] += 1
#         dataaccc[1] += fs
#         continue

#     l2 = all_sites[l1.upstream]
#     found = l2.add_request(index, fs, ts)
#     if found:
#         accesses[2] += 1
#         dataaccc[2] += fs
#         continue

#     l3 = all_sites[l2.upstream]
#     found = l3.add_request(index, fs, ts)
#     if found:
#         accesses[3] += 1
#         dataaccc[3] += fs
#         continue
