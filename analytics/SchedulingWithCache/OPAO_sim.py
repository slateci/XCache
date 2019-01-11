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
    data = data[101:201]
    # data = data[101:1101]
    # data = data[101:20101]

# TODO
# - one origin for US. One cache per other cloud and one EU origin

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
