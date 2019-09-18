#/bin/bash

cat solver.out | grep objective -A 1 | grep -v objective -B1 | grep objective | sed s/,/\ /g | sed s/\ INFO:\ //g | sed s/\\/TradeAdded\(\{\'solutionID\':\ //g | sed s/\}\).//g | sed s/\ \'objective\':\ //g | sed s/\ /,/g > objectives.csv
