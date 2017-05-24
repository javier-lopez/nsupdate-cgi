#!/bin/sh

oldIFS="${IFS}"
IFS='=&'
set -- $QUERY_STRING
#set -- $POST_STRING
IFS="${oldIFS}"

DOMAIN="${2}"

printf "%s\\n" "Status: 200 OK"
printf "%s\\n" "Content-type:text/plain"
printf "\\n"
printf "%s\\n" "<pre>"
dig -t axfr "${DOMAIN}" @localhost | grep -v "^;\|^$\|SOA\|NS"
printf "%s\\n" "</pre>"
