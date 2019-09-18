#!/usr/bin/python

##############################################################################
#
# CLI tool to manage Distributed Ledger Test Networks.
#
#   This class handles CLI parsing and distrutes workload to submodules.
#
#   Current iteration is focused on Ethereum, but is generalized so that
#   Adoption of other distributed ledger frameworks, such as Hyperledger
#   should be easy to adopt/manage.
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
#		is not available when ran as purely CLI script.
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
@click.option('--out',
              default='',
			  help='JSON output file of newly created Accounts, If empty, don\'t save a file.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def clientsCreate(file,verbose,type='all',out=''):
# Create all new clients based off config JSON file.
    # switch on what type
    if str(type) == 'all':
        clients.logic.createClients(file,outFile=out,verbose=verbose,type="prosumer")
        clients.logic.createClients(file,outFile=out,verbose=verbose,type="dso")
        return
    if str(type) == 'prosumers':
        clients.logic.createClients(file,outFile=out,verbose=verbose,type="prosumer")
        return
    if str(type) == 'dso':
        clients.logic.createClients(file,outFile=out,verbose=verbose,type="dso")
        return
    # if option was given and isn't valid, then error & quit.
    print 'ERROR: provided non-valid \'type\' valid: [ prosumers, dso, all ]'
    print 'Program exiting.'
    sys.exit(2)


@clientsGroup.command(name='start',
                 help='start all clients based of config file.')
@click.option('--file',
              default='./network-config.json',
			  help='Network Configuration JSON file location.')
@click.option('--type',
              default='all',
			  help='Type of clients to create: [ prosumers, dso, all(default) ]')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def clientsStart(file,type='all',verbose=False):
# Create all new clients based off config JSON file.
    # switch on what type
    if str(type) == 'all':
        clients.logic.startProsumerClients(file,verbose,type="prosumer")
        clients.logic.startProsumerClients(file,verbose,type="dso")
        return
    if str(type) == 'prosumers':
        clients.logic.startProsumerClients(file,verbose,type="prosumer")
        return
    if str(type) == 'dso':
        clients.logic.startProsumerClients(file,verbose,type="dso")
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
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def clientsStop(file,type='all',verbose=False):
# Create all new clients based off config JSON file.
    # switch on what type
    if str(type) == 'all':
        clients.logic.stopProsumerClients(file,verbose,type="prosumer")
        clients.logic.stopProsumerClients(file,verbose,type="dso")
        return
    if str(type) == 'prosumers':
        clients.logic.stopProsumerClients(file,verbose,type="prosumer")
        return
    if str(type) == 'dso':
        clients.logic.stopProsumerClients(file,verbose,type="dso")
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
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def clientsDelete(file,type='all',verbose=False):
# Delete all clients.
    # switch on what type
    if str(type) == 'all':
        clients.logic.deleteProsumerClients(file,verbose,type="prosumer")
        clients.logic.deleteProsumerClients(file,verbose,type="dso")
        return
    if str(type) == 'prosumers':
        clients.logic.deleteProsumerClients(file,verbose,type="prosumer")
        return
    if str(type) == 'dso':
        clients.logic.deleteProsumerClients(file,verbose,type="dso")
        return
    # if option was given and isn't valid, then error & quit.
    print 'ERROR: provided non-valid \'type\' valid: [ prosumers, dso, all ]'
    print 'Program exiting.'
    sys.exit()


@clientsGroup.command(name='distribute',
                 help='distribute a directory to each client.')
@click.option('--file',
              default='./network-config.json',
			  help='Network Configuration JSON file location.')
@click.option('--local',
			  help='File or Directory to copy to each client (Dir with trailing \'/\' will copy contents, without will copy directory itself ).')
@click.option('--subdir',
              default='',
			  help='Subdirectory of each Client(if any) to copy the directory to. (Optional)')
@click.option('--type',
              default='all',
			  help='Type of clients to create: [ prosumers, dso, all(default) ]')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def clientsDistributeFiles(file,local,subdir,type='all',verbose=False):
# Delete all clients.
    # switch on what type
    if str(type) == 'all':
        clients.logic.distributeFilesToClients(jsonFile=file, inputDir=local, clientType='prosumer', subDirectory=subdir, verbose=False)
        clients.logic.distributeFilesToClients(jsonFile=file, inputDir=local, clientType='dso', subDirectory=subdir, verbose=False)
        return
    if str(type) == 'prosumers':
        clients.logic.distributeFilesToClients(jsonFile=file, inputDir=local, clientType='prosumer', subDirectory=subdir, verbose=False)
        clients.logic.distributeFilesToClients(jsonFile=file, inputDir=local, clientType='dso', subDirectory=subdir, verbose=False)
        return
    if str(type) == 'dso':
        clients.logic.distributeFilesToClients(jsonFile=file, inputDir=local, clientType='dso', subDirectory=subdir, verbose=False)
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
@click.option('--clients',
              default='',
              help='JSON file listing clients that are freshly created.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def blockchainMake(file,verbose,clients):
# Make a new Genesis block config file.
    blockchains.logic.makeGenesisBlockchainConfigFile(file,clients,verbose)


@blockchainGroup.command(name='create',
                    help='Create a new Genesis Block')
@click.option('--file',
              default='./genesis-data.json',
              help='Genesis Data formatted JSON file location.')
@click.option('--datadir',
              default='./ethereum/blockchian/',
              help='data directory to create blockchain at.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def blockchainCreate(file,datadir,verbose=False):
# Create new Genesis block.
    blockchains.logic.createEthereumBlockchain(file,datadir,verbose)


@blockchainGroup.command(name='distribute',
                    help='Distribute new Genesis Block to all clients.')
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
def blockchainDistribute(file,datadir,verbose):
# Distribute the new Genesis block to all clients.
    blockchains.logic.distributeBlockchain(jsonFile=file, blockchainPath=datadir, verbose=False)

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
@click.option('--out',
              default='static-nodes.json',
			  help='JSON output file of newly created bootnodes and their enode addressses.')
@click.option('--file',
              default='./network-config.json',
               help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def bootnodesCreate(file,out='static-nodes.json',verbose=False):
# Create new bootnodes.
    bootnodes.logic.createBootnodeKeys(file,out,verbose)

# bootnodes distribute
@bootnodeGroup.command(name='distribute',
                   help='Create bootnodes.')
@click.option('--file',
              default='',
              help='Network Configuration JSON file location.')
@click.option('--nodes',
              default='created-bootnodes.json',
              help='JSON output file of newly created bootnodes to inform every client of.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def bootnodesDistribute(file,nodes='created-bootnodes.json',verbose=False):
# Create new bootnodes.
    bootnodes.logic.distributeStaticNodesJson(file,nodes,verbose=False)

# bootnodes start
@bootnodeGroup.command(name='start',
                   help='Start bootnodes.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def bootnodesStart(file,verbose=False):
# Create new bootnodes.
    bootnodes.logic.startBootnodes(file,verbose)

# bootnodes stop
@bootnodeGroup.command(name='stop',
                   help='Stop bootnodes.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def bootnodesStop(file,verbose=False):
# Create new bootnodes.
    bootnodes.logic.stopBootnodes(file,verbose)

# bootnodes delete
@bootnodeGroup.command(name='delete',
                   help='Delete all bootnodes.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def bootnodesDelete(file,verbose):
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

# miners create
@minerGroup.command(name='create',
                help='Create new Miners')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--out',
              default='',
			  help='JSON output file of newly created Accounts, If empty, don\'t save a file.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def minersCreate(file,out='',verbose=False,clientType="miners"):
# Create new Miners
    miners.logic.createMinerClients(file,clientType,out,verbose)

# miners start
@minerGroup.command(name='start',
                help='Start Miners')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def minersStart(file,verbose=False):
# Create new Miners
    miners.logic.startMinerClients(file,verbose)

# miners stop
@minerGroup.command(name='stop',
                help='Stop Miners')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def minersStop(file,verbose=False):
# Create new Miners
    miners.logic.stopMinerClients(file,verbose)

# miners delete
@minerGroup.command(name='delete',
                help='Delete all Miners.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def minersDelete(file,verbose=False):
# Delete all Miners.
    miners.logic.deleteMinerClients(file,verbose)



@minerGroup.command(name='distribute',
                 help='distribute a directory to each client.')
@click.option('--file',
              default='./network-config.json',
			  help='Network Configuration JSON file location.')
@click.option('--local',
			  help='File or Directory to copy to each client (Dir with trailing \'/\' will copy contents, without will copy directory itself ).')
@click.option('--subdir',
              default='',
			  help='Subdirectory of each Client(if any) to copy the directory to. (Optional)')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def minerssDistributeFiles(file,local,subdir,verbose):
# Distribute file(s) to each miner.
    miners.logic.distributeFilesToClients(jsonFile=file, inputDir=local, clientType='miners', subDirectory=subdir, verbose=False)


@minerGroup.command(name='connect',
                 help='connect each client(dso/prosumer) to each miner.')
@click.option('--file',
              default='./network-config.json',
			  help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
def minersConnect(file,verbose=False):
# Distribute file(s) to each miner.
    miners.logic.connectMinerClients(jsonFile=file, verbose=verbose)



@cli.group(name='network',
           help='Manage an entire network at once.')
def networkGroup():
# simple method to 'group' 'bootnodes' commands together
    pass

# network create
@networkGroup.command(name='create',
                   help='Create a network from a config file.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
@click.pass_context
def networkCreate(ctx, file, verbose=False):
# Create new network.
#    ctx.forward(clientsStop)
#    ctx.invoke(clientsStop, file=file, verbose=True)
    ctx.invoke(bootnodesCreate, file=file, verbose=verbose)
    ctx.invoke(minersCreate, file=file, verbose=verbose)
    ctx.invoke(clientsCreate, file=file, verbose=verbose,type='all')

# network start
@networkGroup.command(name='start',
                   help='Start an entire Network.')
@click.option('--file',
              default='',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
@click.pass_context
def networkStop(ctx, file, verbose=False):
    ctx.invoke(bootnodesStart, file=file, verbose=verbose)
    ctx.invoke(minersStart, file=file, verbose=verbose)
    ctx.invoke(clientsStart, file=file, verbose=verbose,type='all')

# network stop
@networkGroup.command(name='stop',
                   help='Stop an entire Network.')
@click.option('--file',
              default='',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
@click.pass_context
def networkStop(ctx, file, verbose=False):
    ctx.invoke(clientsStop, file=file, verbose=verbose,type='all')
    ctx.invoke(minersStop, file=file, verbose=verbose)
    ctx.invoke(bootnodesStop, file=file, verbose=verbose)


# network delete
@networkGroup.command(name='delete',
                help='Delete everything related to a network.')
@click.option('--file',
              default='./network-config.json',
              help='Network Configuration JSON file location.')
@click.option('--verbose',
              is_flag=True,
              default=False,
              help='Verbose Output.')
@click.pass_context
def networkDelete(ctx, file, verbose=False):
# Delete all Clients, Miners, & Bootnodes.
# Todo: delete folder with network name/ver. # too.
    ctx.forward(clientsDelete)
    ctx.forward(minersDelete)
    ctx.forward(bootnodesDelete)




##############################################################################
# 'main' entrypoint of script
##############################################################################

if __name__ == '__main__':
# main method, calls CLI procesing.
    cli()
