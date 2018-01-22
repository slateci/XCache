# XCache
This repository contains all all XCache resources ( docker container, docs, k8s deployment).
*   [Documentation](http://slateci.io/XCache/)
*   [DockerHub auto-build](https://hub.docker.com/r/slateci/xcache/)

## To Do

*   Ilija - create simple k8s pod for testing
*   Ilija - deploy at UC and CERN


## Instructions
### How to build

```
git clone https://github.com/slateci/XCache.git
cd Xcache
docker build --tag xcache:latest .
```

### How to run

```docker run -dt -v /tmp/data:/data -v /tmp/x509up_u`id -u`:/var/run/x509up \
  -v /cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/etc/grid-security-emi/certificates:/etc/grid-security/certificates \
  --rm --net=host -e "UIDGID=`id -u`:`id -g`" xcache ```

Note:
1. UIDGID (in the form of uid:gid) is needed and will be used to run the xrootd process.
2. A the disk space for cache is bind mounted to /data. It should be owned by "uid".
3. To access ATLAS data sources, bind mount to /etc/grid-secrity/certificates is needed. Also
   needed is a x509 proxy bind mounted to /var/run/x509up. It should be owned by "uid", have 
   ATLAS voms attributes and should be continously updated.

# To stop

```pkill xrootd```
