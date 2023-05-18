#!/bin/bash

`which python3` check_dhcp.py &
sleep 5
dhclient > /dev/null
echo wait ...
sleep 15
