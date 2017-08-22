#!/usr/bin/python

##############################################################################
#
#
# @Author Michael A. Walker
# @Date 2017-06-27
#
##############################################################################

##############################################################################
# imports
##############################################################################

import json
from subprocess import call,check_output
from StringIO import StringIO
from subprocess import check_output,call
import re
import os.path
import sys, os
import stringcase

import clients

##############################################################################
#
##############################################################################

def to_camel_case(name):
# convert a string to camel_case all lower case.
    print name
    s1 = re.sub('(.)(\s)([A-Z][a-z]+)', r'\1_\3', name)
    print s1
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    print s2
    return s2


def readJsonFile(jsonFile, verbose=False):
# read in a json file and print it if verbose
    if os.path.isfile(jsonFile) <> True:
        print "Operand provided to be the network config file was not a file."
        sys.exit(2)
        return

    with open(str(jsonFile)) as data_file:
        data = json.load(data_file)

    # read in the configuration JSON file
    if verbose:
        print "\nRead in the following network-config json file:\n"
        print json.dumps(data, indent=4, sort_keys=False) + "\n"

    return data


def getMinerJsonValues(jsonFile, verbose=False):
# create all prosumer clients
    data = readJsonFile(jsonFile, verbose)

    try:

        ##########################################################################
        # get the values from the JSON file
        ##########################################################################

        # network specific data
        configurationName = data["configurationName"]
        configurationVersion = data["configurationVersion"]

        # genesis block data
        chainId = data["chainId"]
        difficulty= data["difficulty"]
        gasLimit = data["gasLimit"]
        balance = data["balance"]
        genesisBlockOutFile = data["genesisBlockOutFile"]

        # clients data
        clients = data["clients"]
        clientStartPort = clients["startPort"]

        # prosumer data
        prosumers = clients["prosumer"]
        prosumerProtocol = prosumers["protocol"]
        prosumerCount = prosumers["count"]
        prosumerHosts = prosumers["hosts"]
        prosumerHostCount = len(prosumerHosts)

        # miner data
        miners = clients["miner"]
        minerProtocol = miners["protocol"]
        minerCount = miners["count"]
        minerHosts = miners["hosts"]
        minerHostCount = len(minerHosts)

        # dso data
        DSOs = clients["miner"]
        dsoProtocol = DSOs["protocol"]
        dsoCount = DSOs["count"]
        dsoHosts = DSOs["hosts"]
        dsoHostCount = len(dsoHosts)

    except KeyError as inst:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ("KeyError:  " + str(inst)  + " was invalid in file: " + str(fname) +  " at line: " + str(exc_tb.tb_lineno) )
        print ("Please Try again...")
        sys.exit(3)

    hosts = minerHosts
    count = minerCount
    hostCount = minerHostCount

#    print " hosts : " + str(hosts) + " count: " + str(count) + " hostCount " + str(hostCount)

    # a 'dict' to hold how many clients (prosumers) per host
    hostAllocation = {}

    # assign evenly divisible number of clients
    for x in hosts:
        hostAllocation[x] = count / hostCount

    # determine non-evenly divisible (modulus/remainder) number of clients
    remainderClients = count % len(hosts)

    # add remainder of clients to the appropriate number of hosts.
    for i in range(0,remainderClients):
        key = hostAllocation.keys()[i]
        hostAllocation[key] = hostAllocation[key] + 1

    # return values
    return configurationName , configurationVersion, hostAllocation, clientStartPort, chainId




##############################################################################
# Miner Client Methods
##############################################################################


def createMinerClients(jsonFile,clientType='miners', out='new_miners.json',verbose=False):
# create all miner clients
    outFile = out

    # parse json file
    configurationName , configurationVersion, hostAllocation, clientStartPort, chainId  = getMinerJsonValues(jsonFile,verbose)
    currentProsumerRpcPort = clientStartPort

    verboseResults =  clientType + " port start = " + str(currentProsumerRpcPort)

    newClients = { "miners": []}
    # Loop through each Host to make their fab command.
    # this creates the new acounts for each host
    for host in hostAllocation:

        clientsThisHost = []
        currentProsumerRpcPort += hostAllocation[host]

        # start the command to setup the host, this is the fab function to call
        # note ':' before first paramater, and ',' before all following paramaters
        # Sample command:
        # fab -H eth4 createAccounts:numberOfClients=3,datadir="./.eth"
        command = "createAccounts"
        command += ":numberOfClients=" + str(hostAllocation[host])
        command += ",datadir=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/" + clientType + "/"
        command += ",verbose=" + str(verbose)

        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        results = check_output(["fab", "-H", host, command ])

        verboseResults += "\nresults: " + str(results)

        lines = results.split('\n')
        for line in lines:
            if line.startswith("Address"):
                verboseResults += "\nline with address: " + str(line)
                clientsThisHost.insert(0, line[10:50])
            else:
                verboseResults += "\nline with-out address: " + str(line)

        for x in clientsThisHost:
            verboseResults += "\nMiner Clients This Host: " + str(x)
            newClients['miners'].insert(0, x)

    if outFile <> '':
        with open(str(outFile), 'w') as outfile:
            json.dump(newClients, outfile, indent=4, sort_keys=False)
        print "Newly Created Accounts JSON File output to: " + str(outFile)

    if verbose:
        print "\nCreated the following New accounts on the network.:\n"
        print verboseResults

    print "Created Miner Clients on each Host"
    return newClients


