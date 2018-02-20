#!/usr/bin/env bash

ssh blockchain 'ssh eth1 killall python3'
ssh blockchain 'ssh eth1 python3 components/DSOWrapper.py 10.4.209.25 9005'

