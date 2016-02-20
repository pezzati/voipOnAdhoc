#!/bin/bash

year=$(date +%Y)
month=$(date +%m)
day=$(date +%d)
hour=$(date +%H)
minute=$(date +%M)
second=$(date +%S)
filename=$year-$month-$day-$hour-$minute-$second
echo $filename
tcpdump -w pcaps/$filename.pcap -i wlan0 port 54545