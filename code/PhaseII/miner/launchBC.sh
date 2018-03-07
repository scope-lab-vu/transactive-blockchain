#!/bin/bash
DIR=$(pwd)
echo $DIR
rm -rf eth
tmux new -d -s miner
$DIR/geth-linux-amd64/geth --datadir eth/  init genesis-data.json
$DIR/geth-linux-amd64/geth account new --password password.txt --datadir eth/
sleep 5
tmux send -t miner.0 "$DIR/geth-linux-amd64/geth --datadir $DIR/eth --rpc --rpcport 10000 --rpcaddr 192.168.10.108 --nodiscover --rpcapi "eth,web3,admin,miner,net,db" --password password.txt --unlock 0 --networkid 15 --mine | tee miner.out" ENTER
