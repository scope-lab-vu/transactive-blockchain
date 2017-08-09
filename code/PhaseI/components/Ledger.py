import zmq
import logging
  
from config import *
  
class Ledger: 
  def __init__(self):
    super(Ledger, self).__init__()
    
  def run(self):
    client = zmq.Context().socket(zmq.REP)
    client.bind(LEDGER_ADDRESS)
    while True:
      msg = client.recv_pyobj()
      logging.info(msg)
      try:
        result = "Success."
      except:
        result = "Malformed message."
      logging.info(result)
      client.send_pyobj(result)
                
if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  service = Ledger()
  service.run()
