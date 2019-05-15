#!/bin/sh

# This one has the data volume mounted and periodically collect information from
# .cinfo files, aggregate it and report to ES.

while true; do 
  date
  /reporter.py
  sleep 3600

done