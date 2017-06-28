#from fabric.api import run
from fabric.api import env

from fabric.operations import run, put
from fabric.contrib.project import rsync_project
from StringIO import StringIO
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

env.use_ssh_config = True

#env.hosts = [
#    'eth1',
#    'eth2',
#    'eth3',
#    'eth4',
#    'eth5',
#    'eth6',
#    ]

def anonymous():
    run("uname -a")

def ls():
    run("ls")

def copyBlockchain(localPath,remotePath):
    # make sure the directory is there!
    run('mkdir -p ' + remotePath)

    # our local 'testdirectory' - it may contain files or subdirectories ...
    # put(localPath, remotePath)

    rsync_project(local_dir=localPath, remote_dir=remotePath)
    #put('~/ethereum/', remotePath)

# This starts the appropriate number of clients on a host
# ran by 'fab -H <hostname> startClients:<param>=<value>'
def startClients(dsoCount=0,prosumerCount=1,startProsumerRpcPort=8545,minerCount=0):

    command = "echo command "
    command += " --prosumerCount=" + str(prosumerCount)
    command += " --dsoCount=" + str(dsoCount)
    command += " --prosumerRpcStartPort=" + str(startProsumerRpcPort)
    command += " --minerCount=" + str(minerCount)
    run(command)

def createAccounts(numberOfClients,datadir="./.ethereum"):
    fh = StringIO();
    result=''
    for i in range(1,int(numberOfClients)+1):
        accountCommand = "geth account new --password ./password.txt --datadir " + str(datadir)  + str(i)
        results = run(accountCommand, stdout=fh)
#        lines = results.split('\n')
#        for line in lines:
#            if line.startswith("Address"):
#                result = result + line[10:50] + '\n'
        print results
