""" Storage caches classes """

import pandas as pd
import conf


class XCacheServer(object):

    def __init__(self, size=conf.TB, lwm=0.90, hwm=0.95):
        self.size = size
        self.lwm_bytes = size * lwm
        self.hwm_bytes = size * hwm
        self.lwm = lwm
        self.hwm = hwm
        self.cleanups = 0
        self.files = {}  # fn:[timestamp, acccesses, filesize]
        self.used = 0

    def add_request(self, fn, fs, ts):
        if fn in self.files:
            self.files[fn][0] = ts
            self.files[fn][1] += 1
            return True
        else:
            if self.used + fs > self.hwm_bytes:
                self.clean()
            self.files[fn] = [ts, 1, fs]
            self.used += fs
            return False

    def clean(self):
        # print("cleaning...")
        self.cleanups += 1
        sorted_by_ts = sorted(self.files)
        to_clean = self.hwm_bytes - self.lwm_bytes
        space_freed = 0
        counter = 0
        while space_freed < to_clean:
            space_freed += self.files[sorted_by_ts[counter]][2]
            del self.files[sorted_by_ts[counter]]
            counter += 1
        self.used -= space_freed
        # print('files deleted:', counter, '\tspace freed:', space_freed)

    def get_stats(self):
        df = pd.DataFrame.from_dict(self.files, orient='index')
        df.columns = ['access_time', 'accesses', 'filesize']
        return [self.cleanups, df.filesize.mean(), df.accesses.mean(), df.access_time.max() - df.access_time.mean()]


class XCacheSite(object):

    def __init__(self, name, parent,  servers=1, size=conf.TB, level=0, origin=False, lwm=0.90, hwm=0.95):
        """ cache size is in bytes """
        self.name = name
        self.parent = parent
        self.nservers = servers
        self.server_size = size
        self.lwm = lwm
        self.hwm = hwm
        self.hits = 0
        self.requests = 0
        self.data_from_cache = 0
        self.data_asked_for = 0
        self.servers = []
        self.throughput = {}
        self.origin = origin
        self.level = level
        self.init()

    def init(self):
        for _ in range(self.nservers):
            self.servers.append(XCacheServer(self.server_size, self.lwm, self.hwm))

    def add_request(self, fn, fs, ts):
        # determine server
        self.requests += 1
        self.data_asked_for += fs

        # add egress
        sizebin = fs
        timebin = ts // conf.THROUGHPUT_BIN
        while True:
            if timebin not in self.throughput:
                self.throughput[timebin] = [0, 0]
            if sizebin - conf.PER_FILE_RATE > 0:
                self.throughput[timebin][0] += conf.PER_FILE_RATE
                sizebin -= conf.PER_FILE_RATE
                timebin += 1
            else:
                self.throughput[timebin][0] += sizebin
                break

        if self.origin:
            self.hits += 1
            self.data_from_cache += fs
            return True

        server = int(fn, 16) % self.nservers
        found = self.servers[server].add_request(fn, fs, ts)
        if found:
            self.hits += 1
            self.data_from_cache += fs
        else:
            # add ingress
            sizebin = fs
            timebin = ts // conf.THROUGHPUT_BIN
            while True:
                if sizebin - conf.PER_FILE_RATE > 0:
                    self.throughput[timebin][1] += conf.PER_FILE_RATE
                    sizebin -= conf.PER_FILE_RATE
                    timebin += 1
                else:
                    self.throughput[timebin][1] += sizebin
                    break

        return found

    def get_servers_stats(self):
        data = []
        for s in self.servers:
            data.append(s.get_stats())
        df = pd.DataFrame(data)
        df.columns = ['cleanups', 'avg. filesize', 'avg. accesses', 'avg. age']
        df['site'] = self.name
        return df

    def save_throughput(self):
        df = pd.DataFrame.from_dict(self.throughput, orient='index')
        if not df.shape[0]:
            return
        df.columns = ['egress', 'ingress']
        df.index *= conf.THROUGHPUT_BIN
        df.ingress = -df.ingress
        df = df * 8 / conf.GB / conf.THROUGHPUT_BIN
        df.index = pd.to_datetime(df.index, unit='s')

        df.to_hdf(conf.BASE_DIR + 'results/' + conf.TITLE + '.h5', key='cache-' + self.name, mode='a', complevel=1)

    # def plot_cache_state(self):
    #     """ most important plots. """
    #     df = pd.DataFrame.from_dict(self.cache, orient='index')
    #     df.columns = ['filesize', 'accesses', 'first access', 'last access']

    #     plt.figure(figsize=(18, 6))
    #     plt.suptitle(self.name, fontsize=18)

    #     plt.subplot(131)
    #     plt.xlabel('filesize [MB]')
    #     plt.ylabel('count')
    #     plt.yscale('log', nonposy='clip')
    #     plt.xscale('log', nonposy='clip')
    #     plt.hist(df['filesize'], 200)

    #     plt.subplot(132)
    #     plt.xlabel('accesses (files in cache)')
    #     plt.ylabel('count')
    #     # plt.yscale('log', nonposy='clip')
    #     plt.hist(df.accesses, 100, log=True)

    #     plt.subplot(133)
    #     plt.xlabel('accesses (all files)')
    #     plt.ylabel('count')
    #     # plt.yscale('log', nonposy='clip')
    #     per_file_counts = XCache.all_accesses.groupby(['filename']).size().reset_index(name='counts')
    #     plt.hist(per_file_counts.counts, 100, log=True)
    #     # plt.show()
    #     plt.savefig(self.name + '.png')

    #     # show cache utilization vs time
    #     # show cache hit rate vs time
    #     # show age of the oldest file in cache vs time
    #     # show filesize distribution
    #     # show filesize vs accesses heat map

    # def get_cache_stats(self):
    #     """ just a summary print """
    #     df = pd.DataFrame.from_dict(self.cache, orient='index')
    #     df.columns = ['filesize', 'accesses', 'access_time']

    #     res = {
    #         'total accesses': XCache.all_accesses.shape[0],
    #         'cache hits': self.total_hits,
    #         'delivered data': XCache.all_accesses.filesize.sum() / XCache.TB,
    #         'delivered from cache': self.data_from_cache / XCache.TB,
    #         'cleanups': self.cleanups,
    #         'files in cache': df.shape[0],
    #         'avg. accesses of cached files': df['accesses'].mean(),
    #         'avg. cached file size': df['filesize'].mean() / XCache.MB,
    #     }

    #     return res

    # def store_result(self):
    #     '''storing results into the file'''
    #     df = pd.DataFrame.from_dict(self.get_cache_stats(), orient='index')
    #     df.columns = [self.get_name()]
    #     df.to_hdf(self.get_name() + '_results.h5',  key=self.name, mode='w')
