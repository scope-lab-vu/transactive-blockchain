#!/bin/bash
pkill python3
pkill geth
pkill tmux
pkill xterm
pkill sleep

# appName=job0
# sudo docker ps -a | grep $appName | awk '{print $1}' | xargs sudo docker rm
# sudo docker images -a | grep $appName | awk '{print $3}' | xargs sudo docker rmi


sudo docker rm -f $(sudo docker ps -a -q)
sudo docker rmi -f $(sudo docker images -q)
