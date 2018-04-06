#!/bin/sh

# This should if needed do:
yum install fetch-crl -y

while true; do 
  sleep 21600

  # update crls
  /usr/sbin/fetch-crl

  # update proxy
  # voms-proxy-init -voms atlas -pwstdin < /afs/cern.ch/user/i/ivukotic/gridlozinka.txt

done


# X509_USER_PROXY, X509_CERT_DIR, X509_VOMS_DIR do not have to be defined/provided
# but then it won't really be useful

# if x509 user proxy is provided mount it in /etc/grid-security/x509up

unset X509_USER_PROXY
[ -s /etc/grid-security/x509up ] && export X509_USER_PROXY=/etc/grid-security/x509up

# if X509_CERT_DIR is provided mount it in /etc/grid-security/certificates
unset X509_CERT_DIR
[ ! -d "$X509_CERT_DIR" ] && export X509_CERT_DIR=/etc/grid-security/certificates

# if X509_VOMS_DIR is provided mount it in /etc/grid-security/vomsdir
unset X509_VOMS_DIR
[ ! -d "$X509_VOMS_DIR" ] && export X509_VOMS_DIR=/etc/grid-security/vomsdir

echo $X509_USER_PROXY $X509_CERT_DIR $X509_VOMS_DIR


sleep infinity
