'''
Simulates scheduling in a realistic ATLAS computing grid.
All CEs are connected to a local XCache.
Job durations are input data are taken from historical data.
'''

# import pandas as pd

import OPAO_utils as ou
import compute
# from cache import XCacheSite

PERIODS = ['SEP', 'OCT', 'NOV']  # must be listed in order
KINDS = ['prod']  # anal
DONT_CACHE = []


def main():
    # load computing grid.
    grid = compute.Grid()

    # loop through jobs.
    # "randomly" assign to sites.

    data = ou.load_data(PERIODS, KINDS)
    data = data[101:1101]

# TODO
# - check all cache levels are used
# - add plotting of cache results
# - try using 2nd choice site if 1st choice has large queue

    # creating jobs
    task_counter = 0
    for task in data.itertuples():
        grid.add_task(task)
        task_counter += 1
        if not task_counter % 500:
            print('creating tasks:', task_counter)
    print('total tasks created:', task_counter)
    grid.process_jobs()

    grid.plot_stats()


main()
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
