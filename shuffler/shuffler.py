#!/usr/bin/env python3.6

import os
import sys
from glob import glob
import struct
import time
from datetime import datetime
import shutil

BASE_DIR = '/xcache-meta/namespace'
# BASE_DIR = '/xcache-meta/xrdcinfos/meta'


class Xdisk:
    def __init__(self, path, lwm=0.95, hwm=0.98):
        self.path = path
        self.lwm = lwm
        self.hwm = hwm

    def __str__(self):
        return 'disk: {} utilization: {}%'.format(self.path, int(self.get_utilization() * 100))

    def get_utilization(self):
        (total, used, free) = shutil.disk_usage(self.path)
        return used / total

    def get_free_space(self):
        (total, used, free) = shutil.disk_usage(self.path)
        return free


COLDS = []
HOTS = []

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
        HOTS.append(Xdisk(path, lwm, hwm))

for path in mpts:
    COLDS.append(Xdisk(path))


def countSetBits(n):
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count


def get_file_info(filename):

    fin = open(filename, "rb")

    _, = struct.unpack('i', fin.read(4))
    # print ("file version:", _)
    bs, = struct.unpack('q', fin.read(8))
    # print ('bucket size:', bs)
    fs, = struct.unpack('q', fin.read(8))
    # print ('file size:', fs)

    buckets = int((fs - 1) / bs + 1)
    print('buckets:', buckets)

    StateVectorLengthInBytes = int((buckets - 1) / 8 + 1)
    sv = struct.unpack(str(StateVectorLengthInBytes) + 'B', fin.read(StateVectorLengthInBytes))  # disk written state vector
    # print ('disk written state vector:\n ->', sv, '<-')

    inCache = 0
    for i in sv:
        inCache += countSetBits(i)
    print('blocks cached:', inCache)

    chksum, = struct.unpack('16s', fin.read(16))
    # print ('chksum:', chksum)

    time_of_creation, = struct.unpack('Q', fin.read(8))
    # print ('time of creation:', datetime.fromtimestamp(time_of_creation))

    accesses, = struct.unpack('Q', fin.read(8))
    print('accesses:', accesses)

    path = filename
    if os.path.islink(filename):
        path = os.path.realpath(filename)

    return


FILES = {}  # key is last access time, value is path


def collect_meta():
    # Get a list of cinfo files
    files = [y for x in os.walk(BASE_DIR) for y in glob(os.path.join(x[0], '*.cinfo'))]
    for filename in files:
        last_modification_time = os.stat(filename).st_mtime
        FILES[last_modification_time] = filename
        print(filename, last_modification_time)
    print('files present:', len(FILES))


def CleanUpDarkData():
    # loops over files in BASE_DIR and deletes all files that have no corresponding .cinfo file

    # returns a list of tuples ('current directory',[directories],[files])
    ntp = [x for x in os.walk(BASE_DIR)]
    dark_files_removed = 0
    empty_dirs_removed = 0
    for (cwd, dirs, files) in ntp:

        for f in files:
            keep = True
            if f.endswith('.cinfo'):
                keep = f[:-6] in files
            else:
                keep = f + '.cinfo' in files
            if not keep:
                dark_files_removed += 1
                print('deleting file:', os.path.join(cwd, f))
                os.remove(os.path.join(cwd, f))

        if not dirs and not files:
            print('deleting empty dir', cwd)
            os.rmdir(cwd)
            empty_dirs_removed += 1
            continue

    print('dark files removed:', dark_files_removed)
    print('empty directories removed:', empty_dirs_removed)


def ShuffleAway(disk):
    if not FILES:
        collect_meta()
    for ts in sorted(FILES):
        get_file_info(FILES[ts])
        break


while True:
    print('is some disk above the limit? ', datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    # first check utilization of all the disks and fix them if needed.
    for DISK in HOTS + COLDS:
        print(DISK)
        cdu = DISK.get_utilization()
        if cdu > 98:
            ShuffleAway(DISK)

    # check hot disk utilization if less than HWM sleep 10 seconds then continue
    print('is hot disk above HWM? ', datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    for DISK in HOTS:
        print(DISK)
        cdu = DISK.get_utilization()
        if cdu > DISK.hwm:
            ShuffleAway(DISK)
    time.sleep(120)

    # move files in a round robin way among cold disks untill under LWM
