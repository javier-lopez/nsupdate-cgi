#!/usr/bin/perl

local ($buffer, @pairs, $pair, $name, $value, %FORM);
# Read in text
$ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;

if ($ENV{'REQUEST_METHOD'} eq "POST") {
   read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
}else {
   $buffer = $ENV{'QUERY_STRING'};
}

# Split information into name/value pairs
@pairs = split(/&/, $buffer);

foreach $pair (@pairs) {
   ($name, $value) = split(/=/, $pair);
   $value =~ tr/+/ /;
   $value =~ s/%(..)/pack("C", hex($1))/eg;
   $FORM{$name} = $value;
}

$site   = $FORM{site};
$action = $FORM{action};

print "Content-type:text/html\r\n\r\n";
print '<html>';
print '<head>';
print '<title>Bind Manager 0.0.1</title>';
print '</head>';
print '<body>';
print "<h1>Administration page: $site</h1>";
print "<h2>Action: $action</h2>";

if (($action eq "add") or ($action eq "update")) {
    print '<form action = "bind_manager_action_detail.cgi" method = "POST">';
    print     'TYPE: ';
    print '   <select name = "type">';
    print '      <option value = "A"     selected>A</option>';
    print '      <option value = "CNAME"         >CNAME</option>';
    print '      <option value = "MX"            >MX</option>';
    print '   </select>';
    print     ' NAME: <input type="text" name="name">';
    print     ' IP:   <input type="text" name="ip">';
    print "   <input type=\"hidden\" name=\"site\"   value=\"$site\">";
    print "   <input type=\"hidden\" name=\"action\" value=\"$action\">";
    print '   <input type = "submit" value = "Submit">';
    print '</form>';
} elsif ($action eq "delete") {
    print '<form action = "bind_manager_action_detail.cgi" method = "POST">';
    print     'TYPE: ';
    print '   <select name = "type">';
    print '      <option value = "A"     selected>A</option>';
    print '      <option value = "CNAME"         >CNAME</option>';
    print '      <option value = "MX"            >MX</option>';
    print '   </select>';
    print     ' NAME: <input type="text" name="name">';
    print "   <input type=\"hidden\" name=\"site\"   value=\"$site\">";
    print "   <input type=\"hidden\" name=\"action\" value=\"$action\">";
    print '   <input type = "submit" value = "Submit">';
    print '</form>';
}

print '<pre>';
my $ls_output = `/opt/nsupdate/scripts/bind_manager.sh ls $site`;
print "$ls_output";
print '</pre>';

print '<a href="bind_manager.cgi">Go back</a>';
print '</body>';
print '</html>';

1;
