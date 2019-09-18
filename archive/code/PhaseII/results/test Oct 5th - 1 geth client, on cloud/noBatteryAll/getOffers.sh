#!/bin/bash

cat solver.out | grep -iE "SellingOfferPosted|BuyingOfferPosted" | awk {'print $2 " " $5 " " $6 " " $8 " " $10 " " $12 " " $14 '} | sed s/}\).//g | sed s/\({\'/\ /g | sed s/\':/\ /g | sed s/,/\ /g | sed s/\ \ /\ /g | sed s/\ /,/g > offerData.csv
