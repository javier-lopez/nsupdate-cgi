#!/bin/bash

#usage:   ./bind_manager.sh ACTION TYPE NAME IP
#example: ./bind_manager.sh add A somename.unix 136.186.230.100

DDNS_KEY="/tmp/nsupdate-keys/K.private"
BIND_ZONES_FILE="/etc/bind/named.conf.local"
TMP_NSUPDATE_FILE="/tmp/nsupdate_tmpfile"

ACTION="${1}"

_v4dec() {
    for i in "${@}"; do
        printf "%s\\n" "${i}" | {
            IFS=./
            read a b c d e
            [ -z "${e}" ] && e=32
            printf "%s" "$((a<<24|b<<16|c<<8|d)) $((-1<<(32-e))) "
        }
    done
}

#https://unix.stackexchange.com/a/258926
_ip_is_in_network() {
    #$1 => IP, eg; 10.9.8.7
    #$2 => NETMASK, eg: 10.9.8.0/24
    _v4dec "${1}" "${2}" | {
        read addr1 mask1 addr2 mask2
        if (( (addr1&mask2) == (addr2&mask2) && mask1 >= mask2 )); then
            return 0
            #$ECHO "$1 is in network $2"
        else
            return 1
            #$ECHO "$1 is not in network $2"
        fi
    }
}

_add() {
    _type="${1}"; _name="${2}"; _ip="${3}"

    if [ -z "${_type}" ] || [ -z "${_name}" ] || [ -z "${_ip}" ]; then
        $ECHO "Syntax error: bind_manager.sh add TYPE NAME IP" && exit 1
    fi

    printf "%s\\n" "debug yes" >> "${TMP_NSUPDATE_FILE}"
    printf "%s\\n" "update add ${_name}. 86400 ${_type} ${_ip}" >> "${TMP_NSUPDATE_FILE}"

    if _ip_is_in_network "${_ip}" 136.186.230.0/24; then
        #https://superuser.com/a/977138, bind bug
        printf "%s\\n" >> "${TMP_NSUPDATE_FILE}"
        printf "%s\\n" "update add ${_ip}.in-addr.arpa. 86400 PTR ${_name}." >> "${TMP_NSUPDATE_FILE}"
    fi

    printf "%s\\n" "show" >> "${TMP_NSUPDATE_FILE}"
    printf "%s\\n" "send" >> "${TMP_NSUPDATE_FILE}"
    nsupdate -k "${DDNS_KEY}" -v "${TMP_NSUPDATE_FILE}" 2>&1
    _status="${?}"
    rm -rf "${TMP_NSUPDATE_FILE}"
    return "${_status}"
}

_delete() {
    _type="${1}"; _name="${2}"

    if [ -z "${_type}" ] || [ -z "${_name}" ]; then
        printf "%s\\n" "Syntax error: bind_manager.sh delete TYPE NAME" && exit 1
    fi

    printf "%s\\n" "debug yes" >> "${TMP_NSUPDATE_FILE}"
    printf "%s\\n" "update delete $_name. $_type" >> "${TMP_NSUPDATE_FILE}"
    printf "%s\\n" "show" >> "${TMP_NSUPDATE_FILE}"
    printf "%s\\n" "send" >> "${TMP_NSUPDATE_FILE}"
    nsupdate -k "${DDNS_KEY}" -v "${TMP_NSUPDATE_FILE}" 2>&1
    _status="${?}"
    rm -rf "${TMP_NSUPDATE_FILE}"
    return "${_status}"
}

_update() {
    _type="${1}"; _name="${2}"; _ip="${3}"

    if [ -z "${_type}" ] || [ -z "${_name}" ]; then
        printf "%s\\n" "Syntax error: bind_manager.sh update TYPE NAME IP" && exit 1
    fi

    _delete "${_type}" "${_name}" && _add "${_type}" "${_name}" "${_ip}"
}

_ls_all_domains() {
    awk -F\" '/^zone/{print $2}' "${BIND_ZONES_FILE}"
}

_ls() {
    case "${1}" in
           '')
            for _domain in $(_ls_all_domains); do
                host -t a -l "${_domain}"
            done
            ;;
        zones) _ls_all_domains
            ;;
        *)
            _domain="${1}"
            host -t a -l "${_domain}"
            ;;
    esac

    _status="${?}"
    return "${_status}"
}

_menu() {
    printf "%s\\n" "${1}" >&2 && shift

    [ -z "${2}" ] || printf "\\n" >&2
    for option in $@; do
        printf "%s\\n" " * ${option}" >&2
    done
    printf "\\n > " >&2
    read   _reply
    printf "%s\\n" "${_reply}"
}

_go_interactive() {
    ACTION="$(_menu "Please chooice an action" "add" "update" "delete" "ls")" && clear
    case "${ACTION}" in
        add|update)
            TYPE="$(_menu "Please choice a type" "A" "CNAME" "MX")" && clear
            NAME="$(_menu "Please insert the domain")" && clear
            IP="$(_menu   "Please insert the ip")" && clear
            _"${ACTION}" "${TYPE}" "${NAME}" "${IP}"
            ;;
        delete)
            TYPE="$(_menu "Please choice a type" "A" "CNAME" "MX")" && clear
            NAME="$(_menu "Please insert the domain")" && clear
            _"${ACTION}" "${TYPE}" "${NAME}"
            ;;
        ls)
            NAME="$(_menu "Please insert the domain")" && clear
            _"${ACTION}" "${NAME}"
            ;;
    esac
}

if [ -z "${ACTION}" ]; then
    #$ECHO "Syntax error: bind_manager.sh ACTION TYPE NAME IP" && exit 1
    _go_interactive
else
    case "${ACTION}" in
        add|update|delete|ls) shift; _$ACTION $@ ;;
        *)
            printf "%s\\n" "Invalid action: bind_manager.sh ACTION PARAMS"
            printf "%s\\n" "Valid actions include: add|update|delete|ls"
            ;;
    esac
fi
