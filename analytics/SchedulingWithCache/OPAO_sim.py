'''
Simulates scheduling in a realistic ATLAS computing grid.
All CEs are connected to a local XCache.
Job durations are input data are taken from historical data.
'''

import OPAO_utils as ou
import compute


def main():
    # load computing grid.
    grid = compute.Grid()

    # loop through jobs.
    # "randomly" assign to sites.

    data = ou.load_data()
    data = data[101:10101]

# TODO
# - one origin for US. One cache per other cloud and one EU origin
# - make second ce choice to be in the same cloud as the first.
# - try using 2nd choice site if 1st choice has large queue.
# - prefer large sites for large datasets.

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
