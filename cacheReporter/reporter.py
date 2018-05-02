#!/usr/bin/env python2

import os
import sys
from glob import glob
import struct
import time
from datetime import datetime
import requests

base_dir = '/cache/xrdcinfos/meta'

ct = time.time()
start_time = ct - 24 * 3600
end_time = ct - 23 * 3600

if 'XC_SITE' not in os.environ:
    print "Must set $XC_SITE. Exiting."
    sys.exit(1)
if 'XC_REPORT_COLLECTOR' not in os.environ:
    print "Must set $XC_REPORT_COLLECTOR. Exiting."
    sys.exit(1)

site = os.environ['XC_SITE']
collector = os.environ['XC_REPORT_COLLECTOR']

reports = []


def get_info(filename):

    fin = open(filename, "rb")

    fv, = struct.unpack('i', fin.read(4))
    print "file version:", fv
    bs, = struct.unpack('q', fin.read(8))
    print 'bucket size:', bs
    fs, = struct.unpack('q', fin.read(8))
    print 'file size:', fs

    buckets = int((fs - 1) / bs + 1)
    print 'buckets:', buckets

    StateVectorLengthInBytes = int((buckets - 1) / 8 + 1)
    sv = struct.unpack(str(StateVectorLengthInBytes) + 'B', fin.read(StateVectorLengthInBytes))  # disk written state vector
    # print 'disk written state vector:\n ->', sv, '<-'

    chksum, = struct.unpack('16s', fin.read(16))
    print 'chksum:', chksum

    time_of_creation, = struct.unpack('Q', fin.read(8))
    print 'time of creation:', datetime.fromtimestamp(time_of_creation)

    rec = {
        'sender': 'xCache',
        'type': 'docs',
        'site': site,
        'file': filename.replace(base_dir, ''),
        'size': fs,
        'created_at': time_of_creation
    }

    accesses, = struct.unpack('Q', fin.read(8))
    print 'accesses:', accesses

    for a in range(accesses):
        attach_time, = struct.unpack('Q', fin.read(8))
        detach_time, = struct.unpack('Q', fin.read(8))
        bytes_disk, = struct.unpack('q', fin.read(8))
        bytes_ram, = struct.unpack('q', fin.read(8))
        bytes_missed, = struct.unpack('q', fin.read(8))
        print 'access:', a, 'attached at:', datetime.fromtimestamp(attach_time), 'detached at:', datetime.fromtimestamp(detach_time), 'bytes disk:', bytes_disk, 'bytes ram:', bytes_ram, 'bytes missed:', bytes_missed
        if detach_time > start_time and detach_time < end_time:
            dp = rec.copy()
            dp['attached_at'] = attach_time
            dp['detached_at'] = detach_time
            dp['bytes_disk'] = bytes_disk
            dp['bytes_ram'] = bytes_ram
            dp['bytes_missed'] = bytes_missed
            reports.append(dp)


files = [y for x in os.walk(base_dir) for y in glob(os.path.join(x[0], '*.cinfo'))]
files += [y for x in os.walk(base_dir) for y in glob(os.path.join(x[0], '*%'))]
for filename in files:
    last_modification_time = os.stat(filename).st_mtime
    print(filename, last_modification_time)
    if last_modification_time > start_time and last_modification_time < end_time:
        get_info(filename)

print(reports)
if len(reports) > 0:
    r = requests.post(collector, json=reports)
    print 'response:', r.status_code
else:
    print "Nothing to report"
