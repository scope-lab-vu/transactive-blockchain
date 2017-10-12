 nohup python3 ~/components/MatchingSolverWrapper.py 10.4.209.30 10000 > solver.out 2>&1 &
 
 for i in `ls data/*.csv | cut -d '_' -f2 |tr -d "*.csv"`;
 do 
 echo "launching prosumer $i"
 nohup python3 ~/components/SmartHomeTraderWrapper.py $i 10.4.209.30 10000 > prosumer$i.out 2>&1 &
 done
 
