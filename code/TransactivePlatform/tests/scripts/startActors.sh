#!/bin/bash

GETHCLIENT=localhost
PORT=10000
DIR="~/projects/transactive-blockchain/code"
PROJECT="TransactivePlatform"
FILE="$DIR/$PROJECT/components/data/latlng.csv"
ID=1


tmux new -d -s Prosumer #wait for tmux to start
tmux send -t Prosumer.0 "python3 $DIR/$PROJECT/components/Carpooler.py $ID $GETHCLIENT $PORT $FILE" ENTER
