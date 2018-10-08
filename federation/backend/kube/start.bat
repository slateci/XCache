kubectl create secret -n xcache generic config --from-file=config=config.json
kubectl create secret -n xcache generic cert-secret --from-file=key=secrets/certificates/xcache-backend.key.pem --from-file=cert=secrets/certificates/xcache-backend.cert.cer

kubectl create -f deployment.yaml