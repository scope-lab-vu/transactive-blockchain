from time import sleep

from config import *
from gethRPC import gethRPC

filterID = gethRPC("eth_newFilter", params=[{"fromBlock": "0x1"}]) 
print("filterID = ", filterID)
account = gethRPC("eth_accounts")[0]
print("account = ", account)
receiptID = gethRPC("eth_sendTransaction", params=[{"data": BYTECODE, "gas": '0x4300000', "from": account}])
print("receiptID = ", receiptID)
receipt = None
while receipt is None:
  sleep(5)
  receipt = gethRPC("eth_getTransactionReceipt", params=[receiptID])
  print("receipt = ", receipt)
  print("block = ", gethRPC("eth_blockNumber"))
contract = receipt['contractAddress']
print("test transaction = ", gethRPC("eth_sendTransaction", params=[{"to": contract, "data": '0xf8a8fd6d', "gas": '0x4300000', "from": account}]))
while True:
  sleep(5)
  print("log = ", gethRPC("eth_getFilterChanges", params=[filterID]))

