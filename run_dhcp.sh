#!/bin/bash

`which python3` /root/custom_checks/check_dhcp.py &
sleep 5
dhclient > /dev/null
echo wait ...
sleep 15
