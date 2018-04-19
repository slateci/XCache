import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('ytick', labelsize=14)


class XCache(object):
    """ as implemented in XCache """
    MB = 1024 * 1024
    GB = 1024 * MB
    TB = 1024 * GB

    def __init__(self, size=TB, lwm=0.85, hwm=0.90, max_rate_out=100 * 1024 * 1024):
        """ cache size is in bytes, max_rate_out is in bytes per second """
        self.size = size
        self.lwm_bytes = size * lwm
        self.hwm_bytes = size * hwm
        self.lwm = lwm
        self.hwm = hwm
        # cache record: [filesize, #accesses, time_of_firstaccess, time_of_lastaccess]
        self.cache = {}
        self.requests = []
        # this will hold rates
        self.ingress = []
        self.egress = []
        self.utilization = 0
        self.total_hits = 0
        self.total_requests = 0
        self.data_from_cache = 0
        self.data_delivered = 0
        self.per_file_counts = None
        self.cleanups = 0

    def reset(self):
        """ to be done before starting replay """
        self.cache = {}
        self.utilization = 0
        self.total_hits = 0
        self.total_requests = 0
        self.cleanups = 0
        self.data_from_cache = 0

    def set_size(self, size):
        """ full cache size in bytes. has to be set before doing replay """
        self.size = size
        self.lwm_bytes = size * self.lwm
        self.hwm_bytes = size * self.hwm

    def set_name(self, name):
        print(name)
        self.name = name

    def clean_if_needed(self, filesize):
        """ a simple algo cleaning files with the lowest time_of_last_access """
        if self.utilization + filesize < self.hwm_bytes:
            return
        # print("needs cleaning...")
        self.cleanups += 1
        df = pd.DataFrame.from_dict(self.cache, orient='index')
        df.columns = ['filesize', 'accesses', 'first access', 'last access']
        # df.sort_values(['last access'], ascending=[True], inplace=True)
        # df.sort_values(['accesses', 'last access'], ascending=[True, True], inplace=True)
        # df.sort_values(['accesses', 'filesize'], ascending=[True, False], inplace=True)
        df.sort_values(['accesses', 'last access', 'filesize'], ascending=[True, True, False], inplace=True)
        df['cum_sum'] = df.filesize.cumsum()
        # print('files in cache:', df.shape[0], end='  ')
        df = df[df.cum_sum < (self.hwm_bytes - self.lwm_bytes)]
        # print('files to flush:', df.shape[0])
        ftf = df.index.values
        for fn in ftf:
            self.utilization -= self.cache[fn][0]
            del self.cache[fn]

    def insert_file(self, filename, filesize, transfer_start, transfer_end):
        """ This is needed as files coming from ES are not sorted in time """
        self.requests.append([filename, filesize, transfer_start, transfer_end])
        return

    def replay_cache(self, clairvoyant=False):
        """ this function actually does simulation """
        self.reset()
        all_accesses = pd.DataFrame(self.requests).sort_values(2)
        all_accesses.columns = ['filename', 'filesize', 'first access', 'last access']

        self.total_requests = all_accesses.shape[0]
        self.data_delivered = all_accesses.filesize.sum()
        self.per_file_counts = all_accesses.groupby(['filename']).size().reset_index(name='counts')

        if clairvoyant:
            multiuse = self.per_file_counts[self.per_file_counts.counts > 1].filename
            all_accesses = all_accesses[all_accesses.filename.isin(multiuse)]

        for index, row in all_accesses.iterrows():
            self.add_file(row[0], row[1], row[2], row[3])

    def add_file(self, filename, filesize, transfer_start, transfer_end):
        """ returns True if cached, False if not """
        # check if it was cached
        if filename in self.cache:
            self.total_hits += 1
            self.data_from_cache += filesize
            self.cache[filename][1] += 1
            self.cache[filename][3] = transfer_end
            return True

        # was not in cache
        self.clean_if_needed(filesize)
        self.utilization += filesize
        self.cache[filename] = [filesize, 1, transfer_start, transfer_end]
        return False

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
        plt.hist(self.per_file_counts.counts, 100, log=True)
        # plt.show()
        plt.savefig(self.name + '.png')

        # show cache utilization vs time
        # show cache hit rate vs time
        # show age of the oldest file in cache vs time
        # show filesize distribution
        # show filesize vs accesses heat map

    def print_cache_state(self):
        """ just a summary print """
        df = pd.DataFrame.from_dict(self.cache, orient='index')
        df.columns = ['filesize', 'accesses', 'first access', 'last access']
        print(df.describe())
        print('total requests:', self.total_requests, '\ttotal hits:', self.total_hits,
              'hit probability:', self.total_hits / self.total_requests * 100, '%')
        print('cache used:', df['filesize'].sum() / XCache.GB, 'GB')
        print('avg. accesses (files found in cache):', df['accesses'].mean())
        print('total files cached:', df.shape[0])
        print('delivered total:', self.data_delivered / XCache.TB,
              'delivered cached:', self.data_from_cache / XCache.TB,
              'or:', self.data_from_cache / self.data_delivered * 100, '[%]')
        print('cleanups', self.cleanups)
