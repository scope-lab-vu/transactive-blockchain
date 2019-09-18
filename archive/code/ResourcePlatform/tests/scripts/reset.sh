#!/bin/bash
pkill python3
pkill geth
pkill sleep

appName=job0
sudo docker ps -a | grep $appName | awk '{print $1}' | xargs sudo docker rm
sudo docker images -a | grep $appName | awk '{print $3}' | xargs sudo docker rmi
sudo docker rm $(sudo docker ps -a -q)


#sudo docker rm $(sudo docker ps -a -q)
#docker rmi $(docker images -q)
