#!/bin/sh

CERTPATH=/etc/grid-certs

export X509_USER_PROXY=/etc/proxy/x509up
while true; do 

  # update proxy
  voms-proxy-init -valid 96:0 -key $CERTPATH/userkey.pem -cert $CERTPATH/usercert.pem --voms=atlas
  chown xrootd /etc/proxy/x509up 

  sleep 338400‬

  # update crls
  /usr/sbin/fetch-crl

done