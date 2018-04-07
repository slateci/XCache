#!/bin/sh

# Need to install this - it will create and populate directory /etc/grid-security/certificates
yum install osg-ca-certs voms-clients fetch-crl -y

chmod 400 /root/.globus/xcache-key.pem
chmod 644 /root/.globus/xcache-crt.pem

while true; do 

  # update proxy
  voms-proxy-init -key /root/.globus/xcache-key.pem -cert /root/.globus/xcache-crt.pem
  cp /tmp/x509up_u0 /etc/grid-security/x509up
  
  sleep 21600

  # update crls
  /usr/sbin/fetch-crl

done