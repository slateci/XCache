#!/bin/sh

# Need to install this - it will create and populate directory /etc/grid-security/certificates
yum install osg-ca-certs voms-clients wlcg-voms-atlas -y

CERTPATH=/etc/grid-certs

export X509_USER_PROXY=/etc/grid-security/x509up
while true; do 

  # update proxy
  voms-proxy-init -valid 96:0 -key $CERTPATH/userkey.pem -cert $CERTPATH/usercert.pem --voms=atlas
  chown xrootd /etc/grid-security/x509up 

  sleep 82800

  # update crls
  /usr/sbin/fetch-crl

done