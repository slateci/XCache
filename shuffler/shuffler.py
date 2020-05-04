#!/usr/bin/env python3.6

import os
import sys
from glob import glob
import struct
import time
import shutil

BASE_DIR = '/xcache-meta/namespace'

colds = []
hots = []
# for v in os.environ:
#     if v.startswith('DISK'):
#         colds.append(os.environ(v))

# for i in len(colds):
#     if 'XC_HOT_'+str(i) in os.environ:
#         if

#  if v.startswith('XC_HOT_HWM_')
# if 'XC_HOT' not in os.environ:
#     print("xcache shuffler - Must set $XC_HOT. Exiting.")
#     sys.exit(1)
# if 'XC_HOT_HWM' not in os.environ or 'XC_HOT_LWM' not in os.environ:
#     print("xcache reporter - Must set $XC_HOT_HWM and $XC_HOT_LWM Exiting.")
#     sys.exit(1)

# hot_path = os.environ['XC_HOT']
# hot_hwm = os.environ['XC_HOT_HWM']
# hot_lwm = os.environ['XC_HOT_LWM']
colds = []

time.sleep(9999999)
# collect paths of all cold disks. TODO


def countSetBits(n):
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count


def get_info(filename):

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


while True:
    # check hot disk utilization if less than HWM sleep 10 seconds then continue
    (total, used, free) = shutil.disk_usage(hot_path)
    print("usage:", int(used / total * 100))
    if int(used / total * 100) < hot_hwm:
        time.sleep(10)
        continue
    # Get a list of cinfo files
    files = [y for x in os.walk(BASE_DIR) for y in glob(os.path.join(x[0], '*.cinfo'))]
    for filename in files:
        last_modification_time = os.stat(filename).st_mtime
    # print(filename, last_modification_time)
    # sort in LRU order
    # move files in a round robin way among cold disks untill under LWM
