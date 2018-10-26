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


SERVER="http://localhost"
#SERVER="https://xcache.org"
NFILES=10
curl -X GET "$SERVER/stress_test/$NFILES" > res.json

fns=( $(jq  '.hits.hits[]._source.filename' res.json) )
scps=( $(jq  '.hits.hits[]._source.scope' res.json) )

for ((i=0;i<${#fns[@]};++i)); do
    printf "%s is in %s\n" "${fns[i]}" "${scps[i]}"
done

# while true
# do
# # get next n files in queue and save them as json file
#     while read fp; do
#         date
#         echo $1//$fp
#         xrdcp -f $1//$fp /dev/null
#     done </tests/$2
# done