#!/bin/sh

HEADER_HTML='<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>NsUpdater Public</title>
    <meta name="description" content="NsUpdater Bind Manager">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/nsupdater.css" type="text/css">
    <script>
    function ajaxNsupdaterDump() {
      var xhr = new XMLHttpRequest();
      var url = "nsupdater-dump.cgi"
      var key = "name";
      var value = getQueryString();

      xhr.open("GET", url + "?" + key + "=" + value);
      xhr.onload = function() {
          if (xhr.status === 200) {
              document.getElementById("dump_output").innerHTML = xhr.responseText;
          }
          else {
              document.getElementById("dump_output").innerHTML = "Returned status: " + xhr.status;
          }
      };
      xhr.send();
    }

    function getQueryString() {
        var form = document.forms["dump"];
        return escape(form.zone.value);
    }
    </script>
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

printf "%s\\n" "Content-type:text/html"
printf "%s\\n"
printf "%s\\n" "${HEADER_HTML}"
printf "%s\\n" "${BODY_HEADER_HTML}"
printf "%s\\n"
printf "%s\\n" "      <div class=\"horizontal-center\">"
printf "%s\\n" "        <form name=\"dump\">"
printf "%s\\n" "          <select name = \"zone\">"
for zone in $(grep "^zone" /etc/bind/named.conf.local |
              grep -v "in-addr.arpa" | cut -d\" -f2); do
  printf "%s\\n" "          <option value = \"${zone}\">${zone}</option>";
done
printf "%s\\n" "          </select>"
printf "%s\\n" "          <button type=\"button\" onclick=ajaxNsupdaterDump()>Dump List</button>"
printf "%s\\n" "        </form>"
printf "%s\\n" "      <div id=\"dump_output\"></div>"
printf "%s\\n" "${BODY_FOOTER_HTML}"
