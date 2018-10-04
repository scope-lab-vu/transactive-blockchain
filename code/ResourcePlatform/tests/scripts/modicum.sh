#!/bin/sh

DIR=~/projects/transactive-blockchain/code
PROJECT=ResourcePlatform
LOGS=$DIR/$PROJECT/logs
mkdir -p $LOGS
#PARAMETERS
MINER=172.21.20.34
DIRECTORY_IP=172.21.20.34
PORT=10000
solverID=999
miner=0
dir=1
solver=2
recorder=3
main=4

tmux new-session -s modicum -d

tmux set -g pane-border-status top

tmux split-window -h

tmux split-window -h

tmux split-window -h

tmux split-window -h

tmux select-layout tiled

tmux select-pane -t $miner -T "miner"

tmux select-pane -t $solver -T "Solver"

tmux select-pane -t $dir -T "Directory"

tmux select-pane -t $recorder -T "Recorder"

tmux select-pane -t $main -T "MAIN"

tmux send-keys -t $miner "cd ~/projects/miner"  C-m #C-m is ENTER I think
tmux send-keys -t $miner "pwd ; geth-linux-amd64/geth --datadir eth/ init genesis-data.json" C-m
tmux send-keys -t $miner "geth-linux-amd64/geth account new --password password.txt --datadir eth/" C-m
sleep 1
tmux send-keys -t $miner "geth-linux-amd64/geth --datadir eth/ --rpc --rpcport $PORT --rpcaddr $MINER --nodiscover --rpcapi "eth,web3,admin,miner,net,db" --password password.txt --verbosity 3 --unlock 0 --networkid 15 --mine |& tee miner.log" C-m

sleep 5
tmux send -t $dir "python3 $DIR/$PROJECT/components/Directory.py $MINER $PORT $DIRECTORY_IP |& tee $LOGS/directory.log" C-m
tmux send -t $solver "python3.6 $DIR/$PROJECT/components/Solver.py $MINER $PORT $solverID $DIRECTORY_IP |& tee $LOGS/solver.log" C-m
tmux send -t $recorder "python3 $DIR/$PROJECT/components/EventRecorder.py $MINER $PORT $DIRECTORY_IP |& tee $LOGS/recorder.log" C-m

tmux attach -t modicum
