import time
from bisect import bisect
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('ytick', labelsize=14)

import OPAO_utils as ou
from cache import XCacheSite


class Grid(object):
    def __init__(self):
        self.CEs = {}
        self.dfCEs = None
        self.origins = []
        self.total_cores = 0
        self.status_in_time = []  # ts, running, queued, finished
        self.ds_assignements = {}
        self.JOB_START_DELAY = 1
        self.CORE_NUMBERS = [1, 4, 6, 8, 10, 12, 16, 24, 32, 48, 64, 128]
        self.all_jobs = []
        self.init()

    def init(self):
        self.loadCEs()
        self.createOrigins()

    def loadCEs(self):
        self.dfCEs = ou.load_compute()
        print(self.dfCEs.head())
        # create CEs. CEs have local caches.
        for CE in self.dfCEs.itertuples():
            self.CEs[CE[0]] = Compute(CE[0], CE.tier, CE.cloud, CE.cores)

    def createOrigins(self):
        self.origins.append(XCacheSite('xc_US', origin=True))
        self.origins.append(XCacheSite('xc_EU', origin=True))

    def get_dataset_vp(self, name):
        # TODO
        # check if name is defined at all. If not return weighted without adding to dict
        if name not in self.ds_assignements:
            self.ds_assignements[name] = self.dfCEs.sample(3, weights='cores').index.values

        # print(self.ds_assignements[name])
        return self.ds_assignements[name]

    def add_task(self, task):
        # find sites to execute task at
        sites = self.get_dataset_vp(task.dataset)
        # print('adding task:\n', task, sites)

        files_per_job = 0
        per_file_bytes = 0
        if task.files_in_ds > 0 and task.inputfiles > 0:
            files_per_job = round(task.inputfiles / task.jobs)
            per_file_bytes = round(task.ds_bytes / task.files_in_ds)

        job_duration = int(task.wall_time / task.jobs)
        cores = self.CORE_NUMBERS[bisect(self.CORE_NUMBERS, task.cores / task.jobs)]

        # print('jobs:', task.jobs, '\tcores:', cores, '\tfiles per job', files_per_job, '\tduration:', job_duration)

        file_counter = 0
        for job_number in range(task.jobs):
            files = []
            for _ in range(files_per_job):
                files.append(task.dataset + '/f' + str(file_counter % task.files_in_ds))
                file_counter += 1

            self.all_jobs.append([
                task.created_at + self.JOB_START_DELAY * job_number,
                cores,
                job_duration,
                files,
                per_file_bytes,
                sites
            ]
            )

    def process_jobs(self):
        """ gives jobs to CEs to process. """
        print('sort jobs')
        self.all_jobs.sort(key=lambda x: x[0])

        print('starting submitting...')
        counter = 0
        for job in self.all_jobs:
            sites = job[5]
            self.CEs[sites[0]].add_job(job[0], job[1], job[2], job[3], job[4])
            counter += 1
            if not counter % 1000:
                print('creating jobs:', counter)

        print('all', counter, 'jobs submitted. processing queues.')

        # loop over times
        print('start time:', time.strftime('%Y/%m/%d %H:%M:%S',  time.gmtime(self.all_jobs[0][0])))
        print('end   time:', time.strftime('%Y/%m/%d %H:%M:%S',  time.gmtime(self.all_jobs[-1][0])))
        ts = self.all_jobs[0][0]
        while True:
            ts += self.JOB_START_DELAY
            if not ts % 600:
                (srunning, squeued, sfinished) = self.stats()
                print('time:', time.strftime('%Y/%m/%d %H:%M:%S',  time.gmtime(ts)),
                      '\trunning:', srunning, '\tqueued:', squeued, '\tfinished:', sfinished)
                self.status_in_time.append([ts, srunning, squeued, sfinished])
                if sfinished == counter:
                    print('All DONE.')
                    break
            # loop over sites
            for CE in self.dfCEs.itertuples():
                self.CEs[CE[0]].process_events(ts)

    def stats(self):
        running = queued = finished = 0
        for CE in self.dfCEs.itertuples():
            running += self.CEs[CE[0]].status["running"]
            queued += self.CEs[CE[0]].status["queued"]
            finished += self.CEs[CE[0]].status["finished"]
        return (running, queued, finished)

    def plot_stats(self):

        stats = pd.DataFrame(self.status_in_time)
        stats.columns = ['time', 'running', 'queued', 'finished']
        stats.set_index('time', drop=True)
        print(stats)
        stats.index = pd.to_datetime(stats.index, unit='s')

        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(10, 9))
        fig.suptitle('Totals', fontsize=18)

        ax1.plot(stats.index, stats.running)
        ax1.set_ylabel('running')
        ax1.set_xlabel('time')
        ax1.legend()

        ax2.plot(stats.index, stats.queued)
        ax2.set_ylabel('queued')
        ax2.set_xlabel('time')
        ax2.legend()

        ax3.plot(stats.index, stats.finished)
        ax3.set_ylabel('finished')
        ax3.set_xlabel('time')
        ax3.legend()
        fig.savefig('plots/totals.png')


class Compute(object):

    def __init__(self, name, tier, cloud, cores):
        """ cache size is in bytes """
        self.name = name
        self.tier = tier
        self.cloud = cloud
        self.cores = cores

        self.finish_events = []  # [time, cores]

        self.queue = []
        self.status = {'running': 0, 'queued': 0, 'finished': 0, 'cores_used': 0}
        self.status_in_time = []

        self.init()

    def init(self):
        # attach cache - now scaled according to ncores, later take it from AGIS for large sites.
        xservers = self.cores // 1000 + 1
        self.cache = XCacheSite('xc_' + self.name, servers=xservers, size=20 * ou.TB)

    def add_job(self, ts, cores, duration, files, per_file_bytes):
        # print([ts, cores, duration, files, per_file_bytes])
        self.queue.append([ts, cores, duration, files, per_file_bytes])

    def process_events(self, ts):
        """ Process events up to and including ts. """
        # check if any jobs finished and reclaim cores.
        events_processed = 0
        for event in self.finish_events:
            if event[0] > ts:
                break
            self.status['cores_used'] -= event[1]
            self.status['finished'] += 1
            self.status['running'] -= 1
            events_processed += 1
        if events_processed:
            del self.finish_events[:events_processed]

        self.status['queued'] = 0
        jobs_started = 0
        for job in self.queue:
            if job[0] > ts:  # no jobs to execute at this time.
                break
            # print(ts, 'job starts at:', job[0])

            if (self.cores - self.status['cores_used']) < job[1]:
                # print("can't start.")
                self.status['queued'] += 1
            else:
                # print("can start.")
                self.finish_events.append([ts + job[2], job[1]])
                self.status['running'] += 1
                self.status['cores_used'] += job[1]
                jobs_started += 1
                # add files to cache
                for filen in job[3]:
                    self.cache.add_request(filen, job[4], ts)
        del self.queue[:jobs_started]

    def get_ce_stats(self):
        print(self.name, '\trunning:', self.running, '\tqueued:', self.queued, '\tfinished:', self.finished)
