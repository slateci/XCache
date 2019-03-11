# XCache

## What is it? 

XCache is a service that provides caching of data accessed using [xrootd protocol](here link). It sits in between client and an upstream xrootd servers and can cache/prefetch full files or only blocks already requested. To use it to cache file that is at 
```root://origin.org:1094/my_file.txt```
simply prepend name of the caching server:
```root://caching_server.org:1094//root://origin.org:1094/my_file.txt```    
When deployed using kubernetes all relevant parameters are configured throught the container environment variables.

## Links
*   [Docker](https://hub.docker.com/r/slateci/xcache/)
*   [GitHub](https://github.com/slateci/XCache)
*   [Documentation](http://slateci.io/XCache/)
*   [Monitoring](http://atlas-kibana-dev.mwt2.org/goto/f6bac2569c885896a607dc047b190b6d)

## Configuration

### Mandatory variables

Variable | Meaning
--- | ---
XC_SITE | ATLAS specific. Used in registering cache in AGIS and in all monitoring. Has to correspond to ATLAS sitename.

### Optional settings

Implemented | Option | Variable | Default | Meaning
--- | --- | --- | --- | ---
No | Rucio N2N | XC_RUCIO_N2N | True | This is ATLAS specific thing. To avoid multiple cache copies of the same file (obtained from different sources) it will strip source specific part of the path.
Yes | Monitoring | XC_REPORT_COLLECTOR | http://uct2-collectd.mwt2.org:8080 | This is xrootd internal monitoring info. Actual service status is monitored through the kubernetes infrastructure.
Yes | Port | XC_PORT | 1094 |
No | Subfile caching | SUBFC | True |
Yes | Prefetching | XC_PREFETCH | 0 |
Yes | Block size | XC_BLOCKSIZE | 1M | 
Yes | Disk usage high watermark | XC_SPACE_HIGH_WM | 95% | 
Yes | Disk usage low watermark | XC_SPACE_LOW_WM | 80% |
Yes | RAM size | XC_RAMSIZE | half of the free RAM | At least 1g. Units are ...  

#### To Do

*   Add subfile caching option
*   Test
*   Create core collecting pod.
*   Add summary stream monitoring


