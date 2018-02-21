#!/bin/bash
# MINER=192.168.10.109
# DIR=$(pwd)
# echo $DIR
# rm -rf $DIR/test-10-11-withbattery/prosumer*
# tmux new -d -s DSO
# tmux send -t DSO.0 "python3 components/DSOWrapper.py $MINER 10000" ENTER
# sleep 20
# tmux new -d -s Solver
# tmux send -t Solver.0 "python3 components/MatchingSolverWrapper.py $MINER 10000" ENTER
# tmux new -d -s Recorder
# tmux send -t Recorder.0 "python3 components/EventRecorder.py $MINER 10000" ENTER
#
# sleep 5
#
# #/home/ubuntu/test-10-11-withbattery/testrun_tmux.sh
# $DIR/test-10-11-withbattery/testrun.sh

MINER=192.168.10.108
DIR=$(pwd)
echo $DIR
rm -rf logs/*

nohup python3 components/DSOWrapper.py $MINER 10000 > logs/DSO.out 2>&1 &
sleep 5
nohup python3 components/MatchingSolverWrapper.py $MINER 10000 > logs/Solver.out 2>&1 &
nohup python3 components/EventRecorder.py $MINER 10000 > logs/Recorder.out 2>&1 &

#sleep 5

#rm -rf $DIR/test-10-11-withbattery/prosumer*
#$DIR/test-10-11-withbattery/testrun.sh
