#./test.sh

#Cleanup
pkill python3
pkill geth
pkill tail
pkill tmux
pkill sleep
influx -execute 'drop database EnergyMarket'
rm -rf ~/ethereum/*
rm -rf logs/*
rm -rf prosumer-logs/*

#SETUP
( cd fab ; ./create.sh m2s2-network-config.json )
sleep 10s
( cd fab ; ./start.sh m2s2-network-config.json )
MINER=localhost
PORT=9000
SOLVER1_PORT=9001
SOLVER2_PORT=9002
DIR=$(pwd)
x=(700 1300 700 1300 100)
y=(150 150 600 600 600)

#START TMUX
i=0
xterm -geometry 93x31+${x[i]}+${y[i]} -hold -e tmux new -s Miner1 &
i=1
xterm -geometry 93x31+${x[i]}+${y[i]} -hold -e tmux new -s DSO &
i=2
xterm -geometry 93x31+${x[i]}+${y[i]} -hold -e tmux new -s Solver &
tmux new -d -s Solver2
i=3
xterm -geometry 93x31+${x[i]}+${y[i]} -hold -e tmux new -s Recorder &
sleep 5 #wait for tmux to start

# Start market
tmux send -t Miner1.0 "tail -f ~/ethereum/test_network_002_1/miners/00001/output.log" ENTER
#read -p "Wait for at least 15 blocks to be mined. Then press enter to start Market"
tmux send -t DSO.0 "python3 components/DSOWrapper.py $MINER $PORT 2>&1 | tee logs/DSO.log" ENTER
tmux send -t Solver.0 "python3 components/MatchingSolverWrapper.py $MINER $SOLVER1_PORT 2>&1 | tee logs/Solver1.log" ENTER
tmux send -t Solver2.0 "python3 components/MatchingSolverWrapper.py $MINER $SOLVER2_PORT 2>&1 | tee logs/Solver2.log" ENTER
tmux send -t Recorder.0 "python3 components/EventRecorder.py $MINER $PORT 2>&1 | tee logs/Recorder.log" ENTER

sleep 10s #Wait for Market to connect so they can get events
# Start prosumers
$DIR/test-10-11-withbattery/testrun_tmux.sh
sleep 1
i=4
xterm -geometry 93x31+${x[i]}+${y[i]} -hold -e tmux attach -t prosumer101.0 &

SolverPID="$(ps -ef | pgrep -f MatchingSolverWrapper | sed -n 1p)" # Get ip of first solver instance
start=$SECONDS
# sleep for s to s+r seconds
s=300
r=300
rand=$[ ( $RANDOM % ($r+1) ) + $s ]
echo "$SolverPID will fail in $rand seconds"
sleep $[ $rand ]s
duration=$(( SECONDS - start ))
echo "$duration seconds have passed"

# kill solver
python3 components/failure.py $SolverPID S

sleep 300s
pkill python3
pkill geth
pkill tmux
pkill xterm
