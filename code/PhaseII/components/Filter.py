import logging

from config import *
from EthereumClient import EthereumClient

TOPICS = {
  '0x4a4bcdba1fdd3486b8dad947841b692814e16275e05e493465222f13287e779a': "FinancialAdded",
  '0x6ea1dc127cb431ed30f9518c083ebb1afd5fef492456dea55227403a46e025fb': "FinancialDeposited",
  '0xc2b1f94b59151b30c16e3d9672f8b2128b809750f3edd22efa3d49d8ad245b18': "AssetAdded",
  '0x6efbe3bb6c0a76bcd5d282b89fd10c1462d449b514f73f7393039485f770bfd5': "AssetDeposited",
  '0x00ce43d5445de1586c54d6b80a0c597a8ffdd10c34fc77857a59cbfbb8eee97d': "OfferPosted",
  '0xae4ff21dfe29840d9ecf23fcfa2dadbe7fed7bebb0aecc06e047f6bb0a30200b': "OfferRescinded",
  '0x0af11ecfa0ce9284e22f65068ff6043b4ffabbcf5eeeace0f315d1e1ea5d1b70': "OfferAccepted",
}

class Filter:
  def __init__(self, client):
    self.client = client
    self.filterID = self.client.command("eth_newFilter", params=[{"fromBlock": "0x1"}]) 
    logging.info("Created filter (ID = {}).".format(self.filterID))
    
  def poll_events(self):
    block = self.client.command("eth_blockNumber", params=[])
    log = self.client.command("eth_getFilterChanges", params=[self.filterID])
    logging.debug("Log: {} items (block number: {})".format(len(log), block))
    for log_item in log:
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
    if event == "FinancialAdded":
      params = {'address': decode_address(data, 0), 'amount': decode_uint(data, 1)}
    elif event == "FinancialDeposited":
      params = {'address': decode_address(data, 0), 'amount': decode_uint(data, 1)}
    elif event == "AssetAdded":
      params = {
        'address': decode_address(data, 0), 
        'assetID': decode_uint(data, 1), 
        'power': decode_int(data, 2),
        'start': decode_uint(data, 3),
        'end': decode_uint(data, 4),
      }
    elif event == "AssetDeposited":
      params = {
        'address': decode_address(data, 0), 
        'assetID': decode_uint(data, 1), 
        'power': decode_int(data, 2),
        'start': decode_uint(data, 3),
        'end': decode_uint(data, 4),
      }
    elif event == "OfferPosted":
      params = {
        'offerID': decode_uint(data, 0),
        'assetID': decode_uint(data, 1),
        'power': decode_int(data, 2),
        'start': decode_uint(data, 3),
        'end': decode_uint(data, 4),
        'price': decode_uint(data, 5),
      }
    elif event == "OfferRescinded":
      params = { 'offerID': decode_uint(data, 0) }
    elif event == "OfferAccepted":
      params = {
        'offerID': decode_uint(data, 0),
        'assetID': decode_uint(data, 1),
        'transPower': decode_int(data, 2),
        'transStart': decode_uint(data, 3),
        'transEnd': decode_uint(data, 4),
        'price': decode_uint(data, 5),
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
    "FinancialAdded(address,uint64)",
    "FinancialDeposited(address,uint64)",
    "AssetAdded(address,uint64,int64,uint64,uint64)",
    "AssetDeposited(address,uint64,int64,uint64,uint64)",
    "OfferPosted(uint64,uint64,int64,uint64,uint64,uint64)",
    "OfferRescinded(uint64)",
    "OfferAccepted(uint64,uint64,int64,uint64,uint64,uint64)",
  ]
  for event in events:
    keccak256(event, 192.168.1.2, 9000)
    
# test
if __name__ == "__main__":
  test_log = []
  for log_item in test_log:
    print(decode_log(log_item))



