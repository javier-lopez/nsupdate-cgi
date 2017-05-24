#!/usr/bin/perl

print "Content-type:text/html\r\n\r\n";
print '<html>';
print '<head>';
print '<title>Bind Manager 0.0.1</title>';
print '</head>';
print '<body>';
print '<h1>Welcome to Bind Manager!</h1>';
print '<h2>Please select a domain to administrate:</h2>';
print '<form action = "bind_manager_site.cgi" method = "POST">';
print '   <select name = "site">';

my @domains = `/opt/nsupdate/scripts/bind_manager.sh ls zones`;
foreach $domain (@domains) {
    print "      <option value = \"$domain\" selected>$domain</option>";
}

print '   </select>';
print '   <input type = "submit" value = "Submit">';
print '</form>';
print '</body>';
print '</html>';

1;
