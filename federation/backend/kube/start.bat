kubectl create secret -n ml-usatlas-org generic mg-config --from-file=mgconf=secrets/mg-config.json
kubectl create secret -n ml-usatlas-org generic cert-secret --from-file=key=secrets/certificates/ml-front.key.pem --from-file=cert=secrets/certificates/ml-front.cert.cer

kubectl create -f deployment.yaml