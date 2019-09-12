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

### How to start a test network

# Start the clients (Dso(s) & Prosumer(s))
./network-manager.py clients start --file $1
./network-manager.py miners start --file $1

# Connect the network

# Gets the enode of each client, & adds each client as a peer of each miner
# This creates a star-graph from each miner to each prosumer/dso.
./network-manager.py miners connect --file $1 --verbose

## Network is now running and connected

