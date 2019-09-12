lsof -i tcp:5570 | awk 'NR!=1 {print $2}' | xargs kill -9
lsof -i tcp:5555 | awk 'NR!=1 {print $2}' | xargs kill -9
pkill tmux 
pkill python3

