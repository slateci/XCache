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


mkdir -p /data/xrd/namespace /data/xrd/xrdcinfos /data/xrd/datafiles
mkdir -p /data/xrd/var/log /data/xrd/var/spool /data/xrd/var/run

# sets memory to be used
if [ -z "$RAMSIZE" ]; then
  RAMSIZE=$(free | tail -2 | head -1 | awk '{printf("%d", $NF/1024/1024/2)}')
  [ $RAMSIZE -lt 1 ] && RAMSIZE=1
  RAMSIZE=${RAMSIZE}g
fi

[ -z "$SPACE_LO_MARK" ] && SPACE_LO_MARK="0.75"
[ -z "$SPACE_HI_MARK" ] && SPACE_HI_MARK="0.85"

export LD_PRELOAD=/usr/lib64/libtcmalloc.so
export TCMALLOC_RELEASE_RATE=10

groupmod -o -g $GID xrootd
usermod -o -u $UID -g $GID -s /bin/sh xrootd
chown -R xrootd:xrootd /data/xrd/var
chown -R xrootd:xrootd /data/xrd &

/usr/bin/xrootd -c /etc/xrootd/xcache.cfg -l /data/xrd/var/log/xrootd.log -k 7

wait
