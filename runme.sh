#!/bin/sh

dir="/tmp/cache/"
if [ $(stat -c "%U:%G" ${dir} ) != "xrootd:xrootd" ]; then  chown -R xrootd:xrootd ${dir}; fi

export X509_USER_PROXY=/etc/proxy/x509up
export X509_USER_CERT=/etc/grid-certs/usercert.pem
export X509_USER_KEY=/etc/grid-certs/userkey.pem
export XrdSecGSIPROXYVALID="96:00"
export XrdSecGSICACHECK=0
export XrdSecGSICRLCHECK=0
# export XrdSecDEBUG=3 

# sleep until x509 things set up.
while [ ! -f $X509_USER_PROXY ]
do
  sleep 10
  echo "waiting for x509 proxy."
done

ls -lh $X509_USER_PROXY

# if X509_CERT_DIR is provided mount it in /etc/grid-security/certificates
[ -s /etc/grid-security/certificates ] && export X509_CERT_DIR=/etc/grid-security/certificates

## if X509_VOMS_DIR is provided mount it in /etc/grid-security/vomsdir
#unset X509_VOMS_DIR
#[ ! -d "$X509_VOMS_DIR" ] && export X509_VOMS_DIR=/etc/grid-security/vomsdir

export LD_PRELOAD=/usr/lib64/libtcmalloc.so
export TCMALLOC_RELEASE_RATE=10

env
echo "Starting cache ..."

su -p xrootd -c "/usr/bin/xrootd -c /etc/xrootd/xcache.cfg &"

sleep infinity
