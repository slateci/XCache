#!/usr/bin/env python3.6

import os
import sys
from glob import glob
import struct
import time
from datetime import datetime

if len(sys.argv) < 1:
    print('usage: cinfo_inspector.py <filename>')
    sys.exit(0)

filename = sys.argv[1]
print('cinfo file:', filename)


def countSetBits(n):
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count


def get_info(filename):

    fin = open(filename, "rb")

    fv, = struct.unpack('i', fin.read(4))
    print("file version:", fv)
    if fv < 3:
        return
    bs, = struct.unpack('q', fin.read(8))
    print('bucket size:', bs)
    fs, = struct.unpack('q', fin.read(8))
    print('file size:', fs)

    buckets = int((fs - 1) / bs + 1)
    print('buckets:', buckets)

    StateVectorLengthInBytes = int((buckets - 1) / 8 + 1)
    sv = struct.unpack(str(StateVectorLengthInBytes) + 'B',
                       fin.read(StateVectorLengthInBytes))  # disk written state vector
    # print('disk written state vector:\n ->', sv, '<-')

    inCache = 0
    for i in sv:
        inCache += countSetBits(i)
    print('blocks cached:', inCache)

    chksum, = struct.unpack('16s', fin.read(16))
    print('chksum:', chksum)

    time_of_creation, = struct.unpack('Q', fin.read(8))
    print('time of creation:', datetime.fromtimestamp(time_of_creation))

    accesses, = struct.unpack('Q', fin.read(8))
    print('accesses:', accesses)
    print(
        '#  Attach                Detach               Dur.[s] N_ios  N_mrg      B_hit[kB]      B_miss[kB]    B_bypass[kB]  smth')
    min_access = max(0, accesses - 20)
    for a in range(min_access, accesses):
        attach_time, = struct.unpack('Q', fin.read(8))
        detach_time, = struct.unpack('Q', fin.read(8))
        ios, = struct.unpack('i', fin.read(4))
        dur, = struct.unpack('i', fin.read(4))
        nmrg, = struct.unpack('i', fin.read(4))
        smth, = struct.unpack('i', fin.read(4))
        bhit, = struct.unpack('q', fin.read(8))
        bmis, = struct.unpack('q', fin.read(8))
        bype, = struct.unpack('q', fin.read(8))
        print('{:2d} {}   {}  {:7d} {:5d} {:6d} {:12.0f} {:12.0f} {:12.0f}'.format(
            a,
            datetime.fromtimestamp(attach_time),
            datetime.fromtimestamp(detach_time),
            dur,
            ios,
            nmrg,
            bhit/1024,
            bmis/1024,
            bype/1024
        )
        )


get_info(filename)
