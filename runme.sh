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

mkdir -p /data/xrd/namespace /data/xrd/xrdcinfos /data/xrd/datafiles
mkdir -p /data/xrd/var/log /data/xrd/var/spool /data/xrd/var/run


if [ -z "$XCACHE_PFCRAM" ]; then
  XCACHE_PFCRAM=$(free | tail -2 | head -1 | awk '{printf("%d", $NF/1024/1024/2)}')
  [ $XCACHE_PFCRAM -lt 1 ] && XCACHE_PFCRAM=1
  XCACHE_PFCRAM=${XCACHE_PFCRAM}g
fi

[ -z "$SPACE_LO_MARK" ] && SPACE_LO_MARK="0.75"
[ -z "$SPACE_HI_MARK" ] && SPACE_HI_MARK="0.85"

if [ -s /etc/xrootd/xcache.cfg ]; then
  xcache_cfg=/etc/xrootd/xcache.cfg
else
  xcache_cfg=/tmp/xcache.cfg
  cat > $xcache_cfg <<EOF
  
# Info about the system:
EOF

  free | sed -e 's/^/\#\ /g' >> $xcache_cfg
  echo "" >> $xcache_cfg
  df -k /data | sed -e 's/^/\#\ /g' >> $xcache_cfg
  echo "" >> $xcache_cfg
  cat /etc/xrootd/xcache.cfg.template | sed -e "s/XCACHE_RAMSIZE/$XCACHE_PFCRAM/g"  >> $xcache_cfg
fi

#echo $X509_USER_PROXY $X509_CERT_DIR $X509_VOMS_DIR

export LD_PRELOAD=/usr/lib64/libtcmalloc.so
export TCMALLOC_RELEASE_RATE=10

uidgid_help_exit() {
  echo "please use docker -e UIDGID=N:M to provide uid:gid to run xrootd/cmsd"
  echo "    N and M should be numbers and can not be 0s"
  exit 1
}

[ -n "`echo $UIDGID | tr -d \: | tr -d \[:digit:\]`" ] && uidgid_help_exit

[ -z "$UIDGID" ] && uidgid_help_exit
uid=`echo $UIDGID | awk -F: '{print $1}'`
gid=`echo $UIDGID | awk -F: '{print $2}'`
[ ! -n "$uid" -o ! -n "$gid" ] && uidgid_help_exit
[ $uid -eq 0 -o $gid -eq 0 ] && uidgid_help_exit

groupmod -o -g $gid xrootd
usermod -o -u $uid -g $gid -s /bin/sh xrootd
chown -R xrootd:xrootd /data/xrd/var
chown -R xrootd:xrootd /data/xrd &

su - xrootd -c "/usr/bin/xrootd -c $xcache_cfg -l /data/xrd/var/log/xrootd.log -k 7" 

# not needed?
su - xrootd -c "/usr/bin/cmsd -c $xcache_cfg -l /data/xrd/var/log/cmsd.log -k 7" 

wait
