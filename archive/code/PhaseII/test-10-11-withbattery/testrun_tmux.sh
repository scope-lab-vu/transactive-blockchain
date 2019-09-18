DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" #Directory of this script
echo "Launching Prosumers from $DIR"
for i in `ls $DIR/all_data/ | cut -d '_' -f2 |tr -d "*.csv"`;
do
echo "launching prosumer $i"
tmux new -d -s prosumer$i
tmux send -t prosumer$i.0 "python3 components/SmartHomeTraderWrapper.py $i localhost 9000 2>&1 | tee prosumer-logs/prosumer$i.log" ENTER

done
