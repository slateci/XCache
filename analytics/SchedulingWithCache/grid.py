""" combines both compute and storage """

# from bisect import bisect
import time
import hashlib
import multiprocessing

import OPAO_utils as ou
import conf
from storage import Storage
from compute import Compute
from sampler import Sampler
import pandas as pd


class Grid(object):
    def __init__(self):
        self.comp_sites = []
        self.dfCEs = None
        self.storage = Storage()
        self.total_cores = 0
        self.status_in_time = []  # ts, running, queued, finished
        self.ds_assignements = {}
        self.all_jobs = []

        self.core_seconds = 0
        self.queue_seconds = 0

        self.cloud_weights = None
        self.site_weights = {}
        self.create_infrastructure()
        self.samples = multiprocessing.Queue()
        self.init()

    def init(self):
        sampler = Sampler(self.cloud_weights, self.site_weights, self.samples)
        sampler.daemon = True
        sampler.start()
        if conf.STEPS_TO_FILE:
            self.logfile = open(conf.BASE_DIR + conf.TITLE + ".log", "w", buffering=1)

    def create_infrastructure(self):

        self.dfCEs = ou.load_compute()
        self.total_cores = self.dfCEs.cores.sum()
        print('total cores:', self.total_cores)

        # create origin server
        self.storage.add_storage('Data Lake', parent_name='', servers=1, level=2, origin=True)

        # create cloud level cache servers
        self.cloud_weights = self.dfCEs.groupby('cloud').sum()['cores']
        print(self.cloud_weights)

        if conf.CLOUD_LEVEL_CACHE:
            for cloud, sum_cores in self.cloud_weights.items():
                servers = sum_cores // 2000 + 1
                self.storage.add_storage(cloud, parent_name='Data Lake', servers=servers, level=1, origin=False)

        # create CEs. CEs have local caches.
        for ce in self.dfCEs.itertuples():
            servers = ce.cores // 1000 + 1
            if conf.CLOUD_LEVEL_CACHE:
                p_name = ce.cloud
            else:
                p_name = 'Data Lake'
            self.storage.add_storage(ce.name, parent_name=p_name, servers=servers, level=0, origin=False)
            self.comp_sites.append(Compute(ce.name, ce.tier, ce.cloud, ce.cores, self.storage, ce.name))

        # calculate site weights
        self.cloud_weights /= self.cloud_weights.sum()
        for cl, clv in self.dfCEs.groupby('cloud'):
            self.site_weights[cl] = clv['cores']
            self.site_weights[cl] /= self.site_weights[cl].sum()
        # print(self.cloud_weights,  self.site_weights)

    def get_dataset_vp(self, name):

        if name in self.ds_assignements:
            return self.ds_assignements[name]

        # if len(self.cloud_samples) == 0:
        #     self.cloud_samples = self.cloud_weights.sample(10000, replace=True, weights=self.cloud_weights).index.values.tolist()
        # cs = self.cloud_samples.pop()
        # sw = self.site_weights[cs]
        # site_samples = set(sw.sample(min(len(sw), conf.MAX_CES_PER_TASK), weights=sw).index.values)

        site_samples = self.samples.get()
        # print(site_samples)

        if name is None:  # We have a lot of tasks without dataset. Throw them randomly.
            return site_samples

        self.ds_assignements[name] = site_samples
        return site_samples

    def add_task(self, task):
        # find sites to execute task at
        sites = self.get_dataset_vp(task.dataset)
        # print('adding task:\n', task, sites)

        files_per_job = 0
        per_file_bytes = 0
        if task.ds_files > 0 and task.Sinputfiles > 0:
            files_per_job = round(task.Sinputfiles / task.jobs)
            per_file_bytes = round(task.ds_size / task.ds_files)

        job_duration = int(task.Swall_time / task.jobs)
        # cores = conf.CORE_NUMBERS[bisect(conf.CORE_NUMBERS, task.cores / task.jobs)]
        cores = int(round(task.Scores / task.jobs))

        # print('jobs:', task.jobs, '\tcores:', cores, '\tfiles per job', files_per_job, '\tduration:', job_duration)

        file_counter = 0
        for job_number in range(task.jobs):
            files = []
            for _ in range(files_per_job):
                fn = task.dataset + str(file_counter % task.ds_files)
                fn = hashlib.md5(fn.encode('utf-8')).hexdigest()
                files.append(fn)
                file_counter += 1

            self.all_jobs.append((
                task.created_at + conf.JOB_START_DELAY * job_number,
                cores,
                job_duration,
                files,
                per_file_bytes,
                sites,
                task.taskid
            )
            )

    def process_jobs(self, until=None):
        """ gives jobs to CEs to process. 
        If until is given only jobs starting up to that time will be processed.
        This is to spare memory.
        """

        print('sort jobs')
        self.all_jobs.sort(key=lambda x: x[0])
        total_jobs = len(self.all_jobs)
        print('jobs to do:', total_jobs)

       # loop over times
        print('start time:', time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(self.all_jobs[0][0])))
        print('end   time:', time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(self.all_jobs[-1][0])))
        ts = (self.all_jobs[0][0] - conf.STEP) // conf.STEP * conf.STEP
        while True:
            if until and ts >= until:
                print('remaining jobs:', len(self.all_jobs))
                return
            ts += conf.STEP
            if not ts % conf.BINS:
                self.storage.stats(ts)
                remain = self.stats(ts)
                print('remaining jobs: ', remain)
                if remain == 0 and until is None:
                    print('All DONE.')
                    break

            # loop over sites process events get ce statuses
            for ce in self.comp_sites:
                ncores, nqueued = ce.process_events(ts)
                self.core_seconds += ncores * conf.STEP
                self.queue_seconds += nqueued * conf.STEP

            jobs_added = 0
            for job in self.all_jobs:
                if job[0] > ts + conf.STEP:
                    break
                sites = job[5]

                # the first site not having anything in the queue gets the job
                found_empty = False
                minocc = 99999999.0
                minsite = 999
                for site in sites:
                    occ = len(self.comp_sites[site].queue) / self.comp_sites[site].cores
                    if not occ:
                        self.comp_sites[site].add_job(job[0], job[1], job[2], job[3], job[4], job[6])
                        found_empty = True
                        break
                    if occ < minocc:
                        minocc = occ
                        minsite = site

                # if job unassigned give it to the one with the smallest ratio
                if not found_empty:
                    self.comp_sites[minsite].add_job(job[0], job[1], job[2], job[3], job[4], job[6])

                jobs_added += 1

            # print('deleting:', jobs_added, 'from:', len(self.all_jobs))
            del self.all_jobs[:jobs_added]

    def stats(self, ts):
        """ returns sum of running and queued jobs so we can say when the emulation is done """
        srunning = susedcores = squeued = sfinished = 0
        for ce in self.comp_sites:
            (runn, queu, fini, core) = ce.collect_stats(ts)
            srunning += runn
            squeued += queu
            sfinished += fini
            susedcores += core
        self.status_in_time.append([ts, srunning, squeued, sfinished, susedcores])
        print('time:', time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(ts)),
              '\trunning:', srunning, '\t cores used:',
              susedcores, '\tqueued:', squeued, '\tfinished:', sfinished)
        if conf.STEPS_TO_FILE:
            self.logfile.write(time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(ts)) +
                               '\trunning:' + str(srunning) + '\t cores used:' +
                               str(susedcores) + '\tqueued:' + str(squeued) + '\tfinished:' + str(sfinished) + '\n')
        return srunning + squeued

    def save_stats(self):
        print('core hours:', self.core_seconds / 3600)
        print('queue job hours:', self.queue_seconds / 3600)
        stats = pd.DataFrame(self.status_in_time)
        stats.columns = ['time', 'running', 'queued', 'finished', 'cores used']
        stats['cores used'] /= self.total_cores
        stats['finished'] /= stats.finished.max()
        stats = stats.set_index('time', drop=True)
        stats.index = pd.to_datetime(stats.index, unit='s')
        stats.to_hdf(conf.BASE_DIR + 'results/' + conf.TITLE + '.h5', key='compute', mode='a', complevel=1)
        # print(stats)

        summary = pd.DataFrame.from_dict({
            'core hours': self.core_seconds / 3600,
            'queue hours': self.queue_seconds / 3600
        }, orient='index')
        summary.to_hdf(conf.BASE_DIR + 'results/' + conf.TITLE + '.h5', key='summary', mode='a')

        dic = globals().get('conf', None).__dict__
        for k in dic.keys():
            if k.startswith('s_'):
                dic.pop(k)
        conf_df = pd.DataFrame.from_dict(dic, orient='index')
        conf_df.to_hdf(conf.BASE_DIR + 'results/' + conf.TITLE + '.h5', key='config', mode='a')

        task_finish_times = {}
        for ce in self.comp_sites:
            ce.save_stats()
            for tid, ftime in ce.task_finish_times.items():
                if tid not in task_finish_times:
                    task_finish_times[tid] = ftime
                else:
                    if task_finish_times[tid] < ftime:
                        task_finish_times[tid] = ftime

        self.storage.save_stats()
        tft = pd.DataFrame.from_dict(task_finish_times, orient='index')
        tft.columns = ['model_finish']
        tft.to_hdf(conf.BASE_DIR + 'results/' + conf.TITLE + '.h5', key='tft', mode='a', complevel=1)
