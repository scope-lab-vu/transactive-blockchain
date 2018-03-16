#!/usr/bin/python3

##############################################################################
#
# Sample program to interact with ethereum RPC "2.0" with python.
#
#    Uses pycurl to HTTP POST query and returns json data.
#
# @Author   Michael A. Walker
# @Date     2017-08-06
#
##############################################################################

import pprint
import pycurl
import json
import sys
from io import BytesIO
import time


def rpcCommand(method,params=[],ip='localhost',port='9012',id=1,jsonrpc="2.0",verbose=False,exceptions=False):
    """ Method to abstract away 'curl' usage to interact with RPC of geth clients. """
    # the <ip:port> to connect to
    ipPort = str(ip) + ":" + str(port)
    # buffer to capture output
    buffer = BytesIO()
    # start building curl command to process
    try:
        c = pycurl.Curl()
        c.setopt(pycurl.URL, ipPort)
        c.setopt(pycurl.HTTPHEADER, ['Accept:application/json'])
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)
        data2 = {"jsonrpc":str(jsonrpc),"method": str(method),"params":params,"id":str(id)}
        data = json.dumps(data2)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        if verbose:
            c.setopt(pycurl.VERBOSE, 1)
        #perform pycurl
        c.perform()

        # check response code (HTTP codes)
        if (c.getinfo(pycurl.RESPONSE_CODE) != 200):
            if exceptions:
                raise Exception('rpc_communication_error', 'return_code_not_200')
            return {'error':'rpc_comm_error','desc':'return_code_not_200','error_num':None}
        #close pycurl object
        c.close()
    except pycurl.error as e:
        c.close()
        errno, message = e.args
        if exceptions:
            raise Exception('rpc_communication_error', 'Error No: ' + errno + ", message: " + message)
        return {'error':'rpc_comm_error','desc':message,'error_num':errno}


    # decode result
    results = str(buffer.getvalue().decode('iso-8859-1'))
    if verbose:
        print (results)

    # convert result to json object for parsing
    data = json.loads(results)
    # return appropriate result
    if 'result' in data.keys():
        return data["result"]
    else:
        if 'error' in data.keys():
            if exceptions:
                raise Exception('rpc_communication_error', data)
            return data
        else:
            if exceptions:
                raise Exception('rpc_communication_error', "Unknown Error: possible method/parameter(s) were wrong and/or networking issue.")
            return {"error":"Unknown Error: possible method/parameter(s) were wrong and/or networking issue."}


##############################################################################
# Helper methods to simplify blockchain interactions.
##############################################################################

def getPeerCount(ip,port,verbose=False):
    """ Get number of peers connected to target client. """
    results = rpcCommand(ip=ip,port=port,method="net_peerCount",params=[])
    if verbose == 'True':
        print ("number of peers connected to client at: " + ip + ":" + port + " is: " + results)
    return results

def getAccounts(ip,port,verbose=False):
    """ Get list of accounts on target geth client """
    results = rpcCommand(ip=ip,port=port,method="eth_accounts",params=[])
    if verbose == 'True':
        print ("Accounts: " + result)
    return results

def getBalance(ip,port,account=None,blockParameter="latest", verbose=False):
    """ Get balance of an account. Defaults to first account in client.
          blockParameter defaults to "latest", valid options are:
            String "earliest" for the earliest/genesis block
            String "latest" - for the latest mined block
            String "pending" - for the pending state/transactions
    """
    if blockParameter not in ['earliest', 'latest', 'pending']:
        return "blockParameter was not a valid option: 'earliest', 'latest', 'pending'."
    if account == None:
        if verbose == 'True':
            print ("No account given, querying first account on cliennt.")
        account = rpcCommand(ip=ip,port=port,method='eth_accounts')[0]
        if verbose == 'True':
            print ("   Account Number: " + account)
    results = rpcCommand(ip=ip,port=port,method="eth_getBalance",params=[account,blockParameter])
    if verbose == 'True':
        print( "Account:" +account + ", latest balance: " + results)
    return results

def addPeer(ip,port,enode,verbose=False):
    """ Add a peer to this client."""
    results = rpcCommand(ip=ip,port=port,method="admin_addPeer",params=[enode])
    if verbose == 'True':
        print (results)
    return results

