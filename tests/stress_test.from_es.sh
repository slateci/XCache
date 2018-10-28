#!/bin/sh

#getting paths from a service.given as a parameter 1 and transferting through xcache given as a parameter 2.

# X509_USER_PROXY, X509_CERT_DIR, X509_VOMS_DIR do not have to be defined/provided
# but then it won't really be useful

export X509_USER_PROXY=/etc/grid-security/x509up
export X509_CERT_DIR=/etc/grid-security/certificates
export X509_VOMS_DIR=/etc/grid-security/vomsdir

echo $X509_USER_PROXY $X509_CERT_DIR $X509_VOMS_DIR

export LD_PRELOAD=/usr/lib64/libtcmalloc.so
export TCMALLOC_RELEASE_RATE=10

export TIMEFORMAT='%3R'

#SERVER="http://localhost"
#SERVER="https://xcache.org"
SERVER=$1

# XCACHE_SERVER='https://fax.mwt2.org//'
XCACHE_SERVER=$2

NFILES=10

while true
do

    # get next n files in queue and save them as json file
    curl -k -X GET "$SERVER/stress_test/$NFILES" > res.json

    # parse filenames and paths
    fns=( $(jq -C -r '.[]|.filename'  res.json) )
    pths=( $(jq -C -r '.[]|.path'  res.json) )
    ids=( $(jq -C -r '.[]|._id'  res.json) )

    # loop over them    
    for ((i=0;i<${#fns[@]};++i)); do
        DA=$(date)
        printf "$DA copying %s\n" "${pths[i]}"
        export XRD_LOGFILE=${ids[i]}.LOG
        { time timeout 270 xrdcp -f -d 2 -N $XCACHE_SERVER${pths[i]} /dev/null  2>&1 ; } 2> ${ids[i]}.tim

        # check output code
        # get time from time file
        # do curl of result
        # curl -k -X GET "$SERVER/stress_result/$id/$code/$rate" > res.json
    done

done
