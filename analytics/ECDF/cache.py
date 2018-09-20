import time
import logging
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('ytick', labelsize=14)


def set_skip_tag():
    ''' to flag files we don't want to cache'''
    XCache.all_accesses['skip'] = False
    # XCache.all_accesses['skip'] = XCache.all_accesses.filesize < 102400


def clairvoyant():
    """ adds another column that gives time of the next access. """

    print('======= clarivoyant starting =======')
    gr = XCache.all_accesses.groupby('filename', axis=0)
    all = []
    # count = 0
    for filename, rest in gr:
        # if count > 1000:
            # break
        # count += 1
        r = rest.copy()
        r['filename'] = filename
        r['shifted'] = r['transfer_start'].shift(-1)
        all.append(r)
    result = pd.concat(all, ignore_index=True)
    del gr
    del all
    result.fillna(9.999999E9, inplace=True)
    XCache.all_accesses = result.sort_values('transfer_start')
    XCache.all_accesses.set_index('filename', drop=True, inplace=True)
    print('======= clairvoyant done =======')


class XCache(object):
    """ as implemented in XCache """
    MB = 1024 * 1024
    GB = 1024 * MB
    TB = 1024 * GB

    all_accesses = None

    def __init__(self, name='unnamed', size=TB, lwm=0.85, hwm=0.95, algo='LRU'):
        """ cache size is in bytes """
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.size = size
        self.lwm_bytes = size * lwm
        self.hwm_bytes = size * hwm
        self.lwm = lwm
        self.hwm = hwm
        # cache record: [filesize, #accesses, access_time]
        self.cache = {}
        self.utilization = 0
        self.total_hits = 0
        self.total_requests = 0
        self.data_from_cache = 0
        self.data_delivered = 0
        self.cleanups = 0
        self.t1 = None
        self.t2 = None
        self.algo = algo

    def get_name(self):
        ''' for naming outputfiles '''
        return self.name + '_' + str(int(self.size / XCache.GB)) + '_' + self.algo

    def run(self):
        """ this function actually does simulation """
        self.t1 = time.clock()

        done = 0
        for filename, row in XCache.all_accesses.iterrows():
            if not done % 10000:
                self.logger.debug(done)
            done += 1

            # row [filesize, transfer_start, shifted, skipped]

            filesize = row[0]

            if self.algo == 'Clairvoyant':
                access_time = row[2]
            else:
                access_time = row[1]

            cr = self.cache.get(filename)
            if cr:
                self.total_hits += 1
                self.data_from_cache += filesize
                cr[1] += 1
                cr[2] = access_time
                continue

            # was not in cache
            # if row[3]:  # if skip the cache variable was set
                # continue

            if self.utilization + filesize > self.hwm_bytes:
                # print("needs cleaning...")
                self.cleanups += 1
                self.clean()
            self.utilization += filesize
            self.cache[filename] = [filesize, 1, access_time]  # transfer_start, transfer_start]

        self.t2 = time.clock()
        self.logger.debug("done. Walltime:" + str(self.t2 - self.t1))

    def clean(self):
        """ simple algos cleaning files """
        df = pd.DataFrame.from_dict(self.cache, orient='index')
        df.columns = ['filesize', 'accesses', 'access_time']

        if self.algo == 'LRU':
            # here access time is last time file was accessed, sort it in ascending order.
            df.sort_values(['access_time'], ascending=[True], inplace=True)
        elif self.algo == 'Clairvoyant':
            # here access time is first next access. we want to sort descending
            df.sort_values(['access_time'], ascending=[False], inplace=True)
        elif self.algo == 'ALAS':
            df.sort_values(['accesses', 'access_time', 'filesize'], ascending=[True, True, False], inplace=True)
        elif self.algo == 'FS':
            df.sort_values(['filesize'], ascending=[False], inplace=True)
        elif self.algo == 'ACC':
            df.sort_values(['accesses', 'access_time'], ascending=[True, True], inplace=True)

        df['cum_sum'] = df.filesize.cumsum()
        # print('files in cache:', df.shape[0], end='  ')
        df = df[df.cum_sum < (self.hwm_bytes - self.lwm_bytes)]
        # print('files to flush:', df.shape[0])
        for fn in df.index.values:
            cr = self.cache.pop(fn)
            self.utilization -= cr[0]

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
        df.columns = ['filesize', 'accesses', 'access_time']

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

    def store_result(self):
        '''storing results into the file'''
        df = pd.DataFrame.from_dict(self.get_cache_stats(), orient='index')
        df.columns = [self.get_name()]
        df.to_hdf(self.get_name() + '_results.h5',  key=self.name, mode='w')