def getEnodeInfo(ip,port,verbose=False):
    """ Get the node info of this client. """
    results = rpcCommand(ip=ip,port=port,method="admin_nodeInfo",params=[])
    if verbose == 'True':
        print ("Enode: " + results['enode'])
    return results['enode']

def deployContract(ip,port,gas = "0x4300000", contractBytecode="", account=None,verbose=False):
    if account == None:
        account = getAccounts(ip,port)[0]
        if verbose == 'True':
            print ("No acocunt provided, first acocunt on this client will be used: " + account)
    # Could add future check to see if account balance is suffient enough.
    # balance = getBalance(ip,port,results1[0])
    # balanceNeeded = .... calculation of contract size + gas offering, etc.
    # print ( "balance is not enough, ohly has: " + balance + " needs: " + balanceNeeded)

    params = [{'from':account, 'data': contractBytecode,'gas': gas}]

    results = rpcCommand(ip=ip,port=port,method="eth_sendTransaction",params=params)
    if verbose == 'True':
        print ("Transaction for deploying contract reciept results:" + results)
    # return receipt.
    return results


def getAddressOfTransaction(ip,port,transactionReceipt,account=None,verbose='False'):
    if account == None:
        account = getAccounts(ip,port)[0]
        if verbose == 'True':
            print ("No acocunt provided, first acocunt on this client will be used: " + account)
    results = rpcCommand("eth_getTransactionReceipt", params=[transactionReceipt], ip=ip, port=port)
    if verbose == 'True':
        print ("TransactionReceipt:")
        pprint.pprint(results)
#        if isinstance(results, dict):
#        else:
#            print ("TransactionReceipt:" + results)
    return results


def callContractMethod(ip,port,toAddress,dataString,gas="0x200000",account=None,verbose=False):
    if account == None:
        account = getAccounts(ip,port)[0]
        if verbose == 'True':
            print ("No acocunt provided, first acocunt on this client will be used: " + account)
    # Could add future check to see if account balance is suffient enough.
    # balance = getBalance(ip,port,results1[0])
    # balanceNeeded = .... calculation of contract size + gas offering, etc.
    # print ( "balance is not enough, ohly has: " + balance + " needs: " + balanceNeeded)
    results = rpcCommand(ip=ip,port=port,method="eth_sendTransaction",params=[{'from':account, 'to':toAddress, 'data': dataString, 'gas': gas}])
    if verbose == 'True':
        print ("Transaction results:" + results)
    return results

def getFilterChanges(ip,port,filterID,verbose=False):
    """ Get filter changes based on filter ID """
    results = rpcCommand(ip=ip,port=port,method="eth_getFilterChanges",params=[filterID])
    if verbose == 'True':
        print ("Filtered Events for FilterID <"+str(filterID)+">:")
        pprint.pprint(results)
    return results

def getBlockNumber(ip,port,verbose='False'):
    """ Get current block number. """
    results = rpcCommand(ip=ip,port=port,method="eth_blockNumber",params=[])
    if verbose == 'True':
        print ("Current block number is: " + results)
    return results

def getTransactionByHash(ip,port,hash,verbose='False'):
    """ Returns the information about a transaction requested by transaction hash. """
    results = rpcCommand(ip=ip,port=port,method='eth_getTransactionByHash',params=[hash])
    if verbose == 'True':
        print ("Transaction by hash:")
        pprint.pprint(results)
    return results

def makeNewFilter(ip,port,fromBlock="0x1",verbose='False'):
    # returned filter ID
    newFilterID = rpcCommand("eth_newFilter", params=[{'fromBlock':fromBlock}], ip=ip, port=port)
    if verbose == 'True':
        print ("Transaction by hash:" + newFilterID)
    return newFilterID


##############################################################################
# Experimental methods, not guarenteed to work!!!!!!
##############################################################################



def callMethodLocally(ip,port):
    address = listAccounts(ip,port)
    print (address)
    zeroInt32= "1".rjust(64,'0')
    print (zeroInt32)
    paramValues = {'to':address[0], 'gas':'0x20000', 'data':"0xcfae3217"+zeroInt32}
#    paramValues = {'to':address[0], 'gas':'0x20000', 'data':"0x23b87507" +zeroInt32+zeroInt32+zeroInt32+zeroInt32}
    results = rpcCommand(ip=ip,port=port,method='eth_call',params=[paramValues,"latest"])
    print (results)

