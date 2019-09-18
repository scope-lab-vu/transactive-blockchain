#!/bin/bash
SESSION=$USER

tmux -2 new-session -d -s $SESSION

# Setup a window for tailing log files
tmux new-window -t $USER:1 -n 'Logs'
tmux split-window -h
tmux select-pane -t 0
tmux send-keys "tail -f logs/gridlabd.log" C-m
tmux select-pane -t 1
tmux send-keys "tail -f logs/agent.log" C-m
tmux split-window -v
tmux send-keys "tail -f logs/player.log" C-m
tmux resize-pane -D 3330
tmux select-pane -t 0 
tmux split-window -v

# Set default window
tmux select-window -t $SESSION:1

# Attach to session
tmux -2 attach-session -t $SESSION
