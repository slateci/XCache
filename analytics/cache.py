import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('ytick', labelsize=14)


class XCache(object):
    """ as implemented in XCache """

    def __init__(self, size, lwm=0.85, hwm=0.90, max_rate_out=100 * 1024 * 1024):
        """ cache size is in bytes, max_rate_out is in bytes per second """
        self.size = size
        self.utilization = 0
        self.total_requests = 0
        self.total_hits = 0
        self.lwm = size * lwm
        self.hwm = size * hwm
        # cache record: [filesize, #accesses, time_of_firstaccess, time_of_lastaccess]
        self.cache = {}
        # this will hold rates
        self.ingress = []
        self.egress = []

    def clean_if_needed(self, filesize):
        """ a simple algo cleaning files with the lowest time_of_last_access """
        if self.utilization + filesize < self.hwm:
            return
        # print("needs cleaning...")
        df = pd.DataFrame.from_dict(self.cache, orient='index')
        df.columns = ['filesize', 'accesses', 'first access', 'last access']
        # df.sort_values(['last access'], ascending=[True], inplace=True)
        # df.sort_values(['accesses', 'last access'], ascending=[True, True], inplace=True)
        # df.sort_values(['accesses', 'filesize'], ascending=[True, False], inplace=True)
        df.sort_values(['accesses', 'last access', 'filesize'], ascending=[True, True, False], inplace=True)
        df['cum_sum'] = df.filesize.cumsum()
        print('files in cache:', df.shape[0], end='  ')
        df = df[df.cum_sum < (self.hwm - self.lwm)]
        print('files to flush:', df.shape[0])
        ftf = df.index.values
        for fn in ftf:
            self.utilization -= self.cache[fn][0]
            del self.cache[fn]

    def add_file(self, filename, filesize, transfer_start, transfer_end):
        """ returns True if cached, False if not """
        self.total_requests += 1
        # check if it was cached
        if filename in self.cache:
            self.total_hits += 1
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
        # show cache utilization vs time
        # show cache hit rate vs time
        # show age of the oldest file in cache vs time
        # show filesize distribution
        # show filesize vs accesses heat map
        pass

    def print_cache_state(self):
        """ just a summary print """
        df = pd.DataFrame.from_dict(self.cache, orient='index')
        df.columns = ['filesize', 'accesses', 'first access', 'last access']
        print(df.describe())
        print('total requests:', self.total_requests, '\ttotal hits:', self.total_hits,
              'hit probability:', self.total_hits / self.total_requests * 100, '%')
        print('cache used:', df['filesize'].sum() / 1024 / 1024 / 1024, 'GB')
        print('avg. accesses:', df['accesses'].mean())
        print('total files cached:', df.shape[0])
        pd.DataFrame.hist(df, column=['filesize', 'accesses'], bins=20)
