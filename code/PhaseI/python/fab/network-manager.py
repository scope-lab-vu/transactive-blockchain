#!/usr/bin/python

##############################################################################
#
# CLI tool to manage Ethereum Test Network.
#
#   This class handles CLI parsing and distrutes workload to submodules.
#
#	Manages:
#		Clients
#		Blockchains
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
import sys

# import submodule methods.

# import single method
#from config.network import readFile
# import all methods
#from config.network import *

# import whole submodule, requires full namespace to access methods/variables.
import config.network
import clients.logic
import bootnodes.logic
import blockchains.logic
import miners.logic

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
def clientsGroup():
# simple method to 'group' 'Clients' commands together
    pass

@clientsGroup.command(name='create',
                 help='create all clients based of config file.')
@click.option('--file',
              default='./network-config.json',
			  help='Network Configuration JSON file location.')
@click.option('--type',
              default='all',
			  help='Type of clients to create: [ prosumers, dso, all(default) ]')
def clientsCreate(file,type='all'):
# Create all new clients based off config JSON file.
    # switch on what type
    if str(type) == 'all':
        clients.logic.createProsumerClients(file)
        clients.logic.createDsoClients(file)
        return
    if str(type) == 'prosumers':
        clients.logic.createProsumerClients(file)
        return
    if str(type) == 'dso':
        clients.logic.createDsoClients(file)
        return
    # if option was given and isn't valid, then error & quit.
    print 'ERROR: provided non-valid \'type\' valid: [ prosumers, dso, all ]'
    print 'Program exiting.'
    sys.exit()

@clientsGroup.command(name='start',
                 help='start all clients based of config file.')
@click.option('--file',
              default='./network-config.json',
			  help='Network Configuration JSON file location.')
@click.option('--type',
              default='all',
			  help='Type of clients to create: [ prosumers, dso, all(default) ]')
def clientsStart(file,type='all'):
# Create all new clients based off config JSON file.
    # switch on what type
    if str(type) == 'all':
        clients.logic.startProsumerClients(file)
        clients.logic.startDsoClients(file)
        return
    if str(type) == 'prosumers':
        clients.logic.startProsumerClients(file)
        return
    if str(type) == 'dso':
        clients.logic.startDsoClients(file)
        return
    # if option was given and isn't valid, then error & quit.
    print 'ERROR: provided non-valid \'type\' valid: [ prosumers, dso, all ]'
    print 'Program exiting.'
    sys.exit()

@clientsGroup.command(name='stop',
                 help='stop all clients based of config file.')
@click.option('--file',
              default='./network-config.json',
			  help='Network Configuration JSON file location.')
@click.option('--type',
              default='all',
			  help='Type of clients to create: [ prosumers, dso, all(default) ]')
def clientsStop(file,type='all'):
# Create all new clients based off config JSON file.
    # switch on what type
    if str(type) == 'all':
        clients.logic.stopProsumerClients(file)
        clients.logic.stopDsoClients(file)
        return
    if str(type) == 'prosumers':
        clients.logic.stopProsumerClients(file)
        return
    if str(type) == 'dso':
        clients.logic.stopDsoClients(file)
        return
    # if option was given and isn't valid, then error & quit.
    print 'ERROR: provided non-valid \'type\' valid: [ prosumers, dso, all ]'
    print 'Program exiting.'
    sys.exit()

@clientsGroup.command(name='delete',
                 help='delete all clients.')
@click.option('--file',
              default='./network-config.json',
			  help='Network Configuration JSON file location.')
@click.option('--type',
              default='all',
			  help='Type of clients to create: [ prosumers, dso, all(default) ]')
def clientsDelete(file,type='all'):
# Delete all clients.
    # switch on what type
    if str(type) == 'all':
        clients.logic.deleteProsumerClients(file)
        clients.logic.deleteDsoClients(file)
        return
    if str(type) == 'prosumers':
        clients.logic.deleteProsumerClients(file)
        return
    if str(type) == 'dso':
        clients.logic.deleteDsoClients(file)
        return
    # if option was given and isn't valid, then error & quit.
    print 'ERROR: provided non-valid \'type\' valid: [ prosumers, dso, all ]'
    print 'Program exiting.'
    sys.exit()

##############################################################################
# 'Blockchains' group of commands
##############################################################################

@cli.group(name='blockchains',
           help='Manage blockchain/genesis block')
def blockchainGroup():
# simple method to 'group' 'Blockchain' commands together
    pass


@blockchainGroup.command(name='make',
                    help='Make Genesis Block config file.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def blockchainMake(file,verbose):
# Create new Genesis block.
    blockchains.logic.makeGenesisBlockchainConfigFile(file,verbose)



@blockchainGroup.command(name='create',
                    help='Create a new Genesis Block')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--datadir',
              default='./ethereum/blockchian/',
              help='data directory to create blockchain at.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def blockchainCreate(file,datadir,verbose):
# Create new Genesis block.
    blockchains.logic.createGenesisBlockchain(file,datadir,verbose)


@blockchainGroup.command(name='delete',
                    help='Delete the blockchain from all clients')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def blockchainDelete(file):
# Delete the blockchain from all clients.
    blockchains.logic.deleteBlockchains(file)

@blockchainGroup.command(name='distribute',
                    help='Distribute new Genesis Block to all peers.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def blockchainDistribute(file):
# Distribute the new Genesis block to all clients.
    blockchains.logic.distributeBlockchains(file)


##############################################################################
# 'bootnodes' group of commands
##############################################################################

@cli.group(name='bootnodes',
           help='Manage bootnodes')
def bootnodeGroup():
# simple method to 'group' 'bootnodes' commands together
    pass

@bootnodeGroup.command(name='create',
                   help='Create bootnodes.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def bootnodesCreate(file):
# Create new bootnodes.
    bootnodes.logic.createBootnodes(file)

@bootnodeGroup.command(name='start',
                   help='Start bootnodes.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def bootnodesStart(file):
# Create new bootnodes.
    bootnodes.logic.startBootnodes(file)

@bootnodeGroup.command(name='stop',
                   help='Stop bootnodes.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def bootnodesStop(file):
# Create new bootnodes.
    bootnodes.logic.stopBootnodes(file)

@bootnodeGroup.command(name='delete',
                   help='Delete all bootnodes.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def bootnodesDelete(file):
# Delete the bootnodes.
    bootnodes.logic.deleteBootnodes(file)

##############################################################################
# 'Miners' group of commands
##############################################################################

@cli.group(name='miners',
           help='Manage Miners')
def minerGroup():
# simple method to 'group' 'Miner' commands together
    pass

@minerGroup.command(name='create',
                help='Create new Miners')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def minersCreate(file):
# Create new Miners
    miners.logic.createMiners(file)

@minerGroup.command(name='start',
                help='Start Miners')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def minersStart(file):
# Create new Miners
    miners.logic.startMiners(file)

@minerGroup.command(name='stop',
                help='Stop Miners')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def minersStop(file):
# Create new Miners
    miners.logic.stopMiners(file)

@minerGroup.command(name='delete',
                help='Delete all Miners.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
def minersDelete(file):
# Delete all Miners.
    miners.logic.deleteMiners(file)

##############################################################################
# 'main' entrypoint of script
##############################################################################

if __name__ == '__main__':
# main method, calls CLI procesing.
    cli()
