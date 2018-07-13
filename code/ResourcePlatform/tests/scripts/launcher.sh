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
if true ; then
for i in $(seq 0 0)
do
  echo "launch Resource Provder $i"
  tmux new -d -s rp$i
  tmux send -t rp$i.0 "sudo python3 $DIR/$PROJECT/components/ResourceProvider.py $(($i*2)) $GETHCLIENT $PORT $JOBS" ENTER
done
fi

if true ; then
for i in $(seq 0 0)
do
  echo "launch Job Creator $i"
  tmux new -d -s jc$i
  tmux send -t jc$i.0 "sudo python3 $DIR/$PROJECT/components/JobCreator.py $(($i*2+1)) $GETHCLIENT $PORT $JOBS" ENTER
done
fi

tmux attach -t rp0.0

# if true; then
#   sudo python3 $DIR/$PROJECT/components/JobCreator.py 101 $GETHCLIENT $PORT $JOBS
# fi
#
# if true; then
#   sudo python3 $DIR/$PROJECT/components/ResourceProvider.py 102 $GETHCLIENT $PORT
# fi
