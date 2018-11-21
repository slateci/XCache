#!/bin/sh

# this script will update state of Service Protocol in AGIS
# usage: ./updateAGISstatus.sh <protocol_id> <new_status>  
# protocol_id can be seen at the end of the link normally used to edit protocol eg. http://atlas-agis.cern.ch/agis/serviceprotocol/edit/433/
# new_status can be: ACTIVE or DISABLED  

curl -k --cert /etc/grid-certs/usercert.pem --cert-type PEM --key /etc/grid-certs/userkey.pem --key-type PEM "https://atlas-agis-api.cern.ch/request/serviceprotocol/update/?json&id=$1&state=$2&state_comment=Automatic+update"

# to generate cert and key in pem format
# openssl pkcs12 -in myCertificate.p12 -out ilija.key.pem -nocerts -nodes
# openssl pkcs12 -in myCertificate.p12 -out ilija.crt.pem -clcerts -nokeys