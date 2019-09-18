#!/usr/bin/env bash

ssh blockchain 'ssh eth1 python3 components/SmartHomeTraderWrapper.py 101 10.4.209.25 9005' &
ssh blockchain 'ssh eth1 python3 components/SmartHomeTraderWrapper.py 103 10.4.209.25 9005' &
ssh blockchain 'ssh eth1 python3 components/SmartHomeTraderWrapper.py 201 10.4.209.25 9005' &
ssh blockchain 'ssh eth1 python3 components/SmartHomeTraderWrapper.py 202 10.4.209.25 9005' &

