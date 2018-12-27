import pandas as pd
import OPAO_utils as ou
from cache import XCacheSite


class Grid(object):
    def __init__(self):
        self.CEs = []
        self.origins = []
        self.total_cores = 0
        self.running = 0
        self.finished = 0
        self.init()

    def init(self):
        self.loadCEs()
        self.createOrigins()

    def loadCEs(self):
        dfCEs = ou.load_compute()

        # create CEs. CEs have local caches.
        for CE in dfCEs.itertuples():
            self.CEs.append(Compute(CE[0], CE.tier, CE.cloud, CE.cores))

    def createOrigins(self):
        self.origins.append(XCacheSite('xc_US', origin=True))
        self.origins.append(XCacheSite('xc_EU', origin=True))

    def stats(self):
        print('running:', self.running, '\tfinished:', self.finished)


class Compute(object):

    def __init__(self, name, tier, cloud, cores):
        """ cache size is in bytes """
        self.name = name
        self.tier = tier
        self.cloud = cloud
        self.cores = cores

        self.running = 0
        self.queued = 0
        self.finished = 0

        self.init()

    def init(self):
        # attach cache - now scaled according to ncores, later take it from AGIS for large sites.
        xservers = self.cores // 1000
        self.cache = XCacheSite('xc_' + self.name, servers=xservers, size=20 * ou.TB)

    def add_job(self, fn, fs, ts):
        pass

    def get_ce_stats(self):
        print(self.name, '\trunning:', self.running,'\tqueued:', self.queued, '\tfinished:', self.finished)
