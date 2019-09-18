#!/bin/bash

cat solver.out | grep -iE 'Solving\.\.\.|Solving linear' | awk {'print $2'} | sed s/,/./g | awk 'ORS=NR%2?",":"\n"' > solvingTimes.csv
#cat solvingTimes.csv  ... | paste - - 
