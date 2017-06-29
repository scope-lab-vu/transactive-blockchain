#!/usr/bin/python

##############################################################################
#
# Configure how to properly setup a network topology for testing blockchain
#    This reads in custom schema JSON and calls associated 'fab' file.
#
# @Author Michael A. Walker
# @Date   2017-06-21
#
##############################################################################

# imports
import json
from subprocess import call,check_output

#class setup-network:

# read in the configuration JSON file
with open('network-config.json') as data_file:
	data = json.load(data_file)

# get the values from the JSON file
prosumerCount = data["prosumerCount"]
prosumerHosts = data["prosumerHosts"]
prosumerHostCount = len(prosumerHosts)
minerHosts = data["minerHosts"]
minerHostCount = len(minerHosts)
minerCount = data["minerCount"]
startProsumerRpcPort = data["startProsumerRpcPort="]


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

# make variable to hold current Port to use for clients
currentProsumerRpcPort = startProsumerRpcPort


newClients = ""
# Loop through each Host to make their fab command.
# this creates the new acounts for each host
for host in prosumerHostAllocation:

	currentProsumerRpcPort += prosumerHostAllocation[host]

	# start the command to setup the host, this is the fab function to call
	# note ':' before first paramater, and ',' before all following paramaters
    # Sample command:
    # fab -H eth4 createAccounts:numberOfClients=3,datadir="./.eth"
	command = "createAccounts"
	command += ":numberOfClients=" + str(prosumerHostAllocation[host])
	#command += ",datadir=" + "./.ethereum"

	# call 'fab' with the correct host and parameters.
	results = check_output(["fab", "-H", host, command ])
	newClients = newClients + str(results)

lines = newClients.split('\n')
result = ""
for line in lines:
	if line.startswith("Address"):
		result = result + line[10:50] + '\n'

print "newClients = " + result

# Loop through each Host to make their fab command.
for host in prosumerHostAllocation:

	currentProsumerRpcPort += prosumerHostAllocation[host]

	# start the command to setup the host, this is the fab function to call
	# note ':' before first paramater, and ',' before all following paramaters
	command = "startClients"
	command += ":prosumerCount=" + str(prosumerHostAllocation[host])
	command += ",startProsumerRpcPort=" + str(currentProsumerRpcPort)

	# call 'fab' with the correct host and parameters.
	results = check_output(["fab", "-H", host, command ])

print "Started Clients on each Host"


