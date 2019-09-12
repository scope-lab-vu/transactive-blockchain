#!/usr/bin/python

##############################################################################
#
# This file contians the code to interact with bootnodes
#
# @Author Michael A. Walker
# @Date 2017-06-27
#
##############################################################################

##############################################################################
# imports
##############################################################################
import json
from subprocess import call, check_output
from StringIO import StringIO
from subprocess import check_output, call
import re
import os.path
import sys, os
import stringcase

##############################################################################
# Helper Methods
##############################################################################

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

def getJsonValues(jsonFile, verbose=False):
    """ Read in network-config json file and parse out values to return from it.
    """
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

        # bootnodes data
        bootnodes = data["bootnodes"]
        bootnodesProtocol = bootnodes["protocol"]
        bootnodesCount = bootnodes["count"]
        bootnodesHosts = bootnodes["hosts"]
        bootnodesStartPort = bootnodes["startPort"]
        bootnodesHostCount = len(bootnodesHosts)


    except KeyError as inst:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ("KeyError: " + str(inst) + " was invalid in file: " + str(fname) + " at line: " + str(exc_tb.tb_lineno) )
        print ("Please Try again...")
        sys.exit(3)
    # a 'dict' to hold how many clients (bootnodess) per host
    bootnodesHostAllocation = {}
    # assign evenly divisible number of clients
    for x in bootnodesHosts:
        bootnodesHostAllocation[x] = bootnodesCount / bootnodesHostCount
    # determine non-evenly divisible (modulus/remainder) number of clients
    remainderBootnodesClients = bootnodesCount % len(bootnodesHosts)
    # add remainder of clients to the appropriate number of hosts.
    for i in range(0,remainderBootnodesClients):
        key = bootnodesHostAllocation.keys()[i]
        bootnodesHostAllocation[key] = bootnodesHostAllocation[key] + 1
    # return values
    return configurationName , configurationVersion, bootnodesHostAllocation, bootnodesStartPort



##############################################################################
# Bootnode client Methods
##############################################################################

def createBootnodeKeys(jsonFile, outFile='', verbose=False,overrideCommand=None):
    """ create all bootnode keys
    """
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort = getJsonValues(jsonFile,verbose)
    verboseResults = ""
    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort
    verboseResults = "bootnode port start = " + str(currentProsumerRpcPort)
    newClients = [] #{ "bootnodes": []}
    # Loop through each Host to make their fab command. 
    for host in prosumerHostAllocation:
        clientsThisHost = []
        currentProsumerRpcPort += int(prosumerHostAllocation[host])
        # fab function to call, note ':' before first paramater, and ',' before all following paramaters
        command = "createBootnodes"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",datadir=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/bootnodes/"
        command += ",startPort=" + str(currentProsumerRpcPort)
        command += ",verbose=" + str(verbose)
        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        if overrideCommand == None:
            results = check_output(["fab", "-H", host, command ])
        else:
            results = check_output(["fab", "-H", host, overrideCommand])
        verboseResults += "\nresults: " + str(results)

        lines = results.split('\n')
        for line in lines:
            if len(line) == 135:
                clientsThisHost.insert(0,"enode://" + line[7:135] + "@" + str(host) + ":" + str(int(line[0:6])))
                currentProsumerRpcPort += 1
        verboseResults += "\nBootnodes this host:\n"
        for x in clientsThisHost:
            verboseResults += str(x) + "\n"
            newClients.insert(0, x)
    if outFile <> '':
        with open(str(outFile), 'w') as outfile:
            json.dump(newClients, outfile, indent=4, sort_keys=False)
        print "Newly Created bootnode JSON File output to: " + str(outFile)
    if verbose:
        print "\nCreated the following New bootnodes on the network.:\n"
        print verboseResults
    print "Created bootnodes on each Host"
    return newClients



def startBootnodes(jsonFile,verbose=False):
# start all bootnodes
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort = getJsonValues(jsonFile,verbose)
    verboseResults = ""
    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort
    verboseResults = "prosumer port start = " + str(currentProsumerRpcPort)
    # Loop through each Host to make their fab command.
    for host in prosumerHostAllocation:
        clientsThisHost = []
        currentProsumerRpcPort += prosumerHostAllocation[host]
        # fab function to call, note ':' before first paramater, and ',' before all following paramaters
        command = "startBootnodes"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",datadir=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/bootnodes/"
        command += ",startPort=" + str(clientStartPort)
        command += ",verbose=" + str(verbose)
        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        results = check_output(["fab", "-H", host, command ])
        verboseResults += "\nresults: " + str(results)
    if verbose:
        print "\nStarted the following New accounts on the network.:\n"
        print verboseResults
    print "Started Bootnodes on each Host"


def stopBootnodes(jsonFile,verbose=False,overrideCommand=None):
    """ Stop all bootnodes
    """
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort = getJsonValues(jsonFile,verbose)
    verboseResults = ""
    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort
    verboseResults = "prosumer port start = " + str(currentProsumerRpcPort)
    newClients = { "clients": []}
    # Loop through each Host to make their fab command.
    for host in prosumerHostAllocation:
        clientsThisHost = []
        currentProsumerRpcPort += prosumerHostAllocation[host]
        # fab function to call, note ':' before first paramater, and ',' before all following paramaters
        command = "stopBootnodes"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",startPort=" + str(clientStartPort)
        command += ",verbose=" + str(verbose)
        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        if overrideCommand == None:
            results = check_output(["fab", "-H", host, command ])
        else:
            results = check_output(["fab", "-H", host, overrideCommand ])
        verboseResults += "\nresults: " + str(results)
    if verbose:
        print "ch Host"
        print verboseResults
    print "Stopped bootnode blockchain clients on each Host"



def deleteBootnodes(jsonFile,verbose=False):
    """ Delete all bootnodes's data
    """
    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort = getJsonValues(jsonFile,verbose)
    verboseResults = ""
    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort
    # Loop through each Host to make their fab command.
    for host in prosumerHostAllocation:
        clientsThisHost = []
        currentProsumerRpcPort += prosumerHostAllocation[host]
        # fab function to call, note ':' before first paramater, and ',' before all following paramaters
        command = "deleteClients"
        command += ":numberOfClients=" + str(prosumerHostAllocation[host])
        command += ",datadir=" + "./ethereum/" + stringcase.snakecase(str(configurationName) + '_' + str(configurationVersion) ) + "/bootnodes/"
        command += ",verbose=" + str(verbose)
        verboseResults += "\ncommand: " + str(command)
        # call 'fab' with the correct host and parameters.
        results = check_output(["fab", "-H", host, command ])
        verboseResults += "\nresults: " + str(results)
    if verbose:
        print "\nVerbose Results for delting all bootnode data.:\n"
        print verboseResults
    else:
        print "Deleted bootnodes' data on each Host"



def distributeStaticNodesJson(file,nodes,verbose=False):

    configurationName , configurationVersion, prosumerHostAllocation, clientStartPort = getJsonValues(file,verbose)

    verboseResults = ""
    # make variable to hold current Port to use for clients
    currentProsumerRpcPort = clientStartPort
    verboseResults = "prosumer port start = " + str(currentProsumerRpcPort)

    print "HERE"

