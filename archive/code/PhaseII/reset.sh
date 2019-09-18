#!/bin/bash
pkill python3
pkill geth
pkill tmux
pkill xterm

rm -rf ./miner/eth
