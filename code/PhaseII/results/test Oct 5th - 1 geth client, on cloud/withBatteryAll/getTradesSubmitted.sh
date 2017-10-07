#/bin/bash

cat solver.out | grep -s "trades have been submitted to the contract." | sed s/,/\ /g | awk {'print $1","$2","$3","$6'} > tradesSubmitted.csv

