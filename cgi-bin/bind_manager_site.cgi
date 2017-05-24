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

$site = $FORM{site};

print "Content-type:text/html\r\n\r\n";
print '<html>';
print '<head>';
print '<title>Bind Manager 0.0.1</title>';
print '</head>';
print '<body>';
print "<h1>Administration page: $site</h1>";
print "<h2>Please select an action.</h2>";
print '<form action = "bind_manager_action.cgi" method = "POST">';
print '   <select name = "action">';
print '      <option value = "ls"     selected>ls</option>';
print '      <option value = "add"            >add</option>';
print '      <option value = "update"         >update</option>';
print '      <option value = "delete"         >delete</option>';
print '   </select>';
print "   <input type=\"hidden\" name=\"site\" value=\"$site\">";
print '   <input type = "submit" value = "Submit">';
print '</form>';
print '<a href="bind_manager.cgi">Go back</a>';
print '</body>';
print '</html>';

1;
