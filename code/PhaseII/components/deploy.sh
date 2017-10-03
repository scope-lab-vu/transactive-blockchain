#!/usr/bin/env bash

scp *.py blockchain:~/components/
ssh blockchain 'scp components/*.py eth1:~/components/'

