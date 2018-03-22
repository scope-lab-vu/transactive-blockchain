#./test.sh

pkill tail
pkill python3
pkill geth

influx -execute 'drop database EnergyMarket'
rm -rf ~/ethereum/*
( cd fab ; ./create.sh m1s1-network-config.json )
sleep 10s
( cd fab ; ./start.sh m1s1-network-config.json )
sleep 10s
./launch-m1s1.sh
sleep 10s
./launch-prosumers.sh
