'''
Simulates scheduling in a realistic ATLAS computing grid.
All CEs are connected to a local XCache.
Job durations are input data are taken from historical data.
'''

# import cProfile

import OPAO_utils as ou
from grid import Grid


def run():
    # load computing grid.
    grid = Grid()

    # loop through jobs.
    # "randomly" assign to sites.

    data = ou.load_data()#(ntasks=10001)

    # creating jobs
    task_counter = 0
    for task in data.itertuples():
        grid.add_task(task)
        task_counter += 1
        if not task_counter % 1000:
            print('creating tasks:', task_counter)

        if not task_counter % 10000:
            grid.process_jobs(until=task.created_at)
    print('total tasks created:', task_counter)

    grid.process_jobs()  # finish the rest
    # cProfile.runctx('grid.process_jobs()', globals(), locals())

    grid.save_stats()


# cProfile.run('main()', 'prof.log')
if __name__ == '__main__':
    run()
