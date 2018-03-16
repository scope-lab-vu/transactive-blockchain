########################################################################################
#
# Python Fabric 'fabfile' for connecting over SSH to control Ethereum's 'geth' Clients.
#
#   -This file contains all the SSH-related content for the 'Network-Manager' app.
#
#   -This file assumes you have an appropriate SSH key(s) installed in your [ ~/.ssh/ ]
#   directory, that you have the appropriate [ ~/.ssh/config ] file configured for each
#   host, and that each host is added to the [ ~/.ssh/known_hosts ] file.
#
#   -This file requires each host to have the following installed:
#       geth - blockchain cleint for ethereum.
#       dtach - simple program that emulates the detach feature of screen
#
#
# @Author Michael A. Walker
# @Date 2017-07-21
#
########################################################################################


########################################################################################
#
# Imports
#
########################################################################################

from fabric.api import env
from fabric.operations import run, put, local
from fabric.contrib.project import rsync_project
from fabric.api import settings, hide

from StringIO import StringIO
from random import *
import sys
import warnings
# ignore that an SSH dep. of Fabric will need Fabric to be upgraded in the future.
warnings.simplefilter(action='ignore', category=FutureWarning)
env.use_ssh_config = True


class FabricException(Exception):
    # error handling class for exceptions when processes return error (such as kill -9 <pid>)
    pass

def runCommand(command):
    """ Run an arbitrary command on a remote system.
    """
    run(command)

def mkdir(remotePath):
    """ make a remote directory
    """
    run('mkdir -p ' + remotePath)

def rmdir(remotePath):
    """ delete a remote directory
    """
    run('rm -rf ' + remotePath)

def runbg(cmd, processname='', stdout=None ,sockname="dtach"):
    """ run any process in the background, uses 'dtach' to allow processing even after Fab disconnects.
    """
    # mktemp uses name of process and XX* pattern to determin name of temp file, which means:
    # same pattern + same process name = same name, which is obviously bad in this case,
    # so we insert a random number ourselves beforehand for each new process.
    randValue = '`mktemp -u /tmp/' + str(int(randint(1,9999999))).rjust(7,'0')
    if (processname <> ''):
        cmd = 'bash -c \'exec -a ' + str(processname) + ' '  + str(cmd) + '\''
    if stdout is None:
        return run('dtach -n ' + randValue + '`.%sXXXXX.dtach` %s'  % (sockname,cmd))
    else:
        return run('dtach -n ' + randValue + '.%sXXXXX.dtach` %s'  % (sockname,cmd),stdout)


def killProcess(processName):
#kill process by name.
    run("ps -eF | grep " + + " | awk {'print $2'} | xargs kill -9")
    run('pkill -f ' + processName)



def copyFile(file, remotePath, clients, verbose=False):
    fh = StringIO();
    result=''
    verboseResults = ''

    for i in range(1,int(clients)+1):
        path = str(remotePath) + '/' + str(i).rjust(5,'0')
        run ('mkdir -p ' + str(path))
        results = put(file,path)
        verboseResults += str(results)
    if verbose:
        print "*** Verbose Output: ***\n" + verboseResults
    else:
        print 'copied file ' + file + ' to ' + path



def createGenesisBlockchain(file="./genesis-data.json",
                            datadir="./ethereum/blockchain",
                            verbose=False):
    fh = StringIO();
    result=''
    verboseResults = ''
    mkdirCommand = "mkdir -p " + datadir
    results = run (mkdirCommand, stdout=fh)
    verboseResults += results + '\n'
    gethCommand = "geth  --datadir " + str(datadir) + " init " + str(file)
    results = run (gethCommand, stdout=fh)
    verboseResults += results + '\n'
    if verbose:
        print "*** Verbose Output: ***\n" + str(verboseResults)
    else:
        print "Genesis Block created in directory: " + str(datadir)



def copyLocalDir(localPath,remotePath,subDir='',numberOfClients=1,verbose=False):
    for i in range(1,int(numberOfClients)+1):
        path = str(remotePath) + "/"  + str(i).rjust(5,'0') + '/' + subDir
        rsync_project(local_dir=localPath, remote_dir=path)
    # no 'verbose' output for now.
    print "Directory " + localPath + " copied to " + remotePath




def createAccounts(numberOfClients,datadir,verbose=False):
    """ Create Ethereum Accounts, given data-directory & number of clients to create.
    """
    fh = StringIO();
    result=''
    verboseResults = ''
    for i in range(1,int(numberOfClients)+1):
        accountCommand = "geth account new --password ./password.txt --datadir " + str(datadir) + "/"  + str(i).rjust(5,'0')
        results = run(accountCommand, stdout=fh)
        verboseResults += results + '\n'
    if verbose:
        print "*** Verbose aOutput: ***\n" + verboseResults
    else:
        print numberOfClients + " new Accounts created."

#import socket

def startClients(numberOfClients,
                datadir,
                startPort,
                network=15,
                verbose='False',
                isMiner='False',
                clientType='prosumer',
                mineThreads=1,
                etherbase='0x0000000000000000000000000000000000000000',
                overrideCommand='',
                netrestrict='127.0.0.0/16'):
    fh = StringIO();
    result=''
    verboseResults = ''
