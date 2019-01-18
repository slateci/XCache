'''
Simulates scheduling in a realistic ATLAS computing grid.
All CEs are connected to a local XCache.
Job durations are input data are taken from historical data.
'''

import OPAO_utils as ou
import compute
import cProfile


def main():
    # load computing grid.
    grid = compute.Grid()

    # loop through jobs.
    # "randomly" assign to sites.

    data = ou.load_data()

    # delete Titan tasks
    data = data[data.index != 15393017]
    data = data[data.index != 15357029]
    data = data[data.index != 15345418]
    data = data[data.index != 15357036]
    data = data[data.index != 15516961]
    data = data[data.index != 15393015]

    # data = data[101:201]
    data = data[101:]
    # data = data[101:1101]
    # data = data[101:20101]
    # data = data[150000:]

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
