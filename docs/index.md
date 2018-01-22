# XCache

## What is it? 

    XCache is a service that provides caching of data accessed using [xrootd protocol](here link).
    It sits in between client and an upstream xrootd servers and can cache/prefetch full files or only blocks already requested.
    To use it to cache file that is at 
    ```root://origin.org:1094/my_file.txt``` simply prepend name of the caching server:
    ```root://caching_server.org:1094//root://origin.org:1094/my_file.txt```
    When deployed using kubernetes all relevant parameters are configured throught the container environment variables.

## Links
*   [Docker](https://hub.docker.com/r/slateci/xcache/)
*   [GitHub](https://github.com/slateci/XCache)
*   [Documentation](http://slateci.io/XCache/)
*   [Monitoring](http://atlas-kibana.mwt2.org)

## Configuration

### Mandatory variables
*   Sitename
*   Certificate 

### Optional variables
Option | Default | Meaning
----------------------
Rucio N2N | True | This is ATLAS specific thing. To avoid multiple cache copies of the same file (obtained from different sources) it will strip source specific part of the path.
Monitoring | True | This is xrootd internal monitoring info. Actual service status is monitored through the kubernetes infrastructure.
Port | 1094 |
Subfile caching | True |
Prefetching | False |
Block size | 1M | 
Disk usage high watermark | 95% | 
Disk usage low watermark | 80% |

#### To Do

*   Ilija - create a pod deployment
*   Create config file generator
*   Test


