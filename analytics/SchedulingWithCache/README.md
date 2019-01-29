# Virtual Placement of data 
## simulating caches and job scheduling

* data extractor:
    * tasks: creationdate, endtime, processingtype, tasktype, site
    * jobs: njobs, sum(wall_time), sum(actualcorecount), sum(ninputdatafiles), proddblock (aka: input dataset)
    * rucio: ds_size, ds_files, ds_type
    * agis: site, cpus

Status: 
* 0 - task info only
* 2 - jobs info level
* 3 - full dataset info

* -1 - task has no jobs 
* -2 - no scope
* -3 - DataIdentifierNotFound
* -4 - RucioException
* -5 - No input dataset. All other exceptions

### To Do
* different sizes of cloud caches.
* track cacheability of different data types.
