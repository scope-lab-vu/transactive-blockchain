#!/usr/bin/env bash

####################################################################
# This defines how many prosumers per feeder to use.
####################################################################


F1=5 # max 9
F2=0 # max 17
F3=5 # max 5
F4=13 # max 13
F5=8 # max 8
F6=1 # max 1
F7=10 # max 10
F8=17 # max 17
F9=5 # max 5
F10=13 # max 13
F11=4 # max 4

IP=10.4.209.25
PORT=9006

MAX_F=2
rm -rf prosumers.out
#echo "F1=" $F1 "
# loop through feeders
for f in `seq 1 $MAX_F`; do
    SUF="F"
    Feed=$SUF$f
    NUM=$(echo $Feed)
    # process is here to make loop function work
    Process=$(echo $NUM)
    # loop through each prosumer in this feeder
    for i in `seq 1 "${!NUM}" `; do
        #echo $i
        #echo $f$(printf %02d $i)
        python3 SmartHomeTraderWrapper.py $f$(printf %02d $i) $IP $PORT >> prosumer.out 2>&1 &
    done
done


