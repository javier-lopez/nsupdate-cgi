#!/bin/sh

BIND_ZONES_FILE="/etc/bind/named.conf.local"

HEADER_HTML='<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>NsUpdater Public</title>
    <meta name="description" content="NsUpdater Bind Manager">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/nsupdater.css" type="text/css">
  </head>'

BODY_HEADER_HTML='
  <body>
    <div class="container">
      <div class="row">
        <div class="two column" style="margin-top: 10%">
          <a href="/nsupdater.html"><h1>NsUpdater</h1></a>
          <h5>Available Zones:</h5>
        </div>
      </div>'

BODY_FOOTER_HTML='</div>
  </body>
</html>'

printf "%s\\n" 'Content-type:text/html'
printf "%s\\n"
printf "%s\\n" "${HEADER_HTML}"
printf "%s\\n" "${BODY_HEADER_HTML}"
printf "%s\\n"
printf "%s\\n" '      <div class="horizontal-center">'
printf "%s\\n" '        <form action = "nsupdater-private-domain.cgi" method = "GET">'
printf "%s\\n" '          <select name = "zone">';
for zone in $(grep "^zone" "${BIND_ZONES_FILE}" | \
              grep -v "in-addr.arpa" | cut -d\" -f2); do
  printf "%s\\n" "          <option value = \"${zone}\">${zone}</option>";
done
printf "%s\\n" '          </select>';
printf "%s\\n" '          <input type = "submit" value = "Admin">';
printf "%s\\n" '        </form>';
printf "%s\\n" '      <div id="dump_output"></div>'
printf "%s\\n" "${BODY_FOOTER_HTML}"
