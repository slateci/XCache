#!/bin/sh

# X509_USER_PROXY, X509_CERT_DIR, X509_VOMS_DIR do not have to be defined/provided
# but then it won't really be useful

# if x509 user proxy is provided mount it in /var/run/x509up

unset X509_USER_PROXY
[ -s /var/run/x509up ] && export X509_USER_PROXY=/var/run/x509up

# if X509_CERT_DIR is provided mount it in /etc/grid-security/certificates
unset X509_CERT_DIR
[ ! -d "$X509_CERT_DIR" ] && export X509_CERT_DIR=/etc/grid-security/certificates

# if X509_VOMS_DIR is provided mount it in /etc/grid-security/vomsdir
unset X509_VOMS_DIR
[ ! -d "$X509_VOMS_DIR" ] && export X509_VOMS_DIR=/etc/grid-security/vomsdir

echo $X509_USER_PROXY $X509_CERT_DIR $X509_VOMS_DIR

export LD_PRELOAD=/usr/lib64/libtcmalloc.so
export TCMALLOC_RELEASE_RATE=10


#SERVER="http://localhost"
#SERVER="https://xcache.org"
SERVER=$1

# XCACHE_SERVER='https://fax.mwt2.org'
XCACHE_SERVER=$2

NFILES=10

while true
do

    # get next n files in queue and save them as json file
    curl -k -X GET "$SERVER/stress_test/$NFILES" > res.json

    # parse filenames and paths
    fns=( $(jq -C -r '.[]|.filename'  res.json) )
    pths=( $(jq -C -r '.[]|.path'  res.json) )

    # loop over them    
    for ((i=0;i<${#fns[@]};++i)); do
        DA=$(date)
        printf "$DA copying %s\n" "${fns[i]}" "${pths[i]}"
        xrdcp -f $XCACHE_SERVER/${pths[i]} /dev/null
    done

done