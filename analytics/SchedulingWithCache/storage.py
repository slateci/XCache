""" Grid Storage class """

import pandas as pd
import matplotlib.pyplot as plt
import conf
from cache import XCacheSite


class Storage(object):
    """ holds all the caches. API for adding accesses and making plots."""

    def __init__(self):
        self.storages = {}
        self.accesses = [0, 0, 0]  # endpoint, second level, xc_Origin
        self.dataaccc = [0, 0, 0]
        self.acs = []
        self.dac = []
        self.total_files = 0

    def add_storage(self, name, parent_name, servers, level=0, origin=False):
        if parent_name not in self.storages and origin is False:
            print("Parent storage has to be created first.")
        if level == 0:
            server_size = conf.CACHE_TB_PER_1K * conf.TB
        elif level == 1:
            server_size = conf.CLOUD_CACHE_TB_PER_2K * conf.TB
        else:
            server_size = 0
        self.storages[name] = XCacheSite(name, parent_name, servers=servers, size=server_size, level=level, origin=origin)

    def add_access(self, site, filename, filesize, timestamp):
        """ called by a CE. Endpoint is CE name. """

        self.total_files += 1

        # first try
        t_1 = self.storages[site]
        found = t_1.add_request(filename, filesize, timestamp)
        if found:
            self.accesses[t_1.level] += 1
            self.dataaccc[t_1.level] += filesize
            return

        # second try
        t_2 = self.storages[t_1.parent]
        found = t_2.add_request(filename, filesize, timestamp)
        if found:
            self.accesses[t_2.level] += 1
            self.dataaccc[t_2.level] += filesize
            return

        # third try
        t_3 = self.storages[t_2.parent]
        found = t_3.add_request(filename, filesize, timestamp)
        if found:
            self.accesses[t_3.level] += 1
            self.dataaccc[t_3.level] += filesize
            return

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

        if not conf.CLOUD_LEVEL_CACHE:
            accdf.drop('Cloud caches', axis=1, inplace=True)
            dacdf.drop('Cloud caches', axis=1, inplace=True)

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

        for site in self.storages:
            self.storages[site].plot_throughput()
