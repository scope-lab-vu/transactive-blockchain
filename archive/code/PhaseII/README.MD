To run single Miner and single Solver
~/projects/transactive-blockchain/code/PhaseII$ ./launch-m1s1.sh

To run 2 Miners and 2 Solvers with eventual Solver failure event
~/projects/transactive-blockchain/code/PhaseII$ ./failure.sh

Grafana : http://localhost:3000/dashboard/db/energy-market?refresh=5s&orgId=1
Row solver one with need to be updated to display the solver data.
click on "Solutions 1">edit
In "FROM default ****" click the stars field and select item Solver*** that is NOT the first one.

In the failure case do this for Solutions 2 as well. 

To look at miner logs
tail -f ~/ethereum/test_network_002_1/miners/00001/output.log

To look at DSO logs
~/projects/transactive-blockchain/code/PhaseII$ tail -f logs/DSO.out

To look at Solver logs
~/projects/transactive-blockchain/code/PhaseII$ tail -f logs/Solver.out

To look at Event Recorder logs
~/projects/transactive-blockchain/code/PhaseII$ tail -f logs/Recorder.out

To look at a prosumer log
~/projects/transactive-blockchain/code/PhaseII$ tail -f test-10-11-withbattery/prosumer101.out

To look at geth client the prosumers connect to in the failure example.
~/ethereum$ tail -f test_network_002_1/prosumer/00001/output.log
