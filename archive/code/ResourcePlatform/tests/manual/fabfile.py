import fabric.api as fabi
import fabric.operations as fop
from hosts import *
import time

fabi.env.key_filename = '~/.ssh/cluster_2018_9_10'

fabi.env.skip_bad_hosts = True
fabi.env.warn_only = True
fabi.env.abort_on_prompts=True


@fabi.task
def test (ip):
    # with contextlib.suppress(FileNotFoundError):
    #     os.remove(filename+".txt")
	#cmd = "tmux new -d -s test 'ls'"
	cmd = "ls"
	out = fabi.execute(runCommand, cmd, hosts=ip)
	print(out[ip])

@fabi.task
def miner(ip=MINERIP):
	tsk = "tmux send-keys -t miner"
	geth = 'geth-linux-amd64/geth'
	cmd = []
	cmd.append("tmux new -d -s miner;")# '%s'" %(cd)
	cmd.append("%s 'cd %s' C-m;" %(tsk, MINERDIR))
	cmd.append("%s '%s --datadir eth/ init genesis-data.json' C-m;" %(tsk, geth))
	cmd.append("%s '%s account new --password password.txt --datadir eth/' C-m;" %(tsk, geth))
	cmd.append("%s '%s --datadir eth/ --rpc --rpcport %s --rpcaddr %s --nodiscover \
	               --rpcapi \"eth,web3,admin,miner,net,db\" --password password.txt --verbosity 3 --unlock 0 \
				   --networkid 15 --mine |& tee miner.log' C-m;" %(tsk, geth,MINERPORT,MINERIP))
	# tmux send-keys -t $miner "geth-linux-amd64/geth account new --password password.txt --datadir eth/" C-m

	out = fabi.execute(runCommand, ''.join(cmd), hosts=ip)
	print("done")
	print(out[ip])
@fabi.task
def stopminer(ip=MINERIP):
	cmd = "tmux kill-session -t miner"
	out = fabi.execute(runCommand, cmd, hosts=ip)

@fabi.task
def Directory(ip=DIR_IP):
	tsk = "tmux send -t directory"
	cmd =[]
	cmd.append("tmux new -d -s directory;")
	cmd.append("%s 'python3 %s/components/Directory.py %s %s |& tee %s/directory.log' C-m;" %(tsk, PROJECT,MINERIP,MINERPORT,LOGS))
	out = fabi.execute(runCommand, ''.join(cmd), hosts=ip)
@fabi.task
def stopDirectory(ip=DIR_IP):
	cmd = "tmux kill-session -t directory"
	out = fabi.execute(runCommand, cmd, hosts=ip)

@fabi.task
def Solver(ip=SOLVER_IP):
	tsk = "tmux send -t solver"
	cmd =[]
	cmd.append("tmux new -d -s solver;")
	cmd.append("%s 'python3.6 %s/components/Solver.py %s %s %s %s |& tee %s/solver.log' C-m;" %(tsk,PROJECT,MINERIP,MINERPORT,'1',DIR_IP,LOGS))
	out = fabi.execute(runCommand, ''.join(cmd), hosts=ip)
@fabi.task
def stopSolver(ip=SOLVER_IP):
	cmd = "tmux kill-session -t solver"
	out = fabi.execute(runCommand, cmd, hosts=ip)

@fabi.task
def Recorder(ip=RECORDER_IP):
	tsk = "tmux send -t recorder"
	cmd =[]
	cmd.append("tmux new -d -s recorder;")
	cmd.append("%s 'python3 %s/components/EventRecorder.py %s %s %s |& tee %s/recorder.log' C-m;" %(tsk, PROJECT,MINERIP,MINERPORT,DIR_IP,LOGS))
	out = fabi.execute(runCommand, ''.join(cmd), hosts=ip)
@fabi.task
def stopRecorder(ip=RECORDER_IP):
	cmd = "tmux kill-session -t recorder"
	out = fabi.execute(runCommand, cmd, hosts=ip)

#@fabi.parallel
def runCommand(command):
	"""run with fab -R '<role to run command on, e.g c2_1>' runCommand:<command to run>
		or to run on a specific host: fab -H '10.0.2.194:2222' runCommand:'hostname'"""
	results = ''
	with fabi.hide('output', 'running', 'warnings', 'aborts'), fabi.settings(warn_only=True):
		results = fabi.run(command)
	return(results)

@fabi.parallel
def prunCommand(command):
	"""run with fab -R '<role to run command on, e.g c2_1>' runCommand:<command to run>
		or to run on a specific host: fab -H '10.0.2.194:2222' runCommand:'hostname'"""
	results = ''
	with fabi.hide('output', 'running', 'warnings', 'aborts'), fabi.settings(warn_only=True):
		results = fabi.run(command)
	print(results)


def put(src,dst):
	fabi.put(src, dst)

@fabi.parallel
def pput(src,dst):
	fabi.put(src, dst)

def LED():
	fabi.run('echo 1 >> /sys/class/leds/beaglebone\:green\:usr2/brightness')
	time.sleep(5)
	fabi.run('echo 0 >> /sys/class/leds/beaglebone\:green\:usr2/brightness')
