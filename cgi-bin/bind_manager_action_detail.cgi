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
$type   = $FORM{type};
$name   = $FORM{name};
if (($action eq "add") or ($action eq "update")) {
    $ip = $FORM{ip};
} else {
    $ip = '';
}

print "Content-type:text/html\r\n\r\n";
print '<html>';
print '<head>';
print '<title>Bind Manager 0.0.1</title>';
print '</head>';
print '<body>';
print "<h1>Administration page: $site</h1>";
print "<h2>Action: $action $type $name $ip</h2>";

print '<pre>';
#system("/opt/nsupdate/scripts/bind_manager.sh $action $type $name $ip");
system("/opt/nsupdate/scripts/bind_manager.sh $action $type $name $ip >/dev/null 2>&1");
if ($? == -1) {
    print "failed to execute: $!\n";
}
elsif ($? & 127) {
    printf "child died with signal %d, %s coredump\n",
    ($? & 127),  ($? & 128) ? 'with' : 'without';
}
else {
    $status = $? >> 8;
    if ($status == 0) {
        print "<h3>Entry '$type $name $ip' was ${action}d succesfully!</h3>";
        print '<pre>';
        my $ls_output = `/opt/nsupdate/scripts/bind_manager.sh ls $site`;
        print "$ls_output";
        print '</pre>';
    } else {
        printf "child exited with value $status\n";
    }
}
print '</pre>';

print '<a href="bind_manager.cgi">Go back</a>';
print '</body>';
print '</html>';

1;
