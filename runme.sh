#!/bin/sh

# find all cache mounts
# export them as variables understandable by xcache config
# make sure their ownership is right
COUNTER=0
for dir in /xcache-data_*
do
    echo "Found ${dir}."
    let COUNTER=COUNTER+1
    echo "exporting it as CACHE_${COUNTER}"
    export CACHE${COUNTER}=${dir}
    echo "making it owned by xrootd if not already."
    if [ $(stat -c "%U:%G" ${dir} ) != "xrootd:xrootd" ]; then  chown -R xrootd:xrootd ${dir}; fi
done


# the same for metadata mount
echo "adding metadata directory."
export META=/xcache-meta
mkdir -p /xcache-meta/xrdcinfos
if [ $(stat -c "%U:%G" /xcache-meta ) != "xrootd:xrootd" ]; then  chown xrootd:xrootd /xcache-meta; fi
if [ $(stat -c "%U:%G" /xcache-meta/xrdcinfos ) != "xrootd:xrootd" ]; then  chown -R xrootd:xrootd /xcache-meta/xrdcinfos; fi

export X509_USER_PROXY=/etc/grid-security/x509up1

# sleep until x509 things set up.
while [ ! -f $X509_USER_PROXY ]
do
  sleep 10
  echo "waiting for x509 proxy."
done

ls $X509_USER_PROXY

# if X509_CERT_DIR is provided mount it in /etc/grid-security/certificates
[ -s /etc/grid-security/certificates ] && export X509_CERT_DIR=/etc/grid-security/certificates

## if X509_VOMS_DIR is provided mount it in /etc/grid-security/vomsdir
#unset X509_VOMS_DIR
#[ ! -d "$X509_VOMS_DIR" ] && export X509_VOMS_DIR=/etc/grid-security/vomsdir

echo "proxy file:" $X509_USER_PROXY 
echo "cert dir:" $X509_CERT_DIR 

# sets memory to be used
if [ -z "$XC_RAMSIZE" ]; then
  XC_RAMSIZE=$(free | tail -2 | head -1 | awk '{printf("%d", $NF/1024/1024/2)}')
  [ $XC_RAMSIZE -lt 1 ] && XC_RAMSIZE=1
  XC_RAMSIZE=${XC_RAMSIZE}g
  echo "will use ${XC_RAMSIZE}g for memory."
fi

[ -z "$XC_SPACE_LO_MARK" ] && XC_SPACE_LO_MARK="0.85"
[ -z "$XC_SPACE_HI_MARK" ] && XC_SPACE_HI_MARK="0.95"

export LD_PRELOAD=/usr/lib64/libtcmalloc.so
export TCMALLOC_RELEASE_RATE=10

env
echo "Starting cache ..."

su -p xrootd -c "/usr/bin/xrootd -c /etc/xrootd/xcache.cfg &"

if  [ -z "$AGIS_PROTOCOL_ID" ]; then
  echo 'not updating AGIS protocol status.'
else
  echo "making AGIS protocol ${AGIS_PROTOCOL_ID} active..."
  ./updateAGISstatus.sh ${AGIS_PROTOCOL_ID} ACTIVE
fi

sleep infinity
