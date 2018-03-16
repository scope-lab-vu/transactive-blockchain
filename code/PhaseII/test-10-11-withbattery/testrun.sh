#nohup python3 ~/components/MatchingSolverWrapper.py 10.4.209.30 10000 > ~/test-10-11-withbattery/solver.out 2>&1 &
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT="$(dirname $DIR)"
echo DIR $DIR
echo PARENT $PARENT
#echo `ls $DIR/all_data | cut -d '_' -f2 | tr -d "*.csv"`
#echo `ls $DIR/all_data/*.csv | cut -d '_' -f2 |tr -d "*.csv"`
for i in `ls $DIR/all_data/ | cut -d '_' -f2 |tr -d "*.csv"`;
do
echo "launching prosumer $i"
nohup python3 components/SmartHomeTraderWrapper.py $i localhost 9000 > test-10-11-withbattery/prosumer$i.out 2>&1 &
done
