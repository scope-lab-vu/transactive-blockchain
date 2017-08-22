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

### How to create a test network

# simple timestamp method
timestamp() {
  date +"%T"
}

# delete temp files beforehand.

rm -f ./static-nodes.json
rm -f ./new-miners.json
rm -f ./new-clients.json
rm -rf ./new-blockchain/
rm -f ./genesis-data.json

#create start-timestamp
timestamp

#### create bootnodes and store them as 'static-nodes.json' for each etherium client connecting to them.
# Uncomment this line if you wish to use bootnodes as Ethereum client discovery mechanism
#./network-manager.py bootnodes create --file $1 --out=./static-nodes.json

#### create each client (all 'clients' are prosumers in current version)
./network-manager.py clients create --file $1 --out=./new-clients.json

#### create each miners we have separate miners that do nothing but mine as an option, and we use it in our test network.
./network-manager.py miners create --file $1 --out=./new-miners.json

#### create a genesis blockchain configuration file with pre-loaded accounts for clients.
./network-manager.py blockchains make --file $1 --clients ./new-clients.json


#### make new blockchain from genesis-data created above, store in ./new-blockchain  directory
./network-manager.py blockchains create --file genesis-data.json --datadir ./new-blockchain/

#### distribute static-nodes.json to each prosumer and each miner client
# Uncomment these 2 lines if you wish to use bootnodes as Ethereum client discovery mechanism
#./network-manager.py clients distribute --file $1 --local ./static-nodes.json
#./network-manager.py miners distribute --file $1 --local ./static-nodes.json

#### distribute the new blockchain genesis block to each client (including miners)
./network-manager.py clients distribute --file $1 --local ./new-blockchain/

./network-manager.py miners distribute --file $1 --local ./new-blockchain/

#create end-timestamp
timestamp

#### Network is now created.
echo "New test-network is now created."
