#!/bin/sh

# X509_USER_PROXY, X509_CERT_DIR, X509_VOMS_DIR do not have to be defined/provided

# if x509 user proxy is provided in a non-standard location (/tmp/x509up_u$(id -u)),
# then the proxy should be bind mounted: -B ${X509_USER_PROXY}:/var/run/x509up

unset X509_USER_PROXY
[ -s /var/run/x509up ] && export X509_USER_PROXY=/var/run/x509up

# if X509_CERT_DIR is not defined, or is inaccessible in the container, then we use
# the default location. Same for X509_VOMS_DIR.
# One can also bind mount:
#     -B ${X509_CERT_DIR}:/etc/grid-security/certificates
#     -B ${X509_VOMS_DIR}:/etc/grid-security/vomsdir

[ ! -z "$X509_CERT_DIR" ] && [ ! -d "$X509_CERT_DIR" ] && export X509_CERT_DIR=/etc/grid-security/certificates
[ ! -z "$X509_VOMS_DIR" ] && [ ! -d "$X509_VOMS_DIR" ] && export X509_VOMS_DIR=/etc/grid-security/vomsdir

echo $X509_USER_PROXY $X509_CERT_DIR $X509_VOMS_DIR

# sets memory to be used
if [ -z "$XC_RAMSIZE" ]; then
  XC_RAMSIZE=$(free | tail -2 | head -1 | awk '{printf("%d", $NF/1024/1024/2)}')
  [ $XC_RAMSIZE -lt 1 ] && XC_RAMSIZE=1
  XC_RAMSIZE=${XC_RAMSIZE}g
fi

[ -z "$XC_SPACE_LO_MARK" ] && XC_SPACE_LO_MARK="0.75"
[ -z "$XC_SPACE_HI_MARK" ] && XC_SPACE_HI_MARK="0.85"

export LD_PRELOAD=/usr/lib64/libtcmalloc.so
export TCMALLOC_RELEASE_RATE=10

su -p xrootd -c "/usr/bin/xrootd -c /etc/xrootd/xcache.cfg -l /data/xrd/var/log/xrootd.log -k 7 & "

sleep infinity
