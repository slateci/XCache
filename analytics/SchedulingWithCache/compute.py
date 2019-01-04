from bisect import bisect
import pandas as pd
import OPAO_utils as ou
from cache import XCacheSite


class Grid(object):
    def __init__(self):
        self.CEs = {}
        self.dfCEs = None
        self.origins = []
        self.total_cores = 0
        self.running = 0
        self.finished = 0
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
        # print(task, sites)

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

        print('all job submitted. processing queues.')
        # loop over times
        for ts in range(self.all_jobs[0][0], self.all_jobs[-1][0] + 86400, self.JOB_START_DELAY):
            if not ts % 60:
                print(ts)
            # loop over sites
            for CE in self.dfCEs.itertuples():
                self.CEs[CE[0]].process_events(ts)

    def stats(self):
        print('running:', self.running, '\tfinished:', self.finished)


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
        self.queue.append([ts, cores, duration, files, per_file_bytes])

    def process_events(self, ts):
        """ Process events up to and including ts. """
        # check if any jobs finished and reclaim cores.
        for event in self.finish_events:
            if event[0] > ts:
                continue
            self.status['cores_used'] -= event[1]
            self.status['finished'] += 1
            self.status['running'] -= 1

        self.status['queued'] = 0
        for job in self.queue:
            if job[0] > ts:  # no jobs to execute at this time.
                break

            if (self.cores - self.status['cores_used']) < job[1]:
                # print("can't start.")
                self.status['queued'] += 1
            else:
                # print("can start.")
                self.finish_events.append([ts + job[2], job[1]])
                self.status['running'] += 1
                self.status['cores_used'] += job[1]

                # add files to cache
                for filen in job[3]:
                    self.cache.add_request(filen, job[4], ts)

    def get_ce_stats(self):
        print(self.name, '\trunning:', self.running, '\tqueued:', self.queued, '\tfinished:', self.finished)
