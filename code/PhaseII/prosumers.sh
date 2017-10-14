#!/bin/bash
for i in `ls ~/projects/transactive-blockchain/code/PhaseII/results/test-10-11-nobattery/prosumer*.out`
do 
#echo $i
python3 stats.py $i
done

