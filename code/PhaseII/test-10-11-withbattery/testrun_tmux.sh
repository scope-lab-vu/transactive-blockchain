nohup python3 ~/components/MatchingSolverWrapper.py 10.4.209.30 10000 > ~/test-10-11-withbattery/solver.out 2>&1 &

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" #Directory of this script
 
for i in `ls $DIR/data/*.csv | cut -d '_' -f2 |tr -d "*.csv"`;
do 
echo "launching prosumer $i"
tmux new -d -s prosumer$i
tmux send -t prosumer$i.0 "python3 ~/components/SmartHomeTraderWrapper.py $i 10.4.209.30 10000" ENTER

#nohup python3 ~/projects/PhaseII/components/SmartHomeTraderWrapper.py $i 10.4.209.30 10000 > ~/test-10-11-withbattery/prosumer$i.out 2>&1 &
done
 
