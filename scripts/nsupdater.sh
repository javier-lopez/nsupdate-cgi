#!/bin/bash

#usage: ./nsupdater.sh Key.private

ECHO=`which echo`
CLEAR=`which clear`
SED=`which sed`
HOST=`which host`
NSUPDATE=`which nsupdate`

KEY="${1}"

function welcomeMsg {
	$ECHO 'Welcome to nsupdater.sh 1.0'
	$ECHO '---------------------------'
	$ECHO
	$ECHO 'From this interface, you can add/remove or update your dns entries.'
	$ECHO
}

function quitMsg {
	$ECHO 'Thank you for using nsupdater, exiting ...'
	exit
}

function optionsMsg {
	$ECHO 'Please chooice one of the following options to get started:'
	$ECHO
	$ECHO '[1] Add'
	$ECHO '[2] Remove'
	$ECHO '[3] Update'
	$ECHO '[4] List Zones'
	$ECHO
	$ECHO '[5] Quit'
	$ECHO
	$ECHO -n '> '
}

function nameMsg {
	$ECHO 'Please insert the Name of your entry, example: new.unix.com: '
	$ECHO
	$ECHO -n '> '
}

function typeMsg {
	$ECHO
	$ECHO 'Please select your entry type: '
	$ECHO
	$ECHO '[1] A'
	$ECHO '[2] CNAME'
	$ECHO '[3] MX'
	$ECHO
	$ECHO -n '> '
}

function ipMsg {
	$ECHO
	$ECHO 'Please insert the IP of your entry, example: 8.8.8.8:'
	$ECHO
	$ECHO -n '> '
}

function timeMsg {
	$ECHO
	$ECHO 'Please insert the time of life for your entry, example: 86400'
	$ECHO
	$ECHO -n '> '
}

function welcomeScreen {
	$CLEAR
	welcomeMsg
	optionsMsg
	read option
}

function getDataScreen {
	$CLEAR
	nameMsg
	read name
	timeMsg
	read time
	typeMsg
	read type
	if [[ $type == "1" ]]; then
		type="A"
	elif [[ $type == "2" ]]; then
		type="CNAME"
	elif [[ $type == "3" ]]; then
		type="MX"
	else
		quitMsg
	fi
	ipMsg
	read ip
}

function zonesScreen {
	$CLEAR
	$ECHO 'There exists the following zones on your account:'
	$ECHO
        grep "^zone" /etc/bind/named.conf.local | cut -d\" -f2
	$ECHO
	$ECHO 'Please insert an specific zone to get more information or write "q" to quit'
	$ECHO
	$ECHO -n '> '
	read zone
	if [[ $zone == "q" ]]; then
		quitMsg
	else
		$ECHO
                $HOST -t a -l $zone
	fi
}

function ipInRange {
	ip_regex='\([0-9]\+\)\.\([0-9]\+\)\.\([0-9]\+\)\.\([0-9]\+\)'
	ip=(`$ECHO $1 | $SED -ne 's:^'"$ip_regex"'$:\1 \2 \3 \4:p'`)

	cidr_ip=(`$ECHO $2 | $SED -ne 's:^'"$ip_regex"'/.*$:\1 \2 \3 \4:p'`)
	cidr_netmask=(`$ECHO $2 | $SED -ne 's:^[^/]*/'"$ip_regex"'$:\1 \2 \3 \4:p'`)

	if [[ ${#cidr_netmask[@]} -ne 4 ]]; then
	  cidr_ip_decimal=(`$ECHO $2 | $SED -ne 's:^[^/]*/\([0-9]\+\)$:\1:p'`)
	  [[ -z $cidr_ip_decimal ]] && return 1
	  cidr_ip_decimal=$(( ((2**${cidr_ip_decimal})-1) << (32-${cidr_ip_decimal}) ))
	  for (( i=0; i<4; i++ )); do
	    cidr_netmask[$i]=$(( ($cidr_ip_decimal >> (8 * (3 - $i))) & 255 ))
	  done
	fi

	cidr_network=()
	for (( i=0; i<4; i++ )); do
	  cidr_network[$i]=$(( ${cidr_ip[$i]} & ${cidr_netmask[$i]} ))
	done

	for (( i=0; i<4; i++ )); do
	  [[ $(( ${ip[$i]} & ${cidr_netmask[$i]} )) -ne ${cidr_network[$i]} ]] && return 1
	done

	return 0
}

welcomeScreen

if [[ $option == "1" ]]; then
	getDataScreen
	$ECHO "update add $name $time $type $ip" > /usr/local/etc/namedb/working/temp
	$ECHO "send" >> /usr/local/etc/namedb/working/temp
	$NSUPDATE -k $KEY -v /usr/local/etc/namedb/working/temp 2>&1
	$ECHO
	$ECHO "adding $name $time $type $ip ..."

	if ipInRange $ip 136.186.230.0/24; then
		$ECHO "update add ${ip}.in-addr.arpa. $time PTR $name" > /usr/local/etc/namedb/working/temp
		$ECHO "send" >> /usr/local/etc/namedb/working/temp
		$NSUPDATE -k $KEY -v /usr/local/etc/namedb/working/temp 2>&1
		$ECHO
		$ECHO "adding ${ip}.in-addr.arpa. $time PTR $name ..."
	fi
elif [[ $option == "2" ]]; then
	getDataScreen
	$ECHO "update delete $name $type" > /usr/local/etc/namedb/working/temp
	$ECHO "send" >> /usr/local/etc/namedb/working/temp
	$NSUPDATE -k $KEY -v /usr/local/etc/namedb/working/temp 2>&1
	$ECHO
	$ECHO "deleting $name $time $type $ip ..."
elif [[ $option == "3" ]]; then
	getDataScreen
	$ECHO "update delete $name $type" > /usr/local/etc/namedb/working/temp
	$ECHO "send" >> /usr/local/etc/namedb/working/temp
	$NSUPDATE -k $KEY -v /usr/local/etc/namedb/working/temp 2>&1

	$ECHO "update add $name $time $type $ip" > /usr/local/etc/namedb/working/temp
	$ECHO "send" >> /usr/local/etc/namedb/working/temp
	$NSUPDATE -k $KEY -v /usr/local/etc/namedb/working/temp 2>&1
	$ECHO
	$ECHO "updating $name $time $type $ip ..."
	:
elif [[ $option == "4" ]]; then
	zonesScreen
	:
elif [[ $option == "5" ]]; then
	quitMsg
fi
