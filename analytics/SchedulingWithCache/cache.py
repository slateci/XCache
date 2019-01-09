import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import conf


class Storage(object):
    """ holds all the caches. API for adding accesses and making plots."""

    def __init__(self):
        self.origin_US = XCacheSite('xc_US', origin=True)
        self.origin_EU = XCacheSite('xc_EU', origin=True)
        self.endpoints = {}
        self.accesses = [0, 0, 0]  # endpoint, xc_US, xc_EU
        self.dataaccc = [0, 0, 0]
        self.acs = []
        self.dac = []
        self.total_files = 0

    def add_cache_site(self, cloud, name, cores):
        xservers = cores // 1000 + 1
        self.endpoints[name] = XCacheSite('xc_' + name, cloud, servers=xservers, size=20 * conf.TB)

    def add_access(self, endpoint, filename, filesize, timestamp):
        self.total_files += 1
        # first try on endpoint
        found = self.endpoints[endpoint].add_request(filename, filesize, timestamp)
        if found:
            self.accesses[0] += 1
            self.dataaccc[0] += filesize
            return

        # next access through appropriate origin
        if self.endpoints[endpoint].cloud == 'US':
            self.origin_US.add_request(filename, filesize, timestamp)
            self.accesses[1] += 1
            self.dataaccc[1] += filesize
        else:
            self.origin_EU.add_request(filename, filesize, timestamp)
            self.accesses[2] += 1
            self.dataaccc[2] += filesize

    def stats(self, ts):
        print('XCache statistics:', self.accesses, self.dataaccc)
        self.acs.append([ts, self.accesses[0], self.accesses[1], self.accesses[2]])
        self.dac.append([ts, self.dataaccc[0], self.dataaccc[1], self.dataaccc[2]])

    def plot_stats(self):

        accdf = pd.DataFrame(self.acs)
        accdf.columns = ['time', 'level 1', 'origin US', 'origin EU']
        accdf = accdf.set_index('time', drop=True)
        accdf.index = pd.to_datetime(accdf.index, unit='s')

        dacdf = pd.DataFrame(self.dac)
        dacdf.columns = ['time', 'level 1', 'origin US', 'origin EU']
        dacdf = dacdf.set_index('time', drop=True)
        dacdf.index = pd.to_datetime(dacdf.index, unit='s')

        dacdf = dacdf / conf.TB

        fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 10), sharex=True,)
        fig.suptitle('Cache levels\n' + conf.TITLE, fontsize=18)

        accdf.plot(ax=axs[0][0])
        axs[0][0].set_ylabel('hits')
        axs[0][0].set_xlabel('time')
        axs[0][0].legend()

        dacdf.plot(ax=axs[1][0])
        axs[1][0].set_ylabel('data delivered [TB]')
        axs[1][0].set_xlabel('time')
        axs[1][0].legend()

        accdf = accdf.div(accdf.sum(axis=1), axis=0)
        dacdf = dacdf.div(dacdf.sum(axis=1), axis=0)

        accdf.plot(ax=axs[0][1])
        axs[0][1].set_ylabel('hits [%]')
        axs[0][1].set_xlabel('time')
        axs[0][1].grid(axis='y')
        axs[0][1].legend()

        dacdf.plot(ax=axs[1][1])
        axs[1][1].set_ylabel('data delivered [%]')
        axs[1][1].set_xlabel('time')
        axs[1][1].grid(axis='y')
        axs[1][1].legend()

        # plt.show()

        fig.autofmt_xdate()
        fig.subplots_adjust(hspace=0)

        fig.savefig(conf.BASE_DIR + 'plots_' + conf.TITLE + '/cache/filling_up.png')


class XCacheServer(object):

    def __init__(self, size=conf.TB, lwm=0.90, hwm=0.95):
        self.size = size
        self.lwm_bytes = size * lwm
        self.hwm_bytes = size * hwm
        self.lwm = lwm
        self.hwm = hwm
        self.cleanups = 0
        self.files = {}
        self.used = 0

    def add_request(self, fn, fs, ts):
        if fn in self.files:
            self.files[fn][1] += 1
            self.files[fn][2] = ts
            return True
        else:
            if self.used + fs > self.hwm_bytes:
                self.clean()
            self.files[fn] = [fs, 1, ts]
            self.used += fs
            return False

    def clean(self):
        # print("cleaning...")
        self.cleanups += 1
        df = pd.DataFrame.from_dict(self.files, orient='index')
        df.columns = ['filesize', 'accesses', 'access_time']

        # here access time is last time file was accessed, sort it in ascending order.
        df.sort_values(['access_time'], ascending=[True], inplace=True)

        df['cum_sum'] = df.filesize.cumsum()
        # print('files in cache:', df.shape[0], end='  ')
        df = df[df.cum_sum < (self.hwm_bytes - self.lwm_bytes)]
        # print('files to flush:', df.shape[0])
        for fn in df.index.values:
            cr = self.files.pop(fn)
            self.used -= cr[0]

    def get_stats(self):
        df = pd.DataFrame.from_dict(self.files, orient='index')
        df.columns = ['filesize', 'accesses', 'access_time']
        return [self.cleanups, df.filesize.mean(), df.accesses.mean(), df.access_time.max() - df.access_time.mean()]


class XCacheSite(object):

    def __init__(self, name, cloud='US',  servers=1, size=conf.TB, lwm=0.90, hwm=0.95, origin=False):
        """ cache size is in bytes """
        self.name = name
        self.cloud = cloud
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

        server = int(hashlib.md5(fn.encode('utf-8')).hexdigest(), 16) % self.nservers
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

    def plot_throughput(self):
        df = pd.DataFrame.from_dict(self.throughput, orient='index')
        df.columns = ['egress', 'ingress']
        df.index *= conf.THROUGHPUT_BIN
        # df = df[df.index > 1534626000]
        # df = df[df.index < 1534669200]
        df.ingress = -df.ingress
        df = df * 8 / conf.GB / conf.THROUGHPUT_BIN
        df.index = pd.to_datetime(df.index, unit='s')
        fig, ax = plt.subplots(figsize=(18, 6))
        fig.suptitle(self.name + '\n' + conf.TITLE, fontsize=18)
        fig.autofmt_xdate()
        ax.set_ylabel('throughput [Gbps]')
        df.plot(kind='line', ax=ax)
        fig.savefig(conf.BASE_DIR + 'plots_' + conf.TITLE + '/cache/thr_' + self.name + '.png')

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
