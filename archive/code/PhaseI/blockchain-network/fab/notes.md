
### How to create a test network 

#### create bootnodes and store them as 'static-nodes.json' for each etherium client connecting to them.
./network-manager.py bootnodes create --file ./sample-network-config.json --out=static-nodes.json
#### create each client (all 'clients' are prosumers in current version)
./network-manager.py clients create --file=./sample-network-config.json --out=./new-clients.json

#### create each miners we have separate miners that do nothing but mine as an option, and we use it in our test network.
./network-manager.py miners create --file=./sample-network-config.json --out=./new-miners.json

#### create a genesis blockchain configuration file with pre-loaded accounts for clients.
./network-manager.py blockchains make --file ./sample-network-config.json --clients ./new-clients.json

#### make new blockchain from genesis-data created above, store in ./new-blockchain  directory
./network-manager.py blockchains create --file genesis-data.json --datadir ./new-blockchain

#### distribute static-nodes.json to each prosumer and each miner client 
./network-manager.py clients distribute --file ./sample-network-config.json --local ./static-nodes.json

./network-manager.py miners distribute --file ./sample-network-config.json --local ./static-nodes.json

#### distribute the new blockchain genesis block to each client (including miners)
./network-manager.py clients distribute --file ./sample-network-config.json --local ./new-blockchain/

./network-manager.py miners distribute --file ./sample-network-config.json --local ./new-blockchain/

#### Network is now created. 
