from time import sleep

from config import *
from EthereumClient import EthereumClient
from Filter import decode_log

ip=192.168.1.2
port=9000
geth = EthereumClient(ip=ip, port=port)
filterID = geth.command("eth_newFilter", params=[{"fromBlock": "0x1"}]) 
print("filterID = ", filterID)
account = geth.command("eth_accounts")[0]
print("account = ", account)
receiptID = geth.command("eth_sendTransaction", params=[{"data": BYTECODE, "gas": TRANSACTION_GAS, "from": account}])
print("receiptID = ", receiptID)
receipt = None
while receipt is None:
  sleep(5)
  receipt = geth.command("eth_getTransactionReceipt", params=[receiptID])
  print("block = ", geth.command("eth_blockNumber"))
  print("receipt = ", receipt)
contract = receipt['contractAddress']
print("test transaction = ", geth.command("eth_sendTransaction", params=[{"to": contract, "data": '0xf8a8fd6d', "gas": TRANSACTION_GAS, "from": account}]))
while True:
  sleep(5)
  print("block = ", geth.command("eth_blockNumber"))
  log = geth.command("eth_getFilterChanges", params=[filterID])
  print("log = ", log)
  for log_item in log:
    print(decode_log(log_item))