def connectMinerClients(jsonFile,verbose=False):

    verboseResults = ""
    # get prosumer info
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, networkId = clients.logic.getJsonValues(jsonFile,verbose,'prosumer')
    # get dso info
    configurationName , configurationVersion, dsoHostAllocation, clientStartPort, networkId = clients.logic.getJsonValues(jsonFile,verbose,'dso')

    data = { "enodes": []}

    port = clientStartPort
  #  print str(prosumerHostAllocation)
    for host in prosumerHostAllocation:
        for client in range(int(prosumerHostAllocation[host])):
   #         print "host: " + str(host) + " port" + str(client+port)
            x = getEnode(host,client+port)
            data['enodes'].insert(0, x)
        port += int(prosumerHostAllocation[host])


    port = clientStartPort
 #   print str(dsoHostAllocation)
    for host in dsoHostAllocation:
        for client in range(int(dsoHostAllocation[host])):
    #        print "host: " + str(host) + " port" + str(client+port)
            x = getEnode(host,client+port)
            data['enodes'].insert(0, x)
        port += int(dsoHostAllocation[host])

    if verbose:
        print data

    configurationName , configurationVersion, minerHostAllocation, clientStartPort, networkId = getMinerJsonValues(jsonFile,verbose)

    for host in minerHostAllocation:
        verboseResults += "\nresults: "

        for enode in data['enodes']:
#            print enode + "\n"
            results = check_output(["./test/pycurlAddPeer.py", str(host), str(minerHostAllocation[host]+int(clientStartPort)+2000-1), str(enode) ])
            verboseResults += "\n" + str(results)
    if verbose:
        print verboseResults

#    print str(dsoHostAllocation)
#    getEnode("10.4.209.29", "9010")

def startMinerClients(jsonFile,verbose=False):
# create all prosumer clients
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, networkId = getMinerJsonValues(jsonFile,verbose)

    verboseResults = ""

    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = int(clientStartPort) + 2000

    verboseResults = "prosumer port start = " + str(currentProsumerRpcPort)

    newClients = { "miners": []}
    # Loop through each Host to make their fab command.
    for host in prosumerHostAllocation:
        clientsThisHost = []
        # start the command to setup the host, this is the fab function to call
        # note ':' before first paramater, and ',' before all following paramaters
        # Sample command:
        # fab -H eth4 ....
            #numberOfClients,datadir,startPort,network=15,verbose=False,isMiner=False
        command = "startClients"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",datadir=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/miners/"
        command += ",startPort=" + str(currentProsumerRpcPort)
        command += ",network=" + str(networkId)
        command += ",isMiner=" + str('True')
        command += ",clientType=" + str("miner")
        command += ",verbose=" + str(verbose)

        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        results = check_output(["fab", "-H", host, command ])

        verboseResults += "\nresults: " + str(results)
        currentProsumerRpcPort += prosumerHostAllocation[host]

    if verbose:
        print "\nStarted the following miner accounts on the network.:\n"
        print verboseResults

#    rpcCommand(ip='10.4.209.29',port=9010,method="net_peerCount",params=[])

    print "Started miner Clients on each Host"
    return newClients



def stopMinerClients(file, verbose=False):
# will stop all miner clients
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, chainId = getMinerJsonValues(file,verbose)

    verboseResults = ""

    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort

    verboseResults = "miner port start = " + str(currentProsumerRpcPort)

    newClients = { "miners": []}
    # Loop through each Host to make their fab command.
    for host in prosumerHostAllocation:

        clientsThisHost = []

        currentProsumerRpcPort += prosumerHostAllocation[host]

        # start the command to setup the host, this is the fab function to call
        # note ':' before first paramater, and ',' before all following paramaters
        # Sample command:
        # fab -H eth4 ....

        # stopClients(numberOfClients,network=15,verbose=False,isMiner

        command = "stopClients"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",network=" + str(chainId)
        command += ",clientType=" + "miner"
        command += ",isMiner=" + str(False)
        command += ",verbose=" + str(verbose)

        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        results = check_output(["fab", "-H", host, command ])

        verboseResults += "\nresults: " + str(results)

    if verbose:
        print "\nCreated the following New accounts on the network.:\n"
        print verboseResults

    # print newClients
    print "Stopped Miner blockchain clients on each Host"



