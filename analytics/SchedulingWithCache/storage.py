""" Grid Storage class """

import pandas as pd
import matplotlib.pyplot as plt
import conf
from cache import XCacheSite


class Storage(object):
    """ holds all the caches. API for adding accesses and making plots."""

    def __init__(self):
        self.origin = XCacheSite('Data Lake', origin=True)
        self.cloud_caches = {}
        self.endpoints = {}
        self.accesses = [0, 0, 0]  # endpoint, second level, xc_Origin
        self.dataaccc = [0, 0, 0]
        self.acs = []
        self.dac = []
        self.total_files = 0

    def add_cloud_cache(self, cloud, name, cores):
        xservers = cores // 1000 + 1
        self.cloud_caches[name] = XCacheSite('xc_' + name, cloud, servers=xservers, size=conf.CLOUD_CACHE_TB_PER_1K * conf.TB)

    def add_cache_endpoint(self, cloud, name, cores):
        xservers = cores // 1000 + 1
        self.endpoints[name] = XCacheSite('xc_' + name, cloud, servers=xservers, size=conf.CACHE_TB_PER_1K * conf.TB)

    def add_access(self, endpoint, filename, filesize, timestamp):
        self.total_files += 1
        # first try on endpoint
        found = self.endpoints[endpoint].add_request(filename, filesize, timestamp)
        if found:
            self.accesses[0] += 1
            self.dataaccc[0] += filesize
            return

        # next access through cloud cache
        cloud = self.endpoints[endpoint].cloud
        found = self.cloud_caches[cloud].add_request(filename, filesize, timestamp)
        if found:
            self.accesses[1] += 1
            self.dataaccc[1] += filesize
            return

        # next access through the origin
        self.origin.add_request(filename, filesize, timestamp)
        self.accesses[2] += 1
        self.dataaccc[2] += filesize

    def stats(self, ts):
        print('XCache statistics:', self.accesses, self.dataaccc)
        self.acs.append([ts, self.accesses[0], self.accesses[1], self.accesses[2]])
        self.dac.append([ts, self.dataaccc[0], self.dataaccc[1], self.dataaccc[2]])

    def plot_stats(self):

        accdf = pd.DataFrame(self.acs)
        accdf.columns = ['time', 'Site caches', 'Cloud caches', 'Data Lake']
        accdf = accdf.set_index('time', drop=True)
        accdf.index = pd.to_datetime(accdf.index, unit='s')

        dacdf = pd.DataFrame(self.dac)
        dacdf.columns = ['time', 'Site caches', 'Cloud caches', 'Data Lake']
        dacdf = dacdf.set_index('time', drop=True)
        dacdf.index = pd.to_datetime(dacdf.index, unit='s')

        dacdf = dacdf / conf.TB

        fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 10), sharex=True,)
        fig.suptitle('Cache levels\n' + conf.TITLE.replace("_", " "), fontsize=18)

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

        self.origin.plot_throughput()

        for cloud in self.cloud_caches:
            self.cloud_caches[cloud].plot_throughput()

        for site in self.endpoints:
            self.endpoints[site].plot_throughput()
