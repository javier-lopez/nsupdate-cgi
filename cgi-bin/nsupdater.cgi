#!/bin/bash

#change to 0 to avoid printing DEBUG_MSG messages
DEBUG="0"
NSUPDATE_TMPFILE="/tmp/nsupdate-tmpfile"
NSUPDATE_KEY="/tmp/nsupdate-keys/K.private"

DEBUG_MSG() {
    if [ "${DEBUG}" = "1" ]; then
        printf "%s\\n" "${*}"
    fi
}

printf "%s\\n" "Status: 200 OK"
printf "%s\\n" "Content-type:text/plain"
printf "\\n"

oldIFS="${IFS}"
#IFS='=&'
IFS='&'
set -- $QUERY_STRING
#set -- $POST_STRING
IFS="${oldIFS}"

NAMES=(); TTLS=(); TYPES=(); IPS=()

for arg in "${@}"; do
    case "${arg}" in
        name*)
            NAMES+=($(printf "%s\\n" "${arg}" | cut -d= -f2))
            ;;
        ttl*)
            TTLS+=($(printf "%s\\n" "${arg}"  | cut -d= -f2))
            ;;
        type*)
            TYPES+=($(printf "%s\\n" "${arg}" | cut -d= -f2))
            ;;
        ip*)
            IPS+=($(printf "%s\\n" "${arg}"   | cut -d= -f2))
            ;;
    esac
done

DOMAIN="$(printf "%s\\n" "${NAMES[0]}" | cut -d'.' -f2-)"
ORIG_DOMAIN_ENTRIES=()

oldIFS="${IFS}"; IFS='
'
for entry in $(dig -t axfr "${DOMAIN}" @localhost | grep -v "^;\|^$\|SOA\|NS"); do
    ORIG_DOMAIN_ENTRIES+=("${entry}")
done
IFS="${oldIFS}"

DEBUG_MSG "<pre>"
DEBUG_MSG '=== OLD ENTRIES ========================================'
#remove all prev entries
for ORIG_ENTRY in "${ORIG_DOMAIN_ENTRIES[@]}"; do
    orig_name="$(printf "%s\\n" "${ORIG_ENTRY}" | awk '{print $1}')"
    orig_type="$(printf "%s\\n" "${ORIG_ENTRY}" | awk '{print $4}')"

    printf "%s\\n" "${orig_name}" | grep "^ns" >/dev/null && continue

    DEBUG_MSG "entry: ${ORIG_ENTRY}"
    DEBUG_MSG "orig_name : ${orig_name} | orig_type : ${orig_type}"

    printf "%s\\n" "update delete ${orig_name} ${orig_type}" > "${NSUPDATE_TMPFILE}"
    printf "%s\\n" "send" >> "${NSUPDATE_TMPFILE}"
    if ! nsupdate -k "${NSUPDATE_KEY}" -v "${NSUPDATE_TMPFILE}" 2>&1; then
        printf "%s\\n" 'line: 69'
        printf "%s\\n" "entry: ${ORIG_ENTRY}"
    fi
done

DEBUG_MSG '=== GET INPUT PARAMS ==================================='
DEBUG_MSG "domain : $DOMAIN"
DEBUG_MSG "entries: ${ORIG_DOMAIN_ENTRIES[@]}"
DEBUG_MSG '=== NEW ENTRIES ========================================'
DEBUG_MSG "names  : ${NAMES[@]}"
DEBUG_MSG "ttls   : ${TTLS[@]}"
DEBUG_MSG "types  : ${TYPES[@]}"
DEBUG_MSG "ips    : ${IPS[@]}"
DEBUG_MSG '========================================================'
DEBUG_MSG '</pre>'

#add all specified entries
for ((i=0; i<${#NAMES[@]}; i++)); do
    printf "%s\\n" "update add ${NAMES[$i]} ${TTLS[$i]} ${TYPES[$i]} ${IPS[$i]}" > "${NSUPDATE_TMPFILE}"
    printf "%s\\n" "send" >> "${NSUPDATE_TMPFILE}"
    if ! nsupdate -k "${NSUPDATE_KEY}" -v "${NSUPDATE_TMPFILE}" 2>&1; then
        printf "%s\\n" 'line: 90'
        printf "%s\\n" "entry: ${NAMES[$i]} ${TTLS[$i]} ${TYPES[$i]} ${IPS[$i]}"
    fi
done

printf "%s\\n" '<div id="ajax_output" class="notification">
           <div>
                <span onclick="ajaxReset()" id="ajax_reset">x</span>
                <h5>Changes saved!</h5>
           </div>
       </div>'
