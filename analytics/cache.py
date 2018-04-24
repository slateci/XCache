import time
import logging
import threading
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('ytick', labelsize=14)


class XCache(threading.Thread):
    """ as implemented in XCache """
    MB = 1024 * 1024
    GB = 1024 * MB
    TB = 1024 * GB

    all_accesses = None

    def __init__(self, name='unnamed', size=TB, lwm=0.85, hwm=0.90, max_rate_out=100 * 1024 * 1024):
        """ cache size is in bytes, max_rate_out is in bytes per second """
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.size = size
        self.lwm_bytes = size * lwm
        self.hwm_bytes = size * hwm
        self.lwm = lwm
        self.hwm = hwm
        # cache record: [filesize, #accesses, time_of_firstaccess, time_of_lastaccess]
        self.cache = {}
        # this will hold rates
        self.ingress = []
        self.egress = []
        self.utilization = 0
        self.total_hits = 0
        self.total_requests = 0
        self.data_from_cache = 0
        self.data_delivered = 0
        self.cleanups = 0
        self.t1 = None
        self.t2 = None

    def clairvoyant(self):
        """ sets a flag that means that file won't be needed again."""
        # needs fix
        pass
        # multiuse = self.per_file_counts[self.per_file_counts.counts > 1].filename
        # self.all_accesses = self.all_accesses[all_accesses.filename.isin(multiuse)]
        # self.per_file_counts = self.all_accesses.groupby(['filename']).size().reset_index(name='counts')

    def run(self):
        """ this function actually does simulation """
        self.t1 = time.clock()

        done = 0
        for index, row in XCache.all_accesses.iterrows():
            if not done % 10000:
                self.logger.debug(done)
            done += 1
            filename = index
            filesize = row[0]
            transfer_start = row[1]
            if filename in self.cache:
                self.total_hits += 1
                self.data_from_cache += filesize
                self.cache[filename][1] += 1
                self.cache[filename][3] = transfer_start
                continue
            # was not in cache
            if self.utilization + filesize > self.hwm_bytes:
                # print("needs cleaning...")
                self.cleanups += 1
                self.clean()
            self.utilization += filesize
            self.cache[filename] = [filesize, 1, transfer_start, transfer_start]

        self.t2 = time.clock()
        self.logger.debug("done. Walltime:" + str(self.t2 - self.t1))

    def clean(self):
        """ simple algos cleaning files """
        df = pd.DataFrame.from_dict(self.cache, orient='index')
        df.columns = ['filesize', 'accesses', 'first access', 'last access']
        # df.sort_values(['last access'], ascending=[True], inplace=True)
        # df.sort_values(['accesses', 'last access'], ascending=[True, True], inplace=True)
        # df.sort_values(['accesses', 'filesize'], ascending=[True, False], inplace=True)
        df = df.sort_values(['accesses', 'last access', 'filesize'], ascending=[True, True, False], inplace=False)
        df['cum_sum'] = df.filesize.cumsum()
        # print('files in cache:', df.shape[0], end='  ')
        df = df[df.cum_sum < (self.hwm_bytes - self.lwm_bytes)]
        # print('files to flush:', df.shape[0])
        for fn in df.index.values:
            self.utilization -= self.cache[fn][0]
            del self.cache[fn]

    def plot_cache_state(self):
        """ most important plots. """
        df = pd.DataFrame.from_dict(self.cache, orient='index')
        df.columns = ['filesize', 'accesses', 'first access', 'last access']

        plt.figure(figsize=(18, 6))
        plt.suptitle(self.name, fontsize=18)

        plt.subplot(131)
        plt.xlabel('filesize [MB]')
        plt.ylabel('count')
        plt.yscale('log', nonposy='clip')
        plt.xscale('log', nonposy='clip')
        plt.hist(df['filesize'], 200)

        plt.subplot(132)
        plt.xlabel('accesses (files in cache)')
        plt.ylabel('count')
        # plt.yscale('log', nonposy='clip')
        plt.hist(df.accesses, 100, log=True)

        plt.subplot(133)
        plt.xlabel('accesses (all files)')
        plt.ylabel('count')
        # plt.yscale('log', nonposy='clip')
        per_file_counts = XCache.all_accesses.groupby(['filename']).size().reset_index(name='counts')
        plt.hist(per_file_counts.counts, 100, log=True)
        # plt.show()
        plt.savefig(self.name + '.png')

        # show cache utilization vs time
        # show cache hit rate vs time
        # show age of the oldest file in cache vs time
        # show filesize distribution
        # show filesize vs accesses heat map

    def get_cache_stats(self):
        """ just a summary print """
        df = pd.DataFrame.from_dict(self.cache, orient='index')
        df.columns = ['filesize', 'accesses', 'first access', 'last access']

        res = {
            'total accesses': XCache.all_accesses.shape[0],
            'cache hits': self.total_hits,
            'delivered data': XCache.all_accesses.filesize.sum() / XCache.TB,
            'delivered from cache': self.data_from_cache / XCache.TB,
            'cleanups': self.cleanups,
            'files in cache': df.shape[0],
            'avg. accesses of cached files': df['accesses'].mean(),
            'avg. cached file size': df['filesize'].mean() / XCache.MB,
            'walltime': self.t2 - self.t1
        }

        return res
