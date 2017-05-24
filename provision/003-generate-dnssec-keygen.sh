#!/bin/sh
set -xe

for key in K*.private; do
    [ -f "${key}" ] && key_found="1"
done

[ -z "${key_found}" ] && dnssec-keygen -r /dev/urandom -a HMAC-MD5 -b 512 -n HOST example.com
ls -lah

mkdir -p /tmp/nsupdate-keys/
cp ~/K*.key     /tmp/nsupdate-keys/K.key
cp ~/K*.private /tmp/nsupdate-keys/K.private
chmod 777       /tmp/nsupdate-keys/K*
