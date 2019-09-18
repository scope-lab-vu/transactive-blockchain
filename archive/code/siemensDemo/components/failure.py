import zmq
import logging
import sys
from time import time, sleep

from config import *

from Grafana.config import Config
from Grafana.dbase import Database
import collections

import psutil


class Failure():
  def __init__(self):
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()

    self.dbase = Database()

  def fail(self,PID,name):
      logging.info("kill PID %s" %PID)
      p = psutil.Process(int(PID))
      p.terminate()  #or p.kill()
      #(self,interval, obj,seriesName,value)
      current_time = time()
      time_interval = int(current_time - self.epoch) // INTERVAL_LENGTH
      if (name == "S"):
          name = "Solver"
      if (name =="M"):
          name = "Miner"
      logging.info("kill %s:%s, is dead" %(name,PID))
      self.dbase.log(time_interval-1, name+str(PID), "failureEvents",  0)
      self.dbase.log(time_interval, name+str(PID), "failureEvents",  1)



  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.dso.send_pyobj(msg)
    response = self.dso.recv_pyobj()
    self.epoch = time() - response['time'] #DSO sends back how long its been running.
    logging.info("epoch : %s" %(self.epoch))
    self.contract_address = response['contract']
    logging.info("Contract address: " + self.contract_address)

if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  PID = None
  name = None
  if len(sys.argv) > 1:
    PID = sys.argv[1]
  if len(sys.argv) > 2:
    name = sys.argv[2]

  failure = Failure()
  failure.fail(PID, name)
