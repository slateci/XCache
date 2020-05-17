#!/usr/bin/env python3.6

# SHOULD NOT BE USED!
# COPY OF SPARSE FILES CREATES FILES SIGNIFICANTLY BIGGER

import os
# import sys
from glob import glob
import struct
import time
from datetime import datetime
from shutil import copy2
import stats

BASE_DIR = '/xcache-meta/namespace'


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


def collect_meta():
    # Get a list of cinfo files
    files = [y for x in os.walk(BASE_DIR) for y in glob(os.path.join(x[0], '*.cinfo'))]
    FILES = {}
    for filename in files:
        last_modification_time = os.stat(filename).st_mtime
        FILES[last_modification_time] = filename
        # print(filename, last_modification_time)
    print('files present:', len(FILES))
    return FILES


def clean_dark_data():
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
                try:
                    ffn = os.path.join(cwd, f)
                    print('deleting file:', ffn)
                    os.remove(os.path.realpath(ffn))  # actual file
                    os.remove(ffn)  # link
                    dark_files_removed += 1
                except OSError as oerr:
                    print('file dissapeared?', oerr)
        if not dirs and not files:
            if cwd == BASE_DIR:
                continue
            print('deleting empty dir', cwd)
            try:
                os.rmdir(cwd)
                empty_dirs_removed += 1
            except OSError as oerr:
                print('directory got filled in meanwhile?', oerr)
            continue
    print('dark files removed:', dark_files_removed)
    print('empty directories removed:', empty_dirs_removed)


def ShuffleAway(disk):

    (total, used, _free) = disk.get_space()
    bytes_to_free = used - total * disk.lwm

    FILES = collect_meta()
    max_move = 100
    moved = 0
    for ts in sorted(FILES):

        round_robin_disk_index = moved % len(xd.COLDS)
        data_link_fn = FILES[ts][:-6]

        # check if there is a data file link and is not broken
        try:
            fs = os.stat(data_link_fn).st_blocks * 512
        except OSError as ose:
            print('data file link dissappeared or link broken', ose)
            continue

        # get actual data file path
        data_fn = os.path.realpath(data_link_fn)
        # determine what disk is it on. If not on "disk" continue
        if not data_fn.startswith(disk.path):
            continue

        # # check cinfo file is there and link is not broken
        # cinfo_link = FILES[ts]
        # try:
        #     os.stat(cinfo_link)
        # except OSError as ose:
        #     print('cinfo file dissappeared or link broken', ose)
        #     continue
        # # get actual cinfo file path
        # cinfo_fn = os.path.realpath(cinfo_link)
        # print('cinfo_link', cinfo_link)
        # print('cinfo_fn', cinfo_fn)

        print('age:', time.time() - ts)
        print('data_link_fn', data_link_fn)
        print('data_fn', data_fn)
        print('roundr:', round_robin_disk_index)

        data_new_fn = data_fn.replace(disk.path, xd.COLDS[round_robin_disk_index].path)
        print('data_new_fn', data_new_fn)
        new_path = data_new_fn[:data_new_fn.rindex('/')]
        print('new path', new_path)

        # make a copy of the actual file
        os.makedirs(new_path, exist_ok=True)
        copy2(data_fn, data_new_fn, follow_symlinks=False)
        # delete old link
        os.unlink(data_link_fn)
        # create new link
        os.symlink(data_new_fn, data_link_fn)
        # delete old data
        os.remove(data_fn)
        # check how much data was moved
        get_file_info(FILES[ts])
        print('stat file size:', fs.st_size)
        bytes_to_free -= fs.st_size
        moved += 1
        if bytes_to_free < 0 or moved > max_move:
            break
    print('bytes_to_free:', bytes_to_free)


# print('cleanup dark data')
# clean_dark_data()

if __name__ == "__main__":
    xd = stats.Xdisks()
    while True:
        xd.update()
        xd.report()

        print('is some disk above the limit? ', datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        # first check utilization of all the disks and fix them if needed.
        for DISK in xd.HOTS + xd.COLDS:
            cdu = DISK.get_utilization()
            if cdu > 98:
                print('DISK went highwire!', DISK)
                ShuffleAway(DISK)

        # check hot disk utilization if less than HWM sleep 10 seconds then continue
        if stats.get_load()[0] > 20:
            print('load too high', stats.get_load())
        else:
            print('is hot disk above HWM? ', datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            for DISK in xd.HOTS:
                cdu = DISK.get_utilization()
                if cdu > DISK.hwm:
                    print('HOT disk over the HWM:', DISK)
                    ShuffleAway(DISK)

        time.sleep(120)
