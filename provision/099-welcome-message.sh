#!/bin/sh

cat > ~/.welcome-msg << 'E=O=F'

# Quick start

## Files

    html         => /var/www/               http://localhost/nsupdater.html
    cgi-bin      => /usr/lib/cgi-bin/       http://localhost/cgi-bin/bind_manager.cgi
    scripts      => /opt/nsupdate/scripts/

    bind logs    => /var/log/syslog
    apache2 logs => /var/log/apache2/{access,error}.log

## Usage

    $ /opt/nsupdate/scripts/bind_manager.sh add A new-node.example.com 8.8.8.8
    $ /opt/nsupdate/scripts/bind_manager.sh ls
    $ /opt/nsupdate/scripts/nsupdater.sh

Have fun!
E=O=F

grep 'cat ~/.welcome-msg' ~/.bashrc >/dev/null 2>&1 || \
    printf "%s\\n" "cat ~/.welcome-msg" >> ~/.bashrc
