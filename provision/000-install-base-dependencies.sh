#!/bin/sh
set -xe

_last_apt_get_update() {
    [ -z "${1}" ] && cache_seconds="3600" || cache_seconds="${1}"
    cache_file="/var/cache/apt/pkgcache.bin"
    if [ -f "${cache_file}" ]; then
        last="$(stat -c %Y "${cache_file}")"
        now="$(date +'%s')"
        diff="$(($now - $last))"
        if [ "${diff}" -lt "${cache_seconds}" ]; then
            return 1
        else
            return 0
        fi
    else
        return 0
    fi
}

if [ X"${_require_apt_get_update}" = X"1" ] || _last_apt_get_update 86400; then
    sudo apt-get update
fi

dpkg -l | grep squid-deb-proxy-client >/dev/null 2>&1 || \
    sudo apt-get install --no-install-recommends -y squid-deb-proxy-client
