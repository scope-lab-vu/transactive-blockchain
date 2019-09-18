run ./launch-m1s1.sh

Wait for the prompt from the launching terminal which will say :
"Wait for at least 15 blocks to be mined. Then press enter to start Market"

Wait for the 15 blocks, and press enter. The market and prosumers will launch.

Open Grafana
http://localhost:3000/dashboard/db/energy-market?refresh=5s&orgId=1

update solver 1
click on "Solutions 1">edit
In "FROM default ****" click the stars field and select item Solver*** that is NOT the first one.
