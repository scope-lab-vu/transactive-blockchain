from time import sleep

from config import *
from Geth import Geth

geth = Geth()
filterID = geth.command("eth_newFilter", params=[{"fromBlock": "0x1"}]) 
print("filterID = ", filterID)
account = geth.command("eth_accounts")[0]
print("account = ", account)
receiptID = geth.command("eth_sendTransaction", params=[{"data": BYTECODE, "gas": '0x4300000', "from": account}])
print("receiptID = ", receiptID)
receipt = None
while receipt is None:
  sleep(5)
  receipt = geth.command("eth_getTransactionReceipt", params=[receiptID])
  print("receipt = ", receipt)
  print("block = ", geth.command("eth_blockNumber"))
contract = receipt['contractAddress']
print("test transaction = ", geth.command("eth_sendTransaction", params=[{"to": contract, "data": '0xf8a8fd6d', "gas": '0x4300000', "from": account}]))
while True:
  sleep(5)
  print("log = ", geth.command("eth_getFilterChanges", params=[filterID]))

