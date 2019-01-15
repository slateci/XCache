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
MB=1048576

#SERVER="http://localhost"
#SERVER="https:/atlas.xcache.org"
SERVER=$1

# XCACHE_SERVER='https://fax.mwt2.org//'
XCACHE_SERVER=$2

# waiting for the security stuff to be done
sleep 120

while true
do

    # get next n files in queue and save them as json file
    curl -s -k -X GET "$SERVER/stress_test/" > res.json

    # parse filenames and paths
    fn=$(jq -r '.filename'  res.json)
    fs=$(jq -r '.filesize'  res.json) 
    pth=$(jq -r '.path'  res.json)
    id=$(jq -r '._id'  res.json)

    # timeout is calculated for 10 MB/s + 5s. 
    tout=$(( fs/MB/10 + 5)) 

    echo "$(date) copying ${fn}"
    echo "from $XCACHE_SERVER${pth}"
    echo "size ${fs} with timeout at ${tout} seconds."
    export XRD_LOGFILE=${id}.LOG
    { time timeout ${tout} xrdcp -f -d 2 -N $XCACHE_SERVER${pth} /dev/null  2>&1 ; } 2> timing.txt

    code=$?
    if [ "$code" = "0" ]; then
        result="Done"
    elif [ "$code" = "124" ]; then
        result="Timeout"
    elif [ "$code" = "52" ]; then 
        result="Authorization issue"
    elif [ "$code" = "53" ]; then 
        result="Redirection limit"
    elif [ "$code" = "54" ]; then 
        result="Permission denied"
    else
        result=${code}
    fi

    rate=`cat timing.txt`
    rm timing.txt
    rrate=$((fs/rate)) 
    echo "ret code: $result  duration: $rate  rate: ${rrate} MB/s"

    curl -s -k -X GET "$SERVER/stress_result/$id/$result/$rate"

done