def callMethod(ip,port):
    address = listAccounts(ip,port)
    print (address)
    paramValues = {'from':address[0],'to':address[0], 'gas':'0x20000', 'data':'0xf8a8fd6d'}
    results = rpcCommand(ip=ip,port=port,method='eth_sendTransaction',params=[paramValues])
    print (results)

def callMethod2(ip,port):
    address = listAccounts(ip,port)
    print (address)
    zeroInt32= "".rjust(64,'0')
    print (zeroInt32)
    paramValues = {'from':address[0],'to':address[0], 'gas':'0x20000', 'data':"0x23b87507" +zeroInt32+zeroInt32+zeroInt32+zeroInt32}
    results = rpcCommand(ip=ip,port=port,method='eth_sendTransaction',params=[paramValues])
    print (results)


def getHash(ip,port):
    paramValues = {"test()"}
    results = rpcCommand( ip=ip, port=port, method='eth_call', params=["test()"] )
    print (results)


##############################################################################
# 'main' entrypoint of script
##############################################################################

def testSetup(ip,port):
    # Here is the contract
    contractBytecode = '0x60606040526000600360006101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055506000600560006101000a81548167ffffffffffffffff021916908367ffffffffffffffff160217905550341561006357600080fd5b5b336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055505b5b6123eb806100b56000396000f3006060604052361561008c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806323b87507146100915780633436bd0c146101245780633b719dc014610151578063cb791be91461019d578063cbfd042f146101ca578063ed7272e2146101f7578063f1edd7e21461025f578063f8a8fd6d1461029f575b600080fd5b341561009c57600080fd5b6100fa600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803560070b90602001909190803567ffffffffffffffff1690602001909190803567ffffffffffffffff169060200190919050506102b4565b604051808267ffffffffffffffff1667ffffffffffffffff16815260200191505060405180910390f35b341561012f57600080fd5b61014f600480803567ffffffffffffffff16906020019091905050610352565b005b341561015c57600080fd5b61019b600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803567ffffffffffffffff169060200190919050506104ca565b005b34156101a857600080fd5b6101c8600480803567ffffffffffffffff16906020019091905050610628565b005b34156101d557600080fd5b6101f5600480803567ffffffffffffffff16906020019091905050610894565b005b341561020257600080fd5b610235600480803567ffffffffffffffff1690602001909190803567ffffffffffffffff16906020019091905050610b9f565b604051808267ffffffffffffffff1667ffffffffffffffff16815260200191505060405180910390f35b341561026a57600080fd5b61029d600480803567ffffffffffffffff1690602001909190803567ffffffffffffffff169060200190919050506111cc565b005b34156102aa57600080fd5b6102b2611b92565b005b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561031157600080fd5b6103478560008660070b1361032757600161032a565b60005b60008760070b1361033e5786600003610340565b865b8686611c4d565b90505b949350505050565b8067ffffffffffffffff16600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff1667ffffffffffffffff16101515156103c857600080fd5b80600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160392506101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055507f6ea1dc127cb431ed30f9518c083ebb1afd5fef492456dea55227403a46e025fb3382604051808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff1681526020019250505060405180910390a15b50565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561052557600080fd5b80600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160192506101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055507f4a4bcdba1fdd3486b8dad947841b692814e16275e05e493465222f13287e779a8282604051808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff1681526020019250505060405180910390a15b5050565b600080600360009054906101000a900467ffffffffffffffff1667ffffffffffffffff168367ffffffffffffffff1610151561066357600080fd5b600260008467ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002091508160000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161415156106ea57600080fd5b308260000160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506000600181111561073a57fe5b8260000160149054906101000a900460ff16600181111561075757fe5b1461077d578160000160159054906101000a900467ffffffffffffffff16600003610797565b8160000160159054906101000a900467ffffffffffffffff165b90507f6efbe3bb6c0a76bcd5d282b89fd10c1462d449b514f73f7393039485f770bfd53384838560010160009054906101000a900467ffffffffffffffff168660010160089054906101000a900467ffffffffffffffff16604051808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018567ffffffffffffffff1667ffffffffffffffff1681526020018460070b60070b81526020018367ffffffffffffffff1667ffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff1681526020019550505050505060405180910390a15b505050565b600080600460008467ffffffffffffffff1667ffffffffffffffff1681526020019081526020016000209150600260008360000160159054906101000a900467ffffffffffffffff1667ffffffffffffffff1667ffffffffffffffff1681526020019081526020016000209050600560009054906101000a900467ffffffffffffffff1667ffffffffffffffff168367ffffffffffffffff1610151561093957600080fd5b3373ffffffffffffffffffffffffffffffffffffffff168260000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1614151561099757600080fd5b600060028111156109a457fe5b8260010160089054906101000a900460ff1660028111156109c157fe5b1415156109cd57600080fd5b60018260010160086101000a81548160ff021916908360028111156109ee57fe5b0217905550338160000160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550600180811115610a4257fe5b8260000160149054906101000a900460ff166001811115610a5f57fe5b1415610b4e578060010160009054906101000a900467ffffffffffffffff1660018260010160089054906101000a900467ffffffffffffffff1601038160000160159054906101000a900467ffffffffffffffff168360010160009054906101000a900467ffffffffffffffff160202600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160192506101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055505b7fae4ff21dfe29840d9ecf23fcfa2dadbe7fed7bebb0aecc06e047f6bb0a30200b83604051808267ffffffffffffffff1667ffffffffffffffff16815260200191505060405180910390a15b505050565b6000806000806000600260008867ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002093508360010160009054906101000a900467ffffffffffffffff1660018560010160089054906101000a900467ffffffffffffffff1601038460000160159054906101000a900467ffffffffffffffff168702029250600360009054906101000a900467ffffffffffffffff1667ffffffffffffffff168767ffffffffffffffff16101515610c5c57600080fd5b3373ffffffffffffffffffffffffffffffffffffffff168460000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16141515610cba57600080fd5b600180811115610cc657fe5b8460000160149054906101000a900460ff166001811115610ce357fe5b1415610d60578267ffffffffffffffff16600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff1667ffffffffffffffff1610151515610d5f57600080fd5b5b308460000160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550600180811115610daf57fe5b8460000160149054906101000a900460ff166001811115610dcc57fe5b1415610e5a5782600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160392506101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060019150610e5f565b600091505b60a0604051908101604052803373ffffffffffffffffffffffffffffffffffffffff168152602001836001811115610e9357fe5b81526020018867ffffffffffffffff1681526020018767ffffffffffffffff16815260200160006002811115610ec557fe5b81525060046000600560009054906101000a900467ffffffffffffffff1667ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008201518160000160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555060208201518160000160146101000a81548160ff02191690836001811115610f7057fe5b021790555060408201518160000160156101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060608201518160010160006101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060808201518160010160086101000a81548160ff02191690836002811115610ff757fe5b02179055509050506000600181111561100c57fe5b8460000160149054906101000a900460ff16600181111561102957fe5b1461104f578360000160159054906101000a900467ffffffffffffffff16600003611069565b8360000160159054906101000a900467ffffffffffffffff165b90507ece43d5445de1586c54d6b80a0c597a8ffdd10c34fc77857a59cbfbb8eee97d600560009054906101000a900467ffffffffffffffff1688838760010160009054906101000a900467ffffffffffffffff168860010160089054906101000a900467ffffffffffffffff168b604051808767ffffffffffffffff1667ffffffffffffffff1681526020018667ffffffffffffffff1667ffffffffffffffff1681526020018560070b60070b81526020018467ffffffffffffffff1667ffffffffffffffff1681526020018367ffffffffffffffff1667ffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff168152602001965050505050505060405180910390a16005600081819054906101000a900467ffffffffffffffff168092919060010191906101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555094505b5050505092915050565b6000806000806000806000600460008a67ffffffffffffffff1667ffffffffffffffff1681526020019081526020016000209650600260008860000160159054906101000a900467ffffffffffffffff1667ffffffffffffffff1667ffffffffffffffff1681526020019081526020016000209550600260008967ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002094508460010160009054906101000a900467ffffffffffffffff1667ffffffffffffffff168660010160009054906101000a900467ffffffffffffffff1667ffffffffffffffff16116112d3578460010160009054906101000a900467ffffffffffffffff166112ed565b8560010160009054906101000a900467ffffffffffffffff165b93508460010160089054906101000a900467ffffffffffffffff1667ffffffffffffffff168660010160089054906101000a900467ffffffffffffffff1667ffffffffffffffff1610611358578460010160089054906101000a900467ffffffffffffffff16611372565b8560010160089054906101000a900467ffffffffffffffff165b92508460000160159054906101000a900467ffffffffffffffff1667ffffffffffffffff168660000160159054906101000a900467ffffffffffffffff1667ffffffffffffffff16106113dd578460000160159054906101000a900467ffffffffffffffff166113f7565b8560000160159054906101000a900467ffffffffffffffff165b9150836001840103828860010160009054906101000a900467ffffffffffffffff1602029050600560009054906101000a900467ffffffffffffffff1667ffffffffffffffff168967ffffffffffffffff1610151561145557600080fd5b600360009054906101000a900467ffffffffffffffff1667ffffffffffffffff168867ffffffffffffffff1610151561148d57600080fd5b6000600281111561149a57fe5b8760010160089054906101000a900460ff1660028111156114b757fe5b1415156114c357600080fd5b3373ffffffffffffffffffffffffffffffffffffffff168560000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1614151561152157600080fd5b8460010160009054906101000a900467ffffffffffffffff1667ffffffffffffffff168660010160089054906101000a900467ffffffffffffffff1667ffffffffffffffff161080156115b757508460010160089054906101000a900467ffffffffffffffff1667ffffffffffffffff168660010160009054906101000a900467ffffffffffffffff1667ffffffffffffffff16115b1515156115c357600080fd5b600060018111156115d057fe5b8760000160149054906101000a900460ff1660018111156115ed57fe5b14156116a3576001808111156115ff57fe5b8560000160149054906101000a900460ff16600181111561161c57fe5b14151561162857600080fd5b8067ffffffffffffffff16600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900467ffffffffffffffff1667ffffffffffffffff161015151561169e57600080fd5b6116da565b600060018111156116b057fe5b8660000160149054906101000a900460ff1660018111156116cd57fe5b1415156116d957600080fd5b5b8660000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff168660000160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506117638760000160159054906101000a900467ffffffffffffffff1685612023565b61176d8885612023565b61178f8760000160159054906101000a900467ffffffffffffffff1684612162565b6117998884612162565b6117bb8760000160159054906101000a900467ffffffffffffffff16836122a1565b6117c588836122a1565b600060018111156117d257fe5b8760000160149054906101000a900460ff1660018111156117ef57fe5b141561191c5780600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160392506101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555080600160008960000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160192506101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555061199c565b80600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008282829054906101000a900467ffffffffffffffff160192506101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055505b8660000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff168560000160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550338660000160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555060028760010160086101000a81548160ff02191690836002811115611a6757fe5b02179055507f0af11ecfa0ce9284e22f65068ff6043b4ffabbcf5eeeace0f315d1e1ea5d1b70898960006001811115611a9c57fe5b8960000160149054906101000a900460ff166001811115611ab957fe5b14611ac75784600003611ac9565b845b87878c60010160009054906101000a900467ffffffffffffffff16604051808767ffffffffffffffff1667ffffffffffffffff1681526020018667ffffffffffffffff1667ffffffffffffffff1681526020018560070b60070b81526020018467ffffffffffffffff1667ffffffffffffffff1681526020018367ffffffffffffffff1667ffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff168152602001965050505050505060405180910390a15b505050505050505050565b600080600080611ba4336103e86104ca565b611baf6101f4610352565b611bbb336107d06104ca565b611bc66103e8610352565b611bd53360646008600a6102b4565b9350611c05337fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff386009600b6102b4565b9250611c1284600a610b9f565b9150611c1d82610894565b611c28846005610b9f565b9050611c3481846111cc565b611c3d84610628565b611c4683610628565b5b50505050565b600060a0604051908101604052808773ffffffffffffffffffffffffffffffffffffffff168152602001866001811115611c8357fe5b81526020018567ffffffffffffffff1681526020018467ffffffffffffffff1681526020018367ffffffffffffffff1681525060026000600360009054906101000a900467ffffffffffffffff1667ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002060008201518160000160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555060208201518160000160146101000a81548160ff02191690836001811115611d5e57fe5b021790555060408201518160000160156101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060608201518160010160006101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555060808201518160010160086101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555090505060006001811115611e0057fe5b856001811115611e0c57fe5b1415611ef2577fc2b1f94b59151b30c16e3d9672f8b2128b809750f3edd22efa3d49d8ad245b1886600360009054906101000a900467ffffffffffffffff16868686604051808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018567ffffffffffffffff1667ffffffffffffffff1681526020018460070b60070b81526020018367ffffffffffffffff1667ffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff1681526020019550505050505060405180910390a1611fd1565b7fc2b1f94b59151b30c16e3d9672f8b2128b809750f3edd22efa3d49d8ad245b1886600360009054906101000a900467ffffffffffffffff16866000038686604051808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018567ffffffffffffffff1667ffffffffffffffff1681526020018460070b60070b81526020018367ffffffffffffffff1667ffffffffffffffff1681526020018267ffffffffffffffff1667ffffffffffffffff1681526020019550505050505060405180910390a15b6003600081819054906101000a900467ffffffffffffffff168092919060010191906101000a81548167ffffffffffffffff021916908367ffffffffffffffff16021790555090505b95945050505050565b6000600260008467ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002090508167ffffffffffffffff168160010160009054906101000a900467ffffffffffffffff1667ffffffffffffffff161080156120b557508167ffffffffffffffff168160010160089054906101000a900467ffffffffffffffff1667ffffffffffffffff1610155b1561215c5761212f8160000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff168260000160149054906101000a900460ff168360000160159054906101000a900467ffffffffffffffff168460010160009054906101000a900467ffffffffffffffff1660018703611c4d565b50818160010160006101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055505b5b505050565b6000600260008467ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002090508167ffffffffffffffff168160010160009054906101000a900467ffffffffffffffff1667ffffffffffffffff16111580156121f457508167ffffffffffffffff168160010160089054906101000a900467ffffffffffffffff1667ffffffffffffffff16115b1561229b5761226e8160000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff168260000160149054906101000a900460ff168360000160159054906101000a900467ffffffffffffffff16600186018560010160089054906101000a900467ffffffffffffffff16611c4d565b50818160010160086101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055505b5b505050565b6000600260008467ffffffffffffffff1667ffffffffffffffff16815260200190815260200160002090508167ffffffffffffffff168160000160159054906101000a900467ffffffffffffffff1667ffffffffffffffff1611156123b95761238c8160000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff168260000160149054906101000a900460ff16848460000160159054906101000a900467ffffffffffffffff16038460010160089054906101000a900467ffffffffffffffff168560010160089054906101000a900467ffffffffffffffff16611c4d565b50818160000160156101000a81548167ffffffffffffffff021916908367ffffffffffffffff1602179055505b5b5050505600a165627a7a72305820732a9f8e2f85faa6b0d7272a5af04386224cdf5a9f9a1831302a4f921f4cd34e0029'
    sleepTime = 10 #should be fine with our default template network-config.json file.
    print ("*** Sleeping for "+str(sleepTime)+" seconds to allow for mining of first transaction.")
    time.sleep(sleepTime)

    # Make a new filter (locally (Need to double check to make sure.)). Note: Filter doesn't yet have any info about contract.
    newFilterID = makeNewFilter(ip=ip,port=port,fromBlock="0x0",verbose='False')
    print ("*** New Filter ID: " + str(newFilterID))


    # Submit the contract as a transaction.
    transactionReceipt = deployContract(ip=ip,port=port,contractBytecode=contractBytecode,verbose='True')
    print ("*** Smart Contract Submission TransactionReceipt: ")
    pprint.pprint(transactionReceipt)
    # Sleep for some time to allow mining of transaction's block to finish.
    print ("*** Sleeping for "+str(sleepTime)+" seconds to allow for mining of transaction.")
    time.sleep(sleepTime)
    # get the address of the contract, after its transaction has been mined into a complete block.
    contractAddress = getAddressOfTransaction(ip=ip,port=port,transactionReceipt=transactionReceipt,verbose='False')['contractAddress']
    print ("*** Contract Address: " + contractAddress)

    # Call 'test()' in the smart contract.
    transactionReceipt2 = callContractMethod(ip=ip,port=port,toAddress=contractAddress,dataString="0xf8a8fd6d",gas="0x4300000",account=None,verbose='True')

    # Sleep for some time to allow mining of transaction's block to finish.
    print ("*** Sleeping for "+str(sleepTime)+" seconds to allow for mining of transaction.")
    time.sleep(sleepTime)


    changeResults = getFilterChanges(ip=ip,port=port,filterID=newFilterID,verbose="True")
    print ("*** change results: ")
    pprint.pprint(changeResults)


#############################
if __name__ == '__main__':
    ip = sys.argv[1]
    port = sys.argv[2]
    testSetup(ip,port)