#    rpcIP = socket.gethostbyname('www.google.com')

    port = int(startPort)
    for i in range(1,int(numberOfClients)+1):
        fullDataDir = str(datadir) + "/" + str(i).rjust(5,'0')
        command = "geth --password ./password.txt"
        command += " --datadir " + str(datadir) + "/"  + str(i).rjust(5,'0')
        command += " --networkid " + str(network)
        # command += " --ws --wsport " + str(port)
        command += " --port " + str(int(port)+int(i)-1000)
        command += " --unlock 0 "
        command += " --rpc --rpcaddr " + str(env.host_string) + " --rpcport  " + str(port)
        command += " --rpcapi eth,web3,admin,miner,net,db "
        # http://doc.m0n0.ch/quickstartpc/intro-CIDR.html How to format netrestrict value
        command += " --netrestrict " + str(netrestrict)
        command += " --nodiscover "

        name = clientType
        if isMiner == 'True':
            command += " --mine --minerthreads=" + str(mineThreads)  + " --etherbase=" + str(etherbase)
        name += str(i).rjust(5,'0')

        command += ">" + fullDataDir + "/output.log" + " 2>&1"

        # run built command or 'overrideCommand'
        if overrideCommand <> '':
            results = runbg(overrideCommand, name, stdout=fh,sockname=name)
        else:
            results = runbg(command, name, stdout=fh,sockname=name)

        verboseResults += results + '\n'
        port += int(1)
    if verbose:
        print "*** Verbose Output: ***\n" + verboseResults
    else:
        outMessage = ""
        if isMiner:
            outMessage = "Miners "
        else:
            outMessage = "Clients "
        print outMessage + "Started."

def stopClients(numberOfClients,
                network=15,
                clientType='prosumer',
                verbose=False,
                isMiner=False):
    fh = StringIO();
    result=''
    verboseResults = ''

    for i in range(1,int(numberOfClients)+1):
        with settings(warn_only=True):
            command = clientType
            # 'with' here hides output, warnings, etc.
#        print command
            with hide('output','running','warnings','aborts'), settings(warn_only=True):
                results = run("kill -9 `ps aux | egrep " + command + "[0-9]{5} | awk '{print $2}'`")
#            verboseResults += results + '\n'
    if verbose == True:
        print "*** Verbose Output: ***\n" + verboseResults
    else:
        print clientType + " clients stopped."


def deleteClients(numberOfClients,
                datadir,
                clientType='prosumer',
                verbose=False):
    fh = StringIO();
    result=''
    verboseResults = ''
    for i in range(1,int(1)+1):
        path= str(datadir)
        results = run('rm -rf ' + path,stdout=fh)
        verboseResults += results + '\n'
    if verbose:
        print "*** Verbose Output: ***\n" + verboseResults
    else:
        print clientType + " deleted."
    local('uname -n')


##########################################################
#
# bootnodes
#
##########################################################

def createBootnodeKey(keyPathName, verbose=False):
    verboseResults = ""
    results = run('mkdir -p ' + str(keyPathName))
    verboseResults += str(results)
    results = run('bootnode -genkey ' + str(keyPathName)+ 'key')
    verboseResults += str(results)
    results = run('bootnode -nodekey ' + str(keyPathName) + 'key' + ' --writeaddress')
    verboseResults += str(results)
    if verbose:
        print "Created bootnode key, verbose:\n" + verboseResults
    else:
        print "Created bootnode key."


def createBootnodes(numberOfClients,datadir,startPort=0,networkName='',verbose=False):
    fh = StringIO();
    result=''
    verboseResults = ''
    for i in range(1,int(numberOfClients)+1):
        path= str(datadir) + "/"  + str(i).rjust(5,'0') + "/"
        run('mkdir -p ' + path)
        run('bootnode -genkey ' + str(path) + "key" ,stdout=fh)
        results = run('bootnode -nodekey ' + str(path) + "key"  + ' --writeaddress', stdout=fh)
        verboseResults += results + '\n'
        verboseResults +=  str(i+int(startPort)-2).rjust(6,'0') + "," + results + '\n'
    if verbose:
        print "*** Verbose Output: ***\n" + verboseResults
    else:
        print "Bootnodes created."
    return verboseResults


def startBootnodes(numberOfClients,datadir,startPort,networkName='',verbose=False):
    fh = StringIO();
    result=''
    verboseResults = ''
    currentPort = int(startPort)
    allocation = { "bootnodes" : []  }

    for i in range(1,int(numberOfClients)+1):
        path= str(datadir) + "/"  + str(i).rjust(5,'0') + "/"
        command = 'bootnode -nodekey ' + str(path) + "key" + ' -addr \":' + str(currentPort)  + '\"'
        results = runbg(command, 'bootnode' + str(i).rjust(5,'0') , stdout=fh)

        currentPort += i
        verboseResults += results + '\n'
    if verbose:
        print "*** Verbose Output: ***\n" + verboseResults
    else:
        print "Bootnodes created."


def stopBootnodes(numberOfClients,startPort,verbose=False):
    fh = StringIO();
    result=''
    verboseResults = ''
    currentPort = int(startPort)

    for i in range(1,int(numberOfClients)+1):
        with settings(
                hide('warnings', 'running', 'stdout', 'stderr'),
                warn_only=True
            ):
            results = run('ps -eF | grep nodekey.*' + str(currentPort)  + '  | awk {\'print $2\'} | xargs kill -9',stdout=fh,shell=False)
        currentPort += i
        verboseResults += results + '\n'
    if verbose:
        print "*** Verbose Output: ***\n" + verboseResults
    else:
        print "Bootnodes created."


def stopBootnode(processName):
    run('ps -eF | grep nodekey.*' + processName  + '  | awk {\'print $2\'} | xargs kill -9')

def deleteBootnodeKeyFile(keyPathName):
    run('rm ' + keyPathName)
