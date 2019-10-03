#!/bin/bash

#Setup
MINER=localhost
PORT=10000
DIR="~/projects/transactive-blockchain/code"
PROJECT="TransactivePlatform"
echo $DIR
x=(700 1300 700 1300)
y=(150 150 600 600)

# Cleanup
pkill python3
pkill geth
pkill tmux
pkill xterm
#influx -execute 'drop database EnergyMarket'
rm -rf $DIR/miner/eth

#start TMUX
i=0
xterm -geometry 93x31+${x[i]}+${y[i]} -hold -e tmux new -s miner &
i=1
xterm -geometry 93x31+${x[i]}+${y[i]} -hold -e tmux new -s Directory &
i=2
xterm -geometry 93x31+${x[i]}+${y[i]} -hold -e tmux new -s Solver &
sleep 1 #wait for tmux to start

# Start miner
tmux send -t miner.0 "cd $DIR/miner; pwd" ENTER
tmux send -t miner.0 "pwd ; geth-linux-amd64/geth --datadir eth/  init genesis-data.json" ENTER
tmux send -t miner.0 "geth-linux-amd64/geth account new --password password.txt --datadir eth/" ENTER
sleep 5 #Wait for account address
tmux send -t miner.0 "geth-linux-amd64/geth --datadir eth/ --rpc --rpcport $PORT --rpcaddr localhost --nodiscover --rpcapi "eth,web3,admin,miner,net,db" --password password.txt --unlock 0 --networkid 15 --mine | tee miner.out" ENTER

# Start market
read -p "Wait for at least 15 blocks to be mined. Then press enter to start Market"
tmux send -t Directory.0 "python3 $DIR/$PROJECT/components/Directory.py $MINER $PORT" ENTER
tmux send -t Solver.0 "python3 $DIR/$PROJECT/components/Solver.py $MINER $PORT" ENTER

# sleep 10s #Wait for Market to connect so they can get events
# # Start prosumers
# $DIR/test-10-11-withbattery/testrun_tmux.sh
#
# tmux attach -t prosumer101.0
