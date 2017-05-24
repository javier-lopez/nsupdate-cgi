#!/bin/sh

sudo apt-get install --no-install-recommends -y apparmor-utils
sudo aa-complain /usr/sbin/named
