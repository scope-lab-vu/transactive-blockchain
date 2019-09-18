#!/usr/bin/python

##############################################################################
#
# CLI tool to manage Ethereum Test Network.
#
#	Manages:
#		Clients
#		Blockchain
#		Miners
#		bootnodes
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


def getJsonValues(jsonFile, verbose=False,type='prosumer'):
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
        DSOs = clients["dso"]
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


    # a 'dict' to hold how many clients (prosumers) per host
    prosumerHostAllocation = {}



    # assign evenly divisible number of clients
    for x in prosumerHosts:
        prosumerHostAllocation[x] = prosumerCount / prosumerHostCount

    # determine non-evenly divisible (modulus/remainder) number of clients
    remainderProsumerClients = prosumerCount % len(prosumerHosts)

    # add remainder of clients to the appropriate number of hosts.
    for i in range(0,remainderProsumerClients):
        key = prosumerHostAllocation.keys()[i]
        prosumerHostAllocation[key] = prosumerHostAllocation[key] + 1


    # a 'dict' to hold how many clients (prosumers) per host
    dsoHostAllocation = {}

    # assign evenly divisible number of clients
    for x in dsoHosts:
        dsoHostAllocation[x] = dsoCount / dsoHostCount

    # determine non-evenly divisible (modulus/remainder) number of clients
    remainderDsoClients = dsoCount % len(dsoHosts)

    # add remainder of clients to the appropriate number of hosts.
    for i in range(0,remainderDsoClients):
        key = DsoHostAllocation.keys()[i]
        dsoHostAllocation[key] = dsoHostAllocation[key] + 1

    # return values
    if type == 'prosumer':
#        print "prosumer" + str(prosumerHostAllocation)
        return configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, chainId
    else:
 #       print "dso" + str(dsoHostAllocation)
        return configurationName , configurationVersion, dsoHostAllocation, clientStartPort, chainId




##############################################################################
# Prosumer Client Methods
##############################################################################


def createClients(jsonFile, type, verbose=False, outFile=''):
# create all prosumer clients
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, chainId = getJsonValues(jsonFile, verbose, type)

#    verboseResults = ""

    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort

    verboseResults = "prosumer port start = " + str(currentProsumerRpcPort)

    # how to make multidimensional array.
    #    w, h = 8, 5;
    #   Matrix = [[0 for x in range(w)] for y in range(h)]

    newClients = { "clients": []}
    # Loop through each Host to make their fab command.
    # this creates the new acounts for each host
    for host in prosumerHostAllocation:

        clientsThisHost = []

        currentProsumerRpcPort += prosumerHostAllocation[host]

        # start the command to setup the host, this is the fab function to call
        # note ':' before first paramater, and ',' before all following paramaters
        # Sample command:
        # fab -H eth4 createAccounts:numberOfClients=3,datadir="./.eth"
        command = "createAccounts"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",datadir=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/"+type+"/"
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
            verboseResults += "\n" + type + "s This Host: " + str(x)
            newClients["clients"].insert(0, x)

    if outFile <> '':
        if os.path.isfile(outFile) == True:
            data = readJsonFile(outFile, verbose)
#            print "\n\n\n\n"+str(data["clients"])+"\n\n\n\n"
            for client in newClients["clients"]:
                data["clients"].insert(0, client)
            newClients=data
        with open(str(outFile), 'w') as outfile:
            json.dump(newClients, outfile, indent=4, sort_keys=False)
        print "Newly Created Accounts JSON File output to: " + str(outFile)

    if verbose:
        print "\nCreated the following New accounts on the network.:\n"
        print verboseResults

    print "Created " + type + " Clients on each Host"
    return newClients


def startProsumerClients(jsonFile,verbose=False,overrideCommand=None,type="prosumer"):
# create all prosumer clients
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, networkId = getJsonValues(jsonFile,verbose,type)

    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort

    verboseResults = "prosumer port start = " + str(currentProsumerRpcPort)

    newClients = { "clients": []}
    # Loop through each Host to make their fab command.
    for host in prosumerHostAllocation:

        clientsThisHost = []

        # start the command to setup the host, this is the fab function to call
        # note ':' before first paramater, and ',' before all following paramaters
        command = "startClients"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",datadir=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/" +type+"/"
        command += ",startPort=" + str(currentProsumerRpcPort)
        command += ",network=" + str(networkId)
        command += ",clientType=" + str(type)
        command += ",isMiner=" + str(False)
        command += ",verbose=" + str(verbose)

        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        if overrideCommand == None:
            results = check_output(["fab", "-H", host, command ])
        else:
            results = check_output(["fab", "-H", host, overrideCommand ])

        verboseResults += "\nresults: " + str(results)
        currentProsumerRpcPort += prosumerHostAllocation[host]

    if verbose:
        print "\nCreated the following New accounts on the network.:\n"
        print verboseResults

    print "Started Prosumer Clients on each Host"
    return newClients



def stopProsumerClients(file, verbose=False,overrideCommand=None,type="prosumer"):
# will stop all prosumersClients
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, chainId = getJsonValues(file,verbose,type)

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
        command = "stopClients"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",network=" + str(chainId)
        command += ",clientType=" + str(type)
        command += ",isMiner=" + str(False)
        command += ",verbose=" + str(verbose)

        verboseResults += "\n\ncommand: " + str(command) + "\n\n"
        # call 'fab' with the correct host and parameters.
        if overrideCommand == None:
            results = check_output(["fab", "-H", host, command ])
        else:
            results = call(["fab", "-H", host, overrideCommand ])

        verboseResults += "\nresults: " + str(results)

    if verbose:
        print "\nCreated the following New accounts on the network.:\n"
        print verboseResults
    print "Stopped " +type+ " Clients on each Host"



def deleteProsumerClients(jsonFile,verbose=False,type="prosumer"):
# will delete all prosumerClients
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, chainId = getJsonValues(jsonFile,verbose,type)

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
        command = "deleteClients"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",datadir=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/"+type+"/"
        command += ",clientType=" + str(type)
        command += ",verbose=" + str(verbose)

        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        results = check_output(["fab", "-H", host, command ])

        verboseResults += "\nresults: " + str(results)

    if verbose:
        print "\nCreated the following New accounts on the network.:\n"
        print verboseResults
    print "Finished Deleting " + type + " Clients' data on each Host"


def distributeFilesToClients(jsonFile,inputDir,clientType='prosumer',subDirectory='',verbose=False):
# will delete all prosumerClients
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort, chainId = getJsonValues(jsonFile,verbose,clientType)

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


