#!/bin/bash

. ./env.sh

echo $startTime

(exec fncs_broker 3 &> logs/broker.log &)
(exec fncs_player "$hours"h step.player &> logs/player.log &)
(exec gridlabd TE_Challenge.glm &> logs/gridlabd.log &)
(export FNCS_CONFIG_FILE=TE_Challenge_agent.yaml && exec python3 Agent.py $(expr $hours \* 3600) &> logs/agent.log &)
./session.sh
