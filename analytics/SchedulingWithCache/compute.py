""" here all grid sites and processing """

import conf
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rc('xtick', labelsize=12)
matplotlib.rc('ytick', labelsize=14)


class Compute(object):

    def __init__(self, name, tier, cloud, cores, storage, cache):
        """ cache size is in bytes """
        self.name = name
        self.tier = tier
        self.cloud = cloud
        self.cores = cores
        self.storage = storage
        self.cache = cache
        self.finish_events = []  # [time, cores]

        self.queue = []

        self.srunning = self.squeued = self.sfinished = self.scores_used = 0
        self.status_in_time = []

    def add_job(self, ts, cores, duration, files, per_file_bytes):
        # print([ts, cores, duration, files, per_file_bytes])
        self.queue.append([ts, cores, duration, files, per_file_bytes])

    def process_events(self, ts):
        """ Process events up to and including ts. """
        # check if any jobs finished and reclaim cores.
        events_processed = 0
        for event in self.finish_events:
            # finish event[0] - time to finish
            # finihs event[1] - cores it used
            if event[0] > ts:
                break
            self.scores_used -= event[1]
            self.srunning -= 1
            self.sfinished += 1
            events_processed += 1
        if events_processed:
            del self.finish_events[:events_processed]

        jobs_started = 0
        for job in self.queue:
            # job[0] - start time
            # job[1] - cores it need
            # job[2] - duration of job
            # job[3] - list of files to access
            if job[0] > ts:  # no jobs to execute at this time.
                break
            # print(ts, 'job starts at:', job[0])

            if (self.cores - self.scores_used) < job[1]:
                # print("site full.")
                break
            else:
                # print("can start.")
                jobs_started += 1
                self.srunning += 1
                self.scores_used += job[1]
                self.finish_events.append([ts + job[2], job[1]])
                # add files to cache
                for filen in job[3]:
                    self.storage.add_access(self.cache, filen, job[4], ts)

        # remove jobs that have been started from the queue
        del self.queue[:jobs_started]

        return (self.scores_used, len(self.queue))

    def process_events_old(self, ts):
        """ Process events up to and including ts. """
        # check if any jobs finished and reclaim cores.
        events_processed = 0
        for event in self.finish_events:
            # finish event[0] - time to finish
            # finihs event[1] - cores it used
            if event[0] > ts:
                break
            self.scores_used -= event[1]
            self.srunning -= 1
            self.sfinished += 1
            events_processed += 1
        if events_processed:
            del self.finish_events[:events_processed]

        jobs_started = []
        self.squeued = 0
        for ji, job in enumerate(self.queue):
            # job[0] - start time
            # job[1] - cores it need
            # job[2] - duration of job
            if job[0] > ts:  # no jobs to execute at this time.
                break
            # print(ts, 'job starts at:', job[0])

            if (self.cores - self.scores_used) < job[1]:
                # print("can't start.")
                self.squeued += 1
            else:
                # print("can start.")
                self.finish_events.append([ts + job[2], job[1]])
                self.srunning += 1
                self.scores_used += job[1]
                jobs_started.append(ji)
                # add files to cache
                for filen in job[3]:
                    self.storage.add_access(self.cache, filen, job[4], ts)

        # remove jobs that have been started from the queue
        for ji in jobs_started:
            del self.queue[ji]

        return (self.scores_used, self.squeued)

    def collect_stats(self, ts):
        # self.status_in_time.append([ts, self.srunning, self.squeued, self.sfinished, self.scores_used])
        self.status_in_time.append([ts, self.srunning, len(self.queue), self.sfinished, self.scores_used])
        # print(self.name, '\trunning:', self.srunning, '\tqueued:', self.squeued, '\tfinished:', self.sfinished)
        return (self.srunning, len(self.queue), self.sfinished, self.scores_used)

    def plot_stats(self):
        stats = pd.DataFrame(self.status_in_time)
        stats.columns = ['time', 'running', 'queued', 'finished', 'cores_used']
        stats = stats.set_index('time', drop=True)
        stats.index = pd.to_datetime(stats.index, unit='s')

        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=False, figsize=(8, 9))
        fig.suptitle(self.name + '\n' + conf.TITLE.replace('_', ' '), fontsize=18)

        ax1.plot(stats.index, stats.running)
        ax1.plot(stats.index, stats.queued)
        ax1.set_ylabel('jobs')
        ax1.legend()

        ax2.plot(stats.index, stats.finished)
        ax2.set_ylabel('finished')
        ax2.set_xlabel('time')
        # ax2.legend()

        ax3.plot(stats.index, stats.cores_used)
        ax3.set_ylabel('cores used')
        ax3.set_xlabel('time')
        # ax3.legend()

        fig.autofmt_xdate()
        fig.subplots_adjust(hspace=0)

        fig.savefig(conf.BASE_DIR + 'plots_' + conf.TITLE + '/' + self.name + '.png')
        plt.close(fig)
