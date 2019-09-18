import zmq
import logging
  
from config import *
from TradingService import TradingService
  
class Ledger(TradingService): 
  def __init__(self):
    super(Ledger, self).__init__()
    self.events = []
    
  def event(self, name, params):
    logging.info("{}({})".format(name, params))
    self.events.append((name, params))
    
  def poll_events(self, nextEvent):
    return {'nextEvent': len(self.events), 'events': self.events[nextEvent:]}

  def run(self):
    client = zmq.Context().socket(zmq.REP)
    client.bind(LEDGER_ADDRESS)
    while True:
      msg = client.recv_pyobj()
      try:
        function = msg['function']
        params = msg['params']
        if function == 'pollEvents':        
          logging.debug(msg)
          result = self.poll_events(params['nextEvent'])
        else: 
          logging.info(msg)
          result = "Success."
          if function == "addEnergyAsset":
            self.addEnergyAsset(params['address'], params['power'], params['start'], params['end'])
          elif function == "addFinancialBalance":
            self.addFinancialBalance(params['address'], params['amount'])
          elif function == "sendEther":
            pass  
          elif function == "postOffer":
            self.postOffer(params['sender'], params['assetID'], params['price'])
          elif function == "rescindOffer":
            self.rescindOffer(params['sender'], params['offerID'])
          elif function == "acceptOffer":
            self.acceptOffer(params['sender'], params['offerID'], params['assetID'])
          else:
            raise Exception("Unknown function!")
      except Exception as e:
        logging.warning(e)
      client.send_pyobj(result)
                
if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  service = Ledger()
  service.run()

