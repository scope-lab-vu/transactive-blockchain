#!/bin/bash

grep -nis "Iterations:" solver.out | sed s/2017-10/\ /g | sed s/:/,/g| awk {'print $1$3'} > iterations.csv
#grep -is "Iterations:" solver.out | sed s/2017-10/\ /g | awk {'print $2'} > iterationCounts.txt
