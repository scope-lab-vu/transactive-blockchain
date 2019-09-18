#!/usr/bin/python

##############################################################################
#
# Configure how to properly setup a network topology for testing blockchain
#    This reads in custom schema JSON and calls associated 'fab' file.
#
# NOTE: This file is not currently used. processing is localized in each file.
#
# @Author Michael A. Walker
# @Date   2017-06-21
#
##############################################################################

# imports
import json
from subprocess import call,check_output

def readFile(configFile='/home/ubuntu/python/fab/network-config.json'):
# read config file in and parse it.

	# read in the configuration JSON file
	with open(configFile) as data_file:
		data = json.load(data_file)

	# get the values from the JSON file
	global prosumerCount
	global prosumerHosts
	global prosumerHostCount
	global minerHosts
	global minerHostCount
	global startProsumerRpcPort
	global prosumerHostAllocation
	global minerCount

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

#	print prosumerHostAllocation
