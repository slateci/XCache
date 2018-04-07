kubectl create secret generic xcache-cert-secret --from-file=xcache-key.pem=certificates/xcache.key.pem --from-file=xcache-crt.pem=certificates/xcache.crt.pem
