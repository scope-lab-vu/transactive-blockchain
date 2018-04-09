#!/bin/bash

GETHCLIENT=localhost
PORT=10000
DIR=~/projects/transactive-blockchain/code
PROJECT=TransactivePlatform
FILE=$DIR/$PROJECT/components/data/latlng.csv
# ID=1
#
#
# tmux new -d -s Prosumer
# tmux send -t Prosumer.0 "python3 $DIR/$PROJECT/components/Carpooler.py $ID $GETHCLIENT $PORT $FILE" ENTER


i=1
for i in $(seq 0 10);
do
  tmux new -d -s carpooler$i
  tmux send -t carpooler$i.0 "python3 $DIR/$PROJECT/components/Carpooler.py $i $GETHCLIENT $PORT $FILE" ENTER
done
