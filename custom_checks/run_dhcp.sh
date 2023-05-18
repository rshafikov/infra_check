#!/bin/bash

`which python3` /root/custom_checks/check_dhcp.py &
sleep 5
dhclient > /dev/null 2>&1
echo wait ...
sleep 15
