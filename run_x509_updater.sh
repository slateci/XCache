#!/bin/sh

CERTPATH=/etc/grid-certs

export X509_USER_PROXY=/etc/proxy/x509up
while true; do 
  date
  echo 'updating proxy'
  voms-proxy-init -valid 96:0 -key $CERTPATH/userkey.pem -cert $CERTPATH/usercert.pem --voms=atlas
    
  RESULT=$?
  if [ $RESULT -eq 0 ]; then
    echo "Proxy renewed."
  else
    echo "Could not renew proxy."
    sleep 5
    continue
  fi

  echo "Chowning proxy"
  chown xrootd /etc/proxy/x509up 

  RESULT=$?
  if [ $RESULT -eq 0 ]; then
    echo "Chowned proxy."
  else
    echo "Could not chown proxy."
    sleep 5
    continue
  fi

  sleep 338400‬

  echo 'Fetching crls'
  /usr/sbin/fetch-crl
  RESULT=$?
  if [ $RESULT -eq 0 ]; then
    echo "Fetched crls."
  else
    echo "Could not fetch crls."
    sleep 5
    continue
  fi

done