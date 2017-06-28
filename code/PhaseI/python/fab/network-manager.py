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
# Notes:
#	-Auto-complete of commands is a feature when script is 'installed', but
#		is not available when ran as python script.
##############################################################################

##############################################################################
# imports
##############################################################################

import click

# import submodule methods.

# import single method
#from config.network import readFile
# import all methods
#from config.network import *

# import whole submodule, requires full namespace to access methods/variables.
import config.network



def readConfigFile():

	# read the config file
	config.network.readFile()

	# declare every key value as 'global' to all methods in this file.
	global prosumerCount
	global prosumerHosts
	global prosumerHostCount
	global minerHosts
	global minerHostCount
	global startProsumerRpcPort
	global prosumerHostAllocation

	# copy new values from the json file to global variables.
	prosumerCount = config.network.prosumerCount
	prosumerHosts = config.network.prosumerHosts
	prosumerHostCount = config.network.prosumerHosts
	minerHosts = config.network.minerHosts
	minerHostCount = config.network.minerHosts
	minerCount = config.network.minerCount
	startProsumerRpcPort = config.network.startProsumerRpcPort

##############################################################################
# start of methods.
##############################################################################

@click.group()
@click.version_option(version='0.1')
def cli():
# setup the overall CLI method.
	pass

##############################################################################
# 'Clients' group of commands
##############################################################################

@cli.group(name='clients', help='Manage clients')
def clients():
# simple method to 'group' 'Clients' commands together
	pass

@clients.command(name='create',
                 help='create all clients based of config file.')
@click.option('--file',
              default='./network-config.json',
			  help='Network Configuration JSON file location.')
def clientsCreate(file):
# Create all new clients based off config JSON file.
	readConfigFile()

#	print config.network.prosumerCount
	print prosumerCount
	print config.network.prosumerHostAllocation
	click.echo('' +file)

@clients.command(name='delete',
                 help='delete all clients.')
def clientsDelete():
# Delete all clients.
	readConfigFile()
	print prosumerCount
	click.echo('Deleted all Clients.')

##############################################################################
# 'Blockchain' group of commands
##############################################################################

@cli.group(name='blockchain',
           help='Manage blockchain/genesis block')
def blockchain():
# simple method to 'group' 'Blockchain' commands together
	pass

@blockchain.command(name='create',
                    help='Create a new Genesis Block')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def blockchainCreate(file):
# Create new Genesis block.
	click.echo('Creating new Genesis block from: ' +file)

@blockchain.command(name='delete',
                    help='Delete the blockchain from all clients')
def blockchainDelete():
# Delete the blockchain from all clients.
    click.echo('Created Clients')

@blockchain.command(name='distribute',
                    help='Distribute new Genesis Block to all peers.')
def blockchainDistribute():
# Distribute the new Genesis block to all clients.
    click.echo('Created Clients')

##############################################################################
# 'bootnodes' group of commands
##############################################################################

@cli.group(name='bootnodes',
           help='Manage bootnodes')
def bootnodes():
# simple method to 'group' 'bootnodes' commands together
    pass

@bootnodes.command(name='create',
                   help='Create bootnodes.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def bootnodesCreate(file):
# Create new bootnodes.
    click.echo('Creating new Genesis block from: ' + str(file))

@bootnodes.command(name='delete',
                   help='Delete all bootnodes.')
def bootnodesDelete():
# Delete the bootnodes.
    click.echo('Created Clients')

##############################################################################
# 'Miners' group of commands
##############################################################################

@cli.group(name='miners',
           help='Manage Miners')
def miners():
# simple method to 'group' 'Miner' commands together
    pass

@miners.command(name='create',
                help='Create new Miners')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def minersCreate(file):
# Create new Miners
    click.echo('Creating new Genesis block from: ' +file)

@miners.command(name='delete',
                help='Delete all Miners.')
def minersDelete():
# Delete all Miners.
    click.echo('Miners deleted.')

##############################################################################
# 'main' entrypoint of script
##############################################################################

if __name__ == '__main__':
# main method, calls CLI procesing.
    cli()
