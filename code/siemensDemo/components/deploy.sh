#!/usr/bin/env bash

scp *.py blockchain:~/components/
scp ../data/*.csv blockchain:~/data/
ssh blockchain 'scp components/*.py eth1:~/components/'
ssh blockchain 'scp data/*.csv eth1:~/data/'

