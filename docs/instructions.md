# Instructions

### Kubernetes

Before starting you need to create all the necessary secrets. This can be done by executing __xcache-secret.bat__.

To start:
```kubectl create -f xcache.yaml```

To run stress test:
```kubectl create -f xcache-stress_test.yaml```

### Docker

To start:

```
docker run -d \
-e XC_SPACE_HIGH_WM='0.95' \
-e XC_SPACE_LOW_WM='0.80' \
-e XC_PORT='1094' \
-e XC_RAMSIZE='1g' \
-e XC_BLOCKSIZE='1M' \
-e XC_PREFETCH='0' \
-p 1094:1094 \
-v /root/xcache_test/vomsdir:/etc/grid-security/vomsdir/ \
-v /root/xcache_test/proxy:/etc/grid-security/ \
--name xCache slateci/xcache
```

To log into it and check logs:

```docker exec -it xCache bash
ls /data/xrd/var/log/
```
To stop it:

```docker stop xCache```
```docker rm xCache```

To update it:
```docker pull slateci/xcache```