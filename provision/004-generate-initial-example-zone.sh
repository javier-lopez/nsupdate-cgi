#!/bin/sh
set -xe

domain="example.com"

sudo tee "/etc/bind/named.conf.local" << E=O=F
//http://agiletesting.blogspot.mx/2012/03/dynamic-dns-updates-with-nsupdate-and.html
key "${domain}." {
  algorithm hmac-md5;
  secret "$(awk '/Key:/{print $2; exit;}' ~/K*.private)";
};

zone "${domain}" {
  type master;
  file "/var/lib/bind/${domain}.db";
  allow-update { key "${domain}."; };
};
E=O=F

sudo -u bind tee "/var/lib/bind/${domain}.db" << E=O=F
\$ORIGIN ${domain}.
\$TTL 86400  ; 1 day
@    IN SOA  ns1.${domain}. hostmaster.${domain}. (
       2009074711 ; serial
       7200       ; refresh (2 hours)
       300        ; retry (5 minutes)
       604800     ; expire (1 week)
       60         ; minimum (1 minute)
       )
   IN  NS  ns1.${domain}.
ns1    IN  A  127.0.0.1
E=O=F

sudo service bind9 restart
