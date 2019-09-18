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

import pycurl, json
from io import BytesIO

def rpcCommand(method,params=[],ip='localhost',port='9012',id=1,jsonrpc="2.0",verbose=False):
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
 #           raise Exception('rpc_communication_error', 'return_code_not_200')
            return {'error':'rpc_comm_error','desc':'return_code_not_200','error_num':None}
        #close pycurl object
        c.close()
    except pycurl.error as e:
        c.close()
#        raise Exception('rpc_communication_error', 'return_code_not_200')\
        errno, message = e.args
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
            return data
        else:
            return {"error":"Unknown Error: possible method/parameter(s) were wrong and/or networking issue."}


def demonstration():
    data = rpcCommand(port=9012,method="net_peerCount",params=[])
    if isinstance(data, dict):
        if 'error' in data.keys():
            print (data['error'])
        else:
            print (data)
    else:
        print (data)

#    print (str(int(results,16)))


def demoAccounts():
    #get account balance
    results = rpcCommand(port=9012,method="eth_accounts",params=[])
    #print(str(results))
    for account in results:
        results = rpcCommand(port=9012,method="eth_getBalance",params=[account,"latest"])
        print( "Account:" +account + ", latest balance: " + str(int(results,16)))

def addPeer(ip,port,enode):
    results = rpcCommand(ip=ip,port=port,method="admin_addPeer",params=[enode])
    print (results)

def getEnodeInfo():
    results = rpcCommand(ip='10.4.209.29',port=9010,method="net_peerCount",params=[])
    print (results)

def getEnodeInfo(ip,port):
    results = rpcCommand(ip=ip,port=port,method="admin_nodeInfo",params=[])
    print (results)


import sys



##############################################################################
# 'main' entrypoint of script
##############################################################################

if __name__ == '__main__':
#    demonstration()
#    getEnode()
    #getEnodeInfo()
    addPeer(ip=sys.argv[1],port=sys.argv[2],enode=sys.argv[3])
