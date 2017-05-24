#!/bin/sh

sudo tee "/etc/resolv.conf" << E=O=F
nameserver 127.0.0.1
E=O=F
