#!/bin/sh

oldIFS="${IFS}"
IFS='=&'
set -- $QUERY_STRING
IFS="${oldIFS}"

DOMAIN="${2}"
DNS_ENTRIES="$(dig -t axfr "${DOMAIN}" @localhost | grep -v "^;\|^$\|SOA\|NS")"

HEADER_HTML='<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>NsUpdater Private</title>
    <meta name="description" content="NsUpdater Bind Manager">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/nsupdater.css" type="text/css">
    <script>

    function objectToUrl(obj) {
      var url = "";

      for (i = 0; i < obj.length; i++) {
          url += (i == 0 ? "" : "&");
          url += obj[i].name + "[]=" //php way

          switch(obj[i].type) {
            case "select-one":
              url += obj[i].options[obj[i].selectedIndex].value;
              break;
            case "text":
              url += obj[i].value;
              break;
          }

          url += (i == (obj.length-1) ? "&" : "");
      }

      return url;
    }

    function ajaxNsUpdater() {
      var xhr = new XMLHttpRequest();
      var url = "/cgi-bin/nsupdater.cgi"

      var names = document.getElementsByName("name");
      var ttls  = document.getElementsByName("ttl");
      var types = document.getElementsByName("type");
      var ips   = document.getElementsByName("ip");

      url += "?"
      url += objectToUrl(names);
      url += objectToUrl(ttls);
      url += objectToUrl(types);
      url += objectToUrl(ips);
      //remove last ?
      url = url.substring(0, url.length - 1);

      xhr.open("GET", url);
      xhr.onload = function() {
          if (xhr.status === 200) {
              document.getElementById("ajax_output").innerHTML = xhr.responseText;
          }
          else {
              document.getElementById("ajax_output").innerHTML = "Returned status: " + xhr.status;
          }
      };
      xhr.send();
    }

    function addRow(tableID) {
        var table = document.getElementById(tableID);
        var rowCount = table.rows.length;
        var row = table.insertRow(rowCount);
        var colCount = table.rows[0].cells.length;

        for(var i=0; i<colCount; i++) {
            var newcell    = row.insertCell(i);

            newcell.innerHTML = table.rows[1].cells[i].innerHTML;
            //alert(newcell.childNodes);
            switch(newcell.childNodes[0].type) {
                case "text":
                    newcell.childNodes[0].value = "";
                    break;
                case "checkbox":
                    newcell.childNodes[0].checked = false;
                    break;
                case "select-one":
                    newcell.childNodes[0].selectedIndex = 0;
                    break;
            }
        }
    }

    function deleteRow(tableID) {
        try {
            var table = document.getElementById(tableID);
            var rowCount = table.rows.length;

            for(var i=0; i<rowCount; i++) {
                var row = table.rows[i];
                var chkbox = row.cells[0].childNodes[0];
                if(null != chkbox && true == chkbox.checked) {
                    if(rowCount <= 2) {
                        alert("Cannot delete all the rows.");
                        break;
                    }
                    table.deleteRow(i);
                    rowCount--;
                    i--;
                }
            }
        } catch(e) {
            alert(e);
        }
    }

    function ajaxReset() {
        document.getElementById("ajax_output").innerHTML = "<div id=\"ajax_output\"></div>";
    }
    </script>
  </head>'

BODY_HEADER_HTML="
  <body>
    <div class=\"container\">
      <div class=\"row\">
        <div class=\"two column\" style=\"margin-top: 10%\">
          <a href=\"/nsupdater.html\"><h1>NsUpdater</h1></a>
          <h5>Zone editor <b>'${DOMAIN}'</b>:</h5>
        </div>
      </div>"

BODY_FOOTER_HTML='</div>
  </body>
</html>'

printf "%s\\n" "Content-type:text/html"
printf "\\n"
printf "%s\\n" "${HEADER_HTML}"
printf "%s\\n" "${BODY_HEADER_HTML}"

printf "\\n"
printf "%s\\n" '      <div id="ajax_output"></div>'
printf "\\n"

printf "%s\\n" '      <div class="horizontal-center">'
printf "%s"    '     <input type="button" value="Add Entry" onclick="addRow('
printf "%s"    "'dataTable'"
printf "%s\\n" ')" />'
printf "%s"    '       <input type="button" value="Delete Entry" onclick="deleteRow('
printf "%s"    "'dataTable'"
printf "%s\\n" ')" />'
printf "%s\\n" '          <button type="button" onclick=ajaxNsUpdater()>Save</button>'

printf "%s\\n" '        <table id="dataTable">'
printf "%s\\n" '          <tr>'
printf "%s\\n" '            <th class="horizontal-center">ENTRY</th>'
printf "%s\\n" '            <th class="horizontal-center">NAME</th>'
printf "%s\\n" '            <th class="horizontal-center">TTL</th>'
printf "%s\\n" '            <th class="horizontal-center">TYPE</th>'
printf "%s\\n" '            <th class="horizontal-center">IP</th>'
printf "%s\\n" '          </tr>'

i="0";oldIFS="${IFS}"; IFS='
'
for ENTRY in ${DNS_ENTRIES}; do
    NAME="$(printf "%s\\n" "${ENTRY}" | awk '{print $1}' | sed 's:\.$::g')"
    TTL="$(printf  "%s\\n" "${ENTRY}" | awk '{print $2}')"
    TYPE="$(printf "%s\\n" "${ENTRY}" | awk '{print $4}')"
    IP="$(printf   "%s\\n" "${ENTRY}" | awk '{print $5}' | sed 's:\.$::g')"
    printf "%s\\n" '      <tr>'
    printf "%s\\n" '        <td><input type="checkbox" name="chk"/></td>'
    printf "%s\\n" "        <td><input id='nameId' type='text' name='name' value='${NAME}'/></td>"
    printf "%s\\n" "        <td><input id='ttlId'  type='text' name='ttl'  value='${TTL}'/></td>"
    #printf "%s\\n" "        <td><input id='typeId' type='text' name='type'  value='$TYPE'/></td>"
    printf "%s\\n" '        <td>'
    printf "%s\\n" '          <select id="typeId" name="type">'
    for TYPE_HARDCODED in A CNAME MX; do
        if [ "${TYPE_HARDCODED}" =  "${TYPE}" ]; then
            printf "%s\\n" "    <option value='${TYPE}' selected='selected'>${TYPE}</option>"
        else
            printf "%s\\n" "    <option value='${TYPE_HARDCODED}'>${TYPE_HARDCODED}</option>"
        fi
    done
printf "%s\\n" '              </select>'
printf "%s\\n" '            </td>'
printf "%s\\n" "            <td><input id='ipId'  type='text' name='ip' value='${IP}'/></td>"
printf "%s\\n" '          </tr>'
done
IFS="${oldIFS}"

printf "%s\\n" "        </table>"
printf "%s\\n" "${BODY_FOOTER_HTML}"
