#!/usr/bin/env python3.6

import os
from glob import glob
import struct

BASE_DIR = '/xcache-meta/namespace'


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
    # print ('buckets:', buckets)
    StateVectorLengthInBytes = int((buckets - 1) / 8 + 1)
    sv = struct.unpack(str(StateVectorLengthInBytes) + 'B', fin.read(StateVectorLengthInBytes))  # disk written state vector
    # print ('disk written state vector:\n ->', sv, '<-')
    inCache = 0
    for i in sv:
        inCache += countSetBits(i)
    # print('blocks cached:', inCache)
    return buckets, inCache


files = [y for x in os.walk(BASE_DIR) for y in glob(os.path.join(x[0], '*.cinfo'))]
# files += [y for x in os.walk(BASE_DIR) for y in glob(os.path.join(x[0], '*%'))]
print('total files:', len(files))
tb = 0
cb = 0
for filename in files:
    blocks, cached = get_info(filename)
    tb += blocks
    cb += cached
print('total blocks:', tb, '\ncached blocs:', cb, '\nsparsness:', float(cb) / tb)
