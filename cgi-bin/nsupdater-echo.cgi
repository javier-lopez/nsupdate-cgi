#!/bin/sh

printf "%s\\n"  "Status: 200 OK"
printf "%s\\n"  "Content-type:text/plain"
printf "\\n"

oldIFS="${IFS}"
IFS='=&'
set -- $QUERY_STRING
#set -- $POST_STRING
IFS="${oldIFS}"

printf "%s\\n" "<pre>"
#$ECHO "$QUERY_STRING"
#$ECHO "${parm[1]}"
for arg in "${@}"; do
    printf "%s" "${arg} "
done
printf "%s\\n" "</pre>"
