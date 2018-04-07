kubectl create secret generic xcache-cert-secret --from-file=userkey.pem=certificates/xcache.key.pem --from-file=usercert.pem=certificates/xcache.crt.pem
