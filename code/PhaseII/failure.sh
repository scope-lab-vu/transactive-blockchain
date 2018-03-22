#./test.sh

pkill python3
pkill geth
pkill tail

influx -execute 'drop database EnergyMarket'
rm -rf ~/ethereum/*
( cd fab ; ./create.sh sample-network-config.json )
sleep 10s
( cd fab ; ./start.sh sample-network-config.json )
sleep 10s
./launch-market.sh
sleep 10s
./launch-prosumers.sh

SolverPID="$(ps -ef | pgrep -f Solver | sed -n 2p)" # Get ip of second solver instance
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
#pkill tail
