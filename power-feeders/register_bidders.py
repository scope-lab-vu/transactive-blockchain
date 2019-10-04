from core.EthereumClient import EthereumClient
from core.MatchingContract import MatchingContract
from core.MatchingSolver import MatchingSolver, Offer
import config as cfg
import time
import numpy as np

ethclient = EthereumClient(ip='localhost', port=10000, TXGAS=cfg.TRANSACTION_GAS)

account = ethclient.accounts()[0] # use the first owned address


def wait4receipt(ethclient,txHash,name,getReceipt=True):

    if not getReceipt:
        receipt = {}
        receipt['gasUsed'] = -1
        receipt['cumulativeGasUsed'] = -1
        print("Did not wait for receipt")
        return receipt

    if txHash.startswith("0x"): 

        receipt = ethclient.command("eth_getTransactionReceipt", params=[txHash])       
        while receipt is None or "ERROR" in receipt:
            
            print("Waiting for tx to be mined... (block number: {})".format(ethclient.command("eth_blockNumber", params=[])))
            time.sleep(5) 

            receipt = ethclient.command("eth_getTransactionReceipt", params=[txHash])

        if receipt['gasUsed'] == cfg.TRANSACTION_GAS:
            print("Transaction may have failed. gasUsed = gasLimit")

        print("%s gasUsed: %s" %(name,receipt['gasUsed']))
        print("%s cumulativeGasUsed: %s" %(name,receipt['cumulativeGasUsed']))

        return receipt


def deploy_contract(BYTECODE, TXGAS):
    print("Deploying contract...")
    # use command function because we need to get the contract address later
    txHash = ethclient.command("eth_sendTransaction", params=[{'data': BYTECODE, 'from': account, 'gas': TXGAS}])
    print("Transaction hash: " + txHash)

    receipt = wait4receipt(ethclient, txHash, "deployContract")

    contract_address = receipt['contractAddress']

    return contract_address


contract = None
contractBYTECODE = '/home/riaps/projects/transactive-blockchain/transax/smartcontract/output/MatchingContract.bin'
with open(contractBYTECODE) as f:
    BYTECODE = "0x"+f.read()
    contract_address = deploy_contract(BYTECODE, cfg.TRANSACTION_GAS)
    contract = MatchingContract(ethclient, contract_address)

contract.setup(account, cfg.MICROGRID.C_ext, cfg.MICROGRID.C_int, cfg.START_INTERVAL)
print("Contract address: " + contract_address)



#################################################################
# load the list of bidders
file_bidders = './power-feeders/bidders'
list_bidders = {}
with open(file_bidders, 'r') as f_bidders:
    prosumer_id = 0
	for x in f_bidders:        
		list_bidders[x]=prosumer_id
        prosumer_id = prosumer_id + 1

# save the dictionary
np.save('id_bidders.npy', list_bidders)


# register prosumers
for bidder in list_bidders:
    prosumer_id = list_bidders[bidder]
	txHash = contract.registerProsumer(account, prosumer_id, cfg.PROSUMER_FEEDER[prosumer_id])
	receipt = wait4receipt(ethclient, txHash, "registerProsumer")


# write the address of the contract
file_name = 'contract_address'
try:
	os.remove(file_name)
except:
	pass

f = open(file_name, 'w')
f.write( contract_address )
f.close()





