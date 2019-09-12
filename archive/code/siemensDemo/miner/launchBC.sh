#!/bin/bash
DIR=$(pwd)
echo $DIR
rm -rf eth
tmux new -d -s miner

$DIR/geth-linux-amd64/geth --datadir eth/  init genesis-data.json
$DIR/geth-linux-amd64/geth account new --password password.txt --datadir eth/

sleep 5
tmux send -t miner.0 "$DIR/geth-linux-amd64/geth --datadir $DIR/eth --rpc --rpcport 10000 --rpcaddr localhost --nodiscover --rpcapi "eth,web3,admin,miner,net,db" --password password.txt --unlock 0 --networkid 15 --mine | tee miner0.out" ENTER

#tmux send -t miner.0 "$DIR/geth-linux-amd64/geth --datadir $DIR/miner0 --rpc --rpcport 10000 --rpcaddr localhost --nodiscover --rpcapi "eth,web3,admin,miner,net,db" --password password.txt --unlock 0 --networkid 15 --mine | tee miner0.out" ENTER
#tmux send -t miner.1 "$DIR/geth-linux-amd64/geth --datadir $DIR/miner1 --rpc --rpcport 10005 --rpcaddr localhost --nodiscover --rpcapi "eth,web3,admin,miner,net,db" --password password.txt --unlock 0 --networkid 15 --mine | tee miner1.out" ENTER
#tmux send -t prosumers.0 "$DIR/geth-linux-amd64/geth --datadir $DIR/prosumers --rpc --rpcport 10010 --rpcaddr localhost --nodiscover --rpcapi "eth,web3,admin,net,db" --password password.txt --unlock 0 --networkid 15 | tee prosumers.out" ENTER
