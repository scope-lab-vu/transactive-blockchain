import logging

from config import *
from EthereumClient import EthereumClient

TOPICS = {
  '0x47be5dd1d9aeb3db0a9753c2d318b0140db2a5524856bd0b17bd92b4b1da8ede': 'BuyingOfferPosted',
  '0xb0f09a7c285d588112f109144f5e334575b9cd0a6b1ec1c0a5ca6949ab815000': 'SellingOfferPosted',
  '0x25346e016c4cdf007ed72a549d9e82213a82d4f742035bfe48286948ed7ab4e7': 'SolutionCreated',
  '0x15640476521fd414bd504b67b615bbd406c0147e66a8b99bc4c6e79d85686593': 'TradeAdded',
}

class Filter:
  def __init__(self, client, address=None):
    self.client = client
    self.address = address
    self.filterID = self.client.command("eth_newFilter", params=[{"fromBlock": "0x1"}]) 
    logging.info("Created filter (ID = {}).".format(self.filterID))
    
  def poll_events(self):
    block = self.client.command("eth_blockNumber", params=[])
    log = self.client.command("eth_getFilterChanges", params=[self.filterID])
    logging.debug("Log: {} items (block number: {})".format(len(log), block))
    for log_item in log:
      if (self.address is None) or (self.address == log_item['address']):
        yield decode_log(log_item)

def decode_address(data, pos):
  return "0x" + data[pos * 64 + 24 : (pos + 1) * 64]
def decode_uint(data, pos):
  return int(data[pos * 64 : (pos + 1) * 64], 16)
def decode_int(data, pos):
  uint = decode_uint(data, pos)
  if uint > 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff:
    uint -= 0x10000000000000000000000000000000000000000000000000000000000000000
  return uint

def decode_log(log):
  contract = log['address']
  params = log['data']
  try:
    event = (TOPICS[log['topics'][0]])
    data = log['data'][2:]
    if event == "SolutionCreated":
      params = {
        'ID': decode_uint(data, 0)
      }
    elif event == "TradeAdded":
      params = {
        'solutionID': decode_uint(data, 0), 
        'objective': decode_uint(data, 1)
      }
    elif event == "BuyingOfferPosted":
      params = {
        'ID': decode_uint(data, 0),
        'prosumer': decode_uint(data, 1),
        'startTime': decode_int(data, 2),
        'endTime': decode_uint(data, 3),
        'energy': decode_uint(data, 4),
      }
    elif event == "SellingOfferPosted":
      params = {
        'ID': decode_uint(data, 0),
        'prosumer': decode_uint(data, 1),
        'startTime': decode_int(data, 2),
        'endTime': decode_uint(data, 3),
        'energy': decode_uint(data, 4),
      }
  except KeyError:
    event = "unknown"
  return {'from': contract, 'name': event, 'params': params}
  
# generate topics from event signatures
  
def keccak256(string, ip, port):
  client = EthereumClient(ip=ip, port=port)
  print("  '{}': '{}',".format(client.command("web3_sha3", params=["0x" + bytes(string, 'ascii').hex()] ), string))

def generate_topics():
  events = [
    "BuyingOfferPosted(uint64,uint64,uint64,uint64,uint64)",
    "SellingOfferPosted(uint64,uint64,uint64,uint64,uint64)",
    "SolutionCreated(uint64)",
    "TradeAdded(uint64,uint64)",
  ]
  for event in events:
    keccak256(event, "10.4.209.25", 9005)
    
# test
if __name__ == "__main__":
  generate_topics()
#  test_log = []
#  for log_item in test_log:
#    print(decode_log(log_item))



