kubectl create secret generic xcache-proxy-secret --from-file=user-proxy-secret=x509up

kubectl create secret generic xcache-cert-secret --from-file=xcache-cert-file1=certificates/c2.txt --from-file=xcache-cert-file2=certificates/c1.txt

kubectl create secret generic xcache-vomsdir-secret --from-file=xcache-vomsdir-file1=vomsdir/v1.txt --from-file=xcache-vomsdir-file2=vomsdir/v2.txt