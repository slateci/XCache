'''
Simulates scheduling in a realistic ATLAS computing grid.
All CEs are connected to a local XCache.
Job durations are input data are taken from historical data.
'''

import OPAO_utils as ou
from grid import Grid
import cProfile


def main():
    # load computing grid.
    grid = Grid()

    # loop through jobs.
    # "randomly" assign to sites.

    data = ou.load_data(ntasks=10000)

    # creating jobs
    task_counter = 0
    for task in data.itertuples():
        grid.add_task(task)
        task_counter += 1
        if not task_counter % 500:
            print('creating tasks:', task_counter)
    print('total tasks created:', task_counter)

    # grid.plot_jobs_stats()
    grid.process_jobs()
    # cProfile.runctx('grid.process_jobs()', globals(), locals())
    grid.plot_stats()


# cProfile.run('main()', 'prof.log')
main()
