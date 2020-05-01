#!/bin/sh

# In case there is a hot disk configured
# it shuffles coldest files to cold disks.

COUNTER=0
for dir in /xcache-data_*
do
    echo "Found ${dir}."
    let COUNTER=COUNTER+1
    echo "exporting it as COLD_${COUNTER}"
    export DISKS_${COUNTER}=${dir}
done

/shuffler.py
