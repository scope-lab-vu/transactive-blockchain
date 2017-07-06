#from fabric.api import run
from fabric.api import env

from fabric.operations import run, put
from fabric.contrib.project import rsync_project
from StringIO import StringIO
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

env.use_ssh_config = True

def mkdir(remotePath):
# make a remote directory
    run('mkdir -p ' + remotePath)

def rmdir(remotePath):
# delete a remote directory
    run('rm -rf ' + remotePath)

def rmMiners(remotePath="./ethereum/miners/"):
# delete a remote directory
    run('rm -rf ' + remotePath)

def rmClients(remotePath="./ethereum/clients/"):
# delete a remote directory
    run('rm -rf ' + remotePath)

def rmBootnodes(remotePath="./ethereum/bootnodes/"):
# delete a remote directory
    run('rm -rf ' + remotePath)



def startProcess(command,commandName,background=False):
#start
    runCommand = "bash -c \"exec -a " + commandName  + " " + command
    # add & if background is True
    if background:
        runCommand += " &"
    runCommand += " \""
    # run command
    run(runCommand)

def killProcess(processName):
#kill process by name.
    run('pkill -f ' + processName)


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
        print "** Verbose Output: **"
        print verboseResults

def copyLocalDir(localPath,remotePath):
    # make sure the directory is there!
    run('mkdir -p ' + remotePath)

    # our local 'testdirectory' - it may contain files or subdirectories ...
    # put(localPath, remotePath)

    rsync_project(local_dir=localPath, remote_dir=remotePath)
    #put('~/ethereum/', remotePath)

#def startClients():
# Start all clients on the host.

# This starts the appropriate number of clients on a host
# ran by 'fab -H <hostname> startClients:<param>=<value>'
#def startClients(dsoCount=0,prosumerCount=1,startProsumerRpcPort=8545,minerCount=0,commandName="uniqueName"):

#    command = "echo command "
#    command += " --prosumerCount=" + str(prosumerCount)
#    command += " --dsoCount=" + str(dsoCount)
#    command += " --prosumerRpcStartPort=" + str(startProsumerRpcPort)
#    command += " --minerCount=" + str(minerCount)
#    startWithName(command,commandName)

def createAccount(numberOfClients,datadir,networkName='',verbose=False):
    fh = StringIO();
    result=''
    verboseResults = ''
    for i in range(1,int(numberOfClients)+1):
        accountCommand = "geth account new --password ./password.txt --datadir " + str(datadir) + str(networkName)  + str(i).rjust(5,'0')
        results = run(accountCommand, stdout=fh)
        verboseResults += results + '\n'
        lines = results.split('\n')
        for line in lines:
            if line.startswith("Address"):
                result = result + line[10:50] + '\n'
    print result
    if verbose:
        print "*** Verbose Output: ***"
        print verboseResults


def createClients(numberOfClients,datadir="./ethereum/clients/",verbose=False):
# method to create clients. Has default localtio for miners
    createAccount(numberOfClients,datadir,verbose)
#    createEthereumClients


def createMiners(numberOfClients,datadir="./ethereum/miners/",verbose=False):
# method to create miners. Has default localtio for miners
    createAccount(numberOfClients,datadir,verbose)

def createBootnodes(numberOfClients,datadir="./ethereum/bootnodes/",verbose=False):
# method to create miners. Has default localtio for miners
    createAccount(numberOfClients,datadir,verbose)


