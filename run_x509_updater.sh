#!/bin/sh

# Need to install this - it will create and populate directory /etc/grid-security/certificates
yum install osg-ca-certs voms-clients wlcg-voms-atlas fetch-crl -y

chmod 400 /root/.globus/userkey.pem
chmod 644 /root/.globus/usercert.pem

while true; do 

  # update proxy
  voms-proxy-init -key /root/.globus/userkey.pem -cert /root/.globus/usercert.pem --voms=atlas
  mv /tmp/x509up_u0 /var/spool/xrootd/x509up
  chown xrootd /var/spool/xrootd/x509up

  sleep 21600

  # update crls
  /usr/sbin/fetch-crl

done