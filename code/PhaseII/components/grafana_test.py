#!/usr/bin/python3
from Grafana.config import Config
from Grafana.dbase import Database
import time
import datetime

from config import *

finalized = Config.START_INTERVAL - 1
print(finalized)
current_time = time.time()

#strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_finalizing))
dbase = Database()

next_finalizing = current_time
strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_finalizing))

finalized = finalized + 1
EnergyTraded = 5000.0
ID = "109"
#dbase.log(strtime,"Solver", "TotalEnergyTraded", EnergyTraded)
dbase.log(finalized,"Solver1", "TotalEnergyTraded", EnergyTraded)
dbase.log(finalized,"Solver2", "TotalEnergyTraded", EnergyTraded+5000)

next_finalizing = next_finalizing + INTERVAL_LENGTH - 1
# strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_finalizing))
# dbase.log(strtime,"Solver", "TotalEnergyTraded", EnergyTraded)
dbase.log(finalized,"Solver", "TotalEnergyTraded", EnergyTraded)

finalized = finalized + 1
EnergyTraded = 15000.0
next_finalizing = next_finalizing + 1
# strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_finalizing))
# dbase.log(strtime,"Solver", "TotalEnergyTraded", EnergyTraded)
next_finalizing = next_finalizing + INTERVAL_LENGTH - 1
# strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_finalizing))
# dbase.log(strtime,"Solver", "TotalEnergyTraded", EnergyTraded)
dbase.log(finalized,"Solver", "TotalEnergyTraded", EnergyTraded)
