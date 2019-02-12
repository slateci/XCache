import multiprocessing
import time

import conf


class Sampler(multiprocessing.Process):

    def __init__(self, cloud_weights, site_weights, result_queue):
        multiprocessing.Process.__init__(self)
        self.cloud_weights = cloud_weights
        self.site_weights = site_weights
        self.result_queue = result_queue
        self.cloud_samples = []

    def run(self):
        # proc_name = self.name
        while True:
            if self.result_queue.qsize() > 15000:
                time.sleep(1)
                # print(self.name, 'sleeping')
                continue

            if not self.cloud_samples:
                self.cloud_samples = self.cloud_weights.sample(10000, replace=True, weights=self.cloud_weights).index.values.tolist()

            cs = self.cloud_samples.pop()
            sw = self.site_weights[cs]
            site_samples = set(sw.sample(min(len(sw), conf.MAX_CES_PER_TASK), weights=sw).index.values)

            self.result_queue.put(site_samples)
