#!/usr/bin/env python3.6

import os
# import sys
# from glob import glob
import time
# from datetime import datetime
import shutil


class Xdisks:
    def __init__(self):
        self.HOTS = []
        self.COLDS = []
        self.META = []
        self.last_update = None
        self.setup()
        self.update()

    def setup(self):
        mpts = []
        for k in dict(os.environ):
            if k.startswith('DISK'):
                mpts.append(os.environ[k])

        for i in range(len(mpts)):
            lwm, hwm = (0.4, 0.6)
            if 'XC_HOT_HWM_' + str(i) in os.environ:
                hwm = float(os.environ['XC_HOT_HWM_' + str(i)])
            if 'XC_HOT_LWM_' + str(i) in os.environ:
                lwm = float(os.environ['XC_HOT_LWM_' + str(i)])
            if 'XC_HOT_' + str(i) in os.environ:
                path = os.environ['XC_HOT_' + str(i)]
                if path in mpts:
                    mpts.remove(path)
                self.HOTS.append(Xdisk(path, lwm, hwm))

        for path in mpts:
            self.COLDS.append(Xdisk(path))

        self.META.append(Xdisk('/xcache-meta'))

    def update(self):
        file_path = '/proc/diskstats'
        # ref: http://lxr.osuosl.org/source/Documentation/iostats.txt
        columns_disk = ['m', 'mm', 'dev', 'reads', 'rd_mrg', 'rd_sectors',
                        'ms_reading', 'writes', 'wr_mrg', 'wr_sectors',
                        'ms_writing', 'cur_ios', 'ms_doing_io', 'ms_weighted']
        lines = open(file_path, 'r').readlines()
        self.last_update = time.time()
        for line in lines:
            if line == '':
                continue
            split = line.split()
            if len(split) != len(columns_disk):
                continue
            data = dict(zip(columns_disk, split))
            # change values to ints.
            for key in data:
                if key != 'dev':
                    data[key] = int(data[key])
            # get Xdisk with this data['dev'] device and set values
            for DISK in self.COLDS + self.HOTS + self.META:
                if DISK.device == data['dev']:
                    if self.last_update and DISK.iostat_previous:
                        for k in data:
                            if k == 'dev':
                                continue
                            DISK.iostat[k] = data[k] - DISK.iostat_previous[k]
                        # this is not incremented
                        DISK.iostat['cur_ios'] = data['cur_ios']
                    DISK.iostat_previous = data
                    break

    def report(self):
        for DISK in self.COLDS + self.HOTS + self.META:
            print(DISK)
        print('--------------------------------------')


class Xdisk:
    def __init__(self, path, lwm=0.95, hwm=0.98):
        self.path = path
        self.lwm = lwm
        self.hwm = hwm
        self.device = ''
        self.iostat_previous = {}
        self.iostat = {}
        self.set_device()

    def __str__(self):
        res = '{:20} device: {:10} used: {}% '.format(self.path, self.device, int(self.get_utilization() * 100))
        res += 'reads: {} writes: {} cur_IOs: {} ms_reading: {}, ms_writing: {}, ms_io: {}'.format(
            self.iostat['reads'], self.iostat['writes'], self.iostat['cur_ios'],
            self.iostat['ms_reading'], self.iostat['ms_writing'], self.iostat['ms_doing_io'])
        return res

    def get_space(self):
        return shutil.disk_usage(self.path)

    def get_utilization(self):
        (total, used, free) = shutil.disk_usage(self.path)
        return used / total

    def get_free_space(self):
        (total, used, free) = shutil.disk_usage(self.path)
        return free

    def set_device(self):
        file_path = '/etc/mtab'
        lines = open(file_path, 'r').readlines()
        for line in lines:
            if line == '':
                continue
            w = line.split(' ')
            if w[1] == self.path:
                self.device = w[0].replace('/dev/', '')
                break

# def get_load():
#     return os.getloadavg()


if __name__ == "__main__":
    xd = Xdisks()
    while True:
        xd.update()
        xd.report()
        time.sleep(60)
