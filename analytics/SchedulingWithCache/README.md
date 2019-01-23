# Virtual Placement of data 
## simulating caches and job scheduling

### To Do
* data extractor:
    * jobs: wall_time, inputfiletype, processingtype=managed/user, pandaid, actualcorecount
    * traces: filenames, filesize, start_time, pid
    * agis: site, cpus

Status: 
* 0 - task info only
* 2 - jobs info level
* 3 - dataset info

* -1 - task has no jobs 
* -2 - no scope
* -3 - DataIdentifierNotFound
* -4 - RucioException
* -5 - All other exceptions