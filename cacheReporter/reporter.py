#!/usr/bin/env python3.6

import os
import sys
from glob import glob
import struct
import time
import requests
# from datetime import datetime

BASE_DIR = '/xcache-meta/namespace'

ct = time.time()
start_time = ct - 3600
end_time = ct

if 'XC_SITE' not in os.environ:
    print("xcache reporter - Must set $XC_SITE. Exiting.")
    sys.exit(1)
if 'XC_REPORT_COLLECTOR' not in os.environ:
    print("xcache reporter - Must set $XC_REPORT_COLLECTOR. Exiting.")
    sys.exit(1)

site = os.environ['XC_SITE']
collector = os.environ['XC_REPORT_COLLECTOR']

reports = []


def countSetBits(n):
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count


def get_info(filename):

    fin = open(filename, "rb")

    fv, = struct.unpack('i', fin.read(4))
    # print ("file version:", fv)
    if fv<3:
        return
    bs, = struct.unpack('q', fin.read(8))
    # print ('bucket size:', bs)
    fs, = struct.unpack('q', fin.read(8))
    # print ('file size:', fs)

    buckets = int((fs - 1) / bs + 1)
    # print ('buckets:', buckets)

    StateVectorLengthInBytes = int((buckets - 1) / 8 + 1)
    sv = struct.unpack(str(StateVectorLengthInBytes) + 'B', fin.read(StateVectorLengthInBytes))  # disk written state vector
    # print ('disk written state vector:\n ->', sv, '<-')

    inCache = 0
    for i in sv:
        inCache += countSetBits(i)
    # print('blocks cached:', inCache)

    chksum, = struct.unpack('16s', fin.read(16))
    # print ('chksum:', chksum)

    time_of_creation, = struct.unpack('Q', fin.read(8))
    # print ('time of creation:', datetime.fromtimestamp(time_of_creation))

    rec = {
        'sender': 'xCache',
        'type': 'docs',
        'site': site,
        'file': filename.replace(BASE_DIR, '').replace('/atlas/rucio/', '').replace('.cinfo', ''),
        'size': fs,
        'created_at': time_of_creation * 1000,
        'blocks': buckets,
        'blocks_cached': inCache
    }

    accesses, = struct.unpack('Q', fin.read(8))
    # print ('accesses:', accesses)

    min_access = max(0, accesses - 20)
    for a in range(min_access, accesses):
        attach_time, = struct.unpack('Q', fin.read(8))
        detach_time, = struct.unpack('Q', fin.read(8))
        ios, = struct.unpack('i', fin.read(4))
        dur, = struct.unpack('i', fin.read(4))
        bype, = struct.unpack('q', fin.read(8))
        bhit, = struct.unpack('q', fin.read(8))
        bmis, = struct.unpack('q', fin.read(8))
        bwri, = struct.unpack('q', fin.read(8))
        # print (
        #     'access:', a, 
        #     'attached at:', datetime.fromtimestamp(attach_time), 
        #     'detached at:', datetime.fromtimestamp(detach_time), 
        #     'ios', ios,
        #     'duration', dur,
        #     'bytes hit:', bhit, 
        #     'bytes miss:', bmis, 
        #     'bytes bypassed:', bype, 
        #     'bytes written:', bwri
        # )
        if detach_time > start_time and detach_time < end_time:
            dp = rec.copy()
            dp['access'] = a
            dp['attached_at'] = attach_time * 1000
            dp['detached_at'] = detach_time * 1000
            dp['ios']=ios
            dp['duration']=dur
            dp['bytes_hit'] = bhit
            dp['bytes_miss'] = bmis
            dp['bytes_bypassed'] = bype
            dp['bytes_written'] = bwri
            reports.append(dp)


files = [y for x in os.walk(BASE_DIR) for y in glob(os.path.join(x[0], '*.cinfo'))]
# files += [y for x in os.walk(BASE_DIR) for y in glob(os.path.join(x[0], '*%'))]
for filename in files:
    try:
        last_modification_time = os.stat(filename).st_mtime
        # print(filename, last_modification_time)
        if last_modification_time > start_time and last_modification_time < end_time:
            get_info(filename)
    except OSError as oerr:
        print('file dissapeared?', oerr)


print("xcache reporter - files touched:", len(reports))
if len(reports) > 0:
    r = requests.post(collector, json=reports)
    print('xcache reporter - indexing response:', r.status_code)
else:
    print("xcache reporter - Nothing to report")
