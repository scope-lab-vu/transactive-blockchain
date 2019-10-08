from transax.EthereumClient import EthereumClient
from transax.MatchingContract import MatchingContract
from transax.MatchingSolver import MatchingSolver, Offer
import config as cfg
import time


ethclient = EthereumClient(ip='localhost', port=10001, TXGAS=cfg.TRANSACTION_GAS)

# account = ethclient.accounts()[0] # use the first owned address
account = "0x23a00db3c4d956abf86f2ca73a6d906910f3782f"


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
contractBYTECODE = '/home/riaps/projects/transactive-blockchain/transax/smartcontract/output/Matching.bin'
with open(contractBYTECODE) as f:
    BYTECODE = "0x"+f.read()
    contract_address = deploy_contract(BYTECODE, cfg.TRANSACTION_GAS)
    contract = MatchingContract(ethclient, contract_address)

contract.setup(account, cfg.MICROGRID.C_ext, cfg.MICROGRID.C_int, cfg.START_INTERVAL)
print("Contract address: " + contract_address)

prosumer_id = 102
txHash = contract.registerProsumer(account, prosumer_id, cfg.PROSUMER_FEEDER[prosumer_id])
receipt = wait4receipt(ethclient, txHash, "registerProsumer")

txHash = contract.registerProsumer(account, 103, cfg.PROSUMER_FEEDER[103])
receipt = wait4receipt(ethclient, txHash, "registerProsumer")
    
start_time = 1
end_time = 1
energy = 10
value = 5
txHash = contract.postBuyingOffer(account, prosumer_id, start_time, end_time, energy, value)
receipt = wait4receipt(ethclient, txHash, "postBuyingOffer")

txHash = contract.postSellingOffer(account, 103, start_time, end_time, energy, value)
receipt = wait4receipt(ethclient, txHash, "postSellingOffer")


buying_offers = []
selling_offers = []

for event in contract.poll_events():
    params = event['params']
    name = event['name']
    print("{}({}).".format(name, params))

    if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):
        new_offers = True
        offer = Offer(params['ID'], params['prosumer'], params['startTime'], params['endTime'], params['energy'], params['value'])
        if name == "BuyingOfferPosted":
            buying_offers.append(offer)
        else:
            selling_offers.append(offer)

#SOLVE - Double Auction
txHash = contract.startSolve(account, interval=1)
receipt = wait4receipt(ethclient, txHash, "startSolve")


for event in contract.poll_events():
    print("poll events")
    params = event['params']
    name = event['name']
    print("{}({}).".format(name, params))

    if (name == "Solve") :
        solveInterval = params['interval']
        txHash = contract.submitClearingPrice(account, solveInterval, price=10)
        receipt = wait4receipt(ethclient, txHash, "clearingPrice")


for event in contract.poll_events():
    params = event['params']
    name = event['name']
    print("{}({}).".format(name, params))

    if (name == "ClearingPrice"):
        interval = params['interval']
        price = params['price']
        print ("price in interval %s = %s" %(interval, price))

    if (name == "StartOffering"):
        nextInterval = params['interval']
        print ("next interval: %s" %nextInterval)
