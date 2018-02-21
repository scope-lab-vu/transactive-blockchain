#nohup python3 ~/components/MatchingSolverWrapper.py 10.4.209.30 10000 > ~/test-10-11-withbattery/solver.out 2>&1 &
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT="$(dirname $DIR)"
echo DIR $DIR
echo $PARENT/components
for i in `ls $DIR/opal-data10x/*.csv | cut -d '_' -f2 |tr -d "*.csv"`;
do
echo "launching prosumer $i"
nohup python3 $PARENT/components/SmartHomeTraderWrapper.py $i 192.168.10.108 10000 > $PARENT/test-10-11-withbattery/prosumer$i.out 2>&1 &
done
