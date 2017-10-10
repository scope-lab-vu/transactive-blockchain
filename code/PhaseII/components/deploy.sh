#!/usr/bin/env bash

scp *.py blockchain:~/components/
ssh blockchain 'scp components/*.py eth1:~/components/'
scp ../data/withBattery/*.csv blockchain:~/data/
ssh blockchain 'scp data/*.csv eth1:~/data/'

