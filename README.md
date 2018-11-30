# XCache
This repository contains all XCache resources ( docker container, docs, k8s deployment).

## What is it? 

XCache is a service that provides caching of data accessed using [xrootd protocol](http://xrootd.org/). It sits in between client and an upstream xrootd servers and can cache/prefetch full files or only blocks already requested. To use it to cache file that is at ```root://origin.org:1094/my_file.txt``` simply prepend name of the caching server:  ```root://caching_server.org:1094//root://origin.org:1094/my_file.txt``` When deployed using kubernetes all relevant parameters are configured throught the container environment variables.

## Links
*   [Docker](https://hub.docker.com/r/slateci/xcache/)
*   [GitHub](https://github.com/slateci/XCache)
*   [Documentation](http://slateci.io/XCache/)
*   [Monitoring](http://atlas-kibana-dev.mwt2.org/goto/f6bac2569c885896a607dc047b190b6d)

## Analytics / Simulation

### To do
* Job submission with XCache in mind at US scale simulation.
* DISABLING endpoint in AGIS when service is out. Reenabling liveness probe.
* Test separate disk mounting. metadata on separate disk.
* Make a central registration service for multi-server caches. Rucio will periodically ask it for active servers at site.
   * endpoints to enable/disable XCache server
   * endpoint to deliver active servers to RUCIO

## Federation

To make a tree of caching servers, we make all deployed servers report their metadata and status to a central Elasticsearch instance through a REST API of the federation server. The federation server serves filepaths based on the client location and file origin.