def deleteMinerClients(file,verbose=False,type='miners'):
# will delete all miners
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, chainId = getMinerJsonValues(file,verbose)

    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort

    verboseResults = "prosumer port start = " + str(currentProsumerRpcPort)

    newClients = { "clients": []}
    # Loop through each Host to make their fab command.
    # this creates the new acounts for each host
    for host in prosumerHostAllocation:

        clientsThisHost = []

        currentProsumerRpcPort += prosumerHostAllocation[host]

        # start the command to setup the host, this is the fab function to call
        # note ':' before first paramater, and ',' before all following paramaters
        command = "deleteClients"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",datadir=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/" + type + "/"
        command += ",verbose=" + str(verbose)

        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        results = check_output(["fab", "-H", host, command ])

        verboseResults += "\nresults: " + str(results)

    if verbose:
        print "\nCreated the following New accounts on the network.:\n"
        print verboseResults
    print "Deleted Miner Clients' data on each Host"



def distributeFilesToClients(jsonFile,inputDir,clientType='miners',subDirectory='',verbose=False):
# will delete all prosumerClients
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, chainId = getMinerJsonValues(jsonFile,verbose)

    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort

    verboseResults = "prosumer port start = " + str(currentProsumerRpcPort)

    newClients = { "clients": []}
    # Loop through each Host to make their fab command.
    for host in prosumerHostAllocation:

        clientsThisHost = []
        currentProsumerRpcPort += prosumerHostAllocation[host]
        # start the command to call
        # note ':' before first paramater, and ',' before all following paramaters
        command = "copyLocalDir"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",localPath=" + str(inputDir)
        command += ",remotePath=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/" + str(clientType) + "/"
        command += ",subDir=" + str(subDirectory)
        command += ",verbose=" + str(verbose)

        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        results = check_output(["fab", "-H", host, command ])

        verboseResults += "\nresults: " + str(results)

    if verbose:
        print "\nCreated the following New accounts on the network.:\n"
        print verboseResults
    print "Finished Distributing Files to " + str(clientType) + " Clients' data on each Host"

def distributeFilesToClients2(jsonFile,inputDir,clientType='miners',subDirectory='',verbose=False):
# will delete all prosumerClients
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, chainId = getMinerJsonValues(jsonFile,verbose)

    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort

    verboseResults = "miner port start = " + str(currentProsumerRpcPort)

    newClients = { "clients": []}
    # Loop through each Host to make their fab command.
    for host in prosumerHostAllocation:

        clientsThisHost = []
        currentProsumerRpcPort += prosumerHostAllocation[host]
        # start the command to call
        # note ':' before first paramater, and ',' before all following paramaters
        command = "copyLocalDir"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",localPath=" + str(inputDir)
        command += ",remotePath=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/" + str(clientType) + "/"
        command += ",subDir=" + str(subDirectory)
        command += ",verbose=" + str(verbose)

        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        results = check_output(["fab", "-H", host, command ])

        verboseResults += "\nresults: " + str(results)

    if verbose:
        print "\ne network.:\n"
        print verboseResults
    print "Finished Distributing Files to " + str(clientType) + " Clients' data on each Host"


    verbose_results = ''
    results = ''
    mkdir_command = "mkdir -p " + datadir
    results = check_output( ["mkdir",  "-p" , str(datadir) ] )

    verbose_results += results + '\n'
    gethCommand = "geth  --datadir " + str(datadir) + " init " + str(jsonFile)
    print gethCommand
#    call([gethCommand])
#    results = check_output( [ gethCommand ] )
    results = check_output([ "geth", " --datadir ", datadir , " init ", jsonFile ])
    verbose_results += results + '\n'
    print results
    if verbose:
        print "** Verbose Output: **"
        print verbose_results


def getEnode(ip,port):
    results = check_output(["./test/pycurlGetEnode.py", str(ip), str(port) ]).rstrip()
    data = json.loads(results.replace("\'", "\""))
    return str(data['enode'].split('?')[0]).replace("[::]",str(ip))

#def rpcCommand():
#    results = check_output(["./test/pycurlUpgraded.py", "10.4.209.29", "9009" ]).rstrip()
#    data = json.loads(results.replace("\'", "\""))
#    print str(data['enode'].split('?')[0]).replace("[::]","10.4.209.29")


