#!/bin/bash

GETHCLIENT=localhost
PORT=10000
DIR=~/projects/transactive-blockchain/code
PROJECT=ResourcePlatform
JOBS=$DIR/$PROJECT/"jobs"
# ID=1
#
#
# tmux new -d -s Prosumer
# tmux send -t Prosumer.0 "python3 $DIR/$PROJECT/components/Carpooler.py $ID $GETHCLIENT $PORT $FILE" ENTER


i=1
#for i in $(seq 0 99);
#for i in $(seq 0 74)
if false ; then
for i in $(seq 0 0)
do
  echo "launch actor$i"
  tmux new -d -s actor$i
  tmux send -t actor$i.0 "sudo python3 $DIR/$PROJECT/components/JobCreator.py $i $GETHCLIENT $PORT 0 $JOBS" ENTER
done
fi

if true; then
  sudo python3 $DIR/$PROJECT/components/JobCreator.py 101 $GETHCLIENT $PORT $JOBS
fi
