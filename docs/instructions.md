# Creating secrets
First one needs to create k8s secret that contains robot certificate that will be used by the XCache to get the data from origin servers. 
Create directory __certificates__ in __kube__ folder. In it add files __xcache.key.pem__ and __xcache.crt.pem__.
Than execute file __xcache-secret.bat__. This is normally done only once. Upon creation, you may delete __certificates__ folder.

# Create service
This service maps xrootd port to external ports. This is normally done only once. 
From kube directory do:
```kubectl create -f xcache_service.yaml```

# Start XCache:
```kubectl create -f xcache.yaml```

# Run stress test:
```kubectl create -f xcache-stress_test.yaml```




# Docker (obsolete)

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