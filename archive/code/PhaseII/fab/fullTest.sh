#!/bin/bash

##############################################################################
#
# Simple script to create a new test network based on provided config file.
#
# To use -> ./create <network-config-file.json>
#
# @Author Michael A. Walker
# @Date   2017-08-09
#
##############################################################################

### Full integration test of network.

# simple timestamp method
timestamp() {
  date +"%T"
}

# stop old test network instance
echo "stopping previous test network instance."
timestamp
./network-manager.py network stop --file ./sample-network-config.json

# delete old test ntwork instance
echo "deleting previous test network instance."
timestamp
./network-manager.py network delete --file ./sample-network-config.json

# create test network
echo "creating new test network instance."
timestamp
./create.sh ./sample-network-config.json

# start test network
echo "starting new test network instance."
timestamp
./start.sh ./sample-network-config.json

# run tests for setting up contract and calling it
echo "running test of contract interfacing."
timestamp
./test/pycurlMethods.py 10.4.209.25 9008 True

echo "test finished executing"
timestamp
