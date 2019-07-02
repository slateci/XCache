#!/bin/sh

# Need to install this - it will create and populate directory /etc/grid-security/certificates
yum install osg-ca-certs voms-clients wlcg-voms-atlas fetch-crl -y

CERTPATH=/etc/grid-certs

while true; do 

  # update proxy
  voms-proxy-init -valid 24:0 -key $CERTPATH/userkey.pem -cert $CERTPATH/usercert.pem --voms=atlas
  mv /tmp/x509up_u0 /etc/grid-security/x509up
  chown xrootd /etc/grid-security/x509up
  export X509_USER_PROXY=/etc/grid-security/x509up 

  sleep 82800

  # update crls
  /usr/sbin/fetch-crl

done