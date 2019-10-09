export GETH="/home/riaps/projects/geth/geth-linux-amd64-1.8.22-7fa3509e"
export KEYSTORE="/home/riaps/projects/geth/geth-linux-amd64-1.8.22-7fa3509e/eth/keystore/"
export NODE1="/home/riaps/projects/geth/node1"
export NODE2="/home/riaps/projects/geth/node2"
startBC:
	tmux new -d -s node1
	tmux new -d -s node2
	tmux new -d -s miner
	tmux send -t node1 "cd $(NODE1); ./geth --keystore $(KEYSTORE) --port 30301 --datadir eth/ --rpc --rpcport 10001 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,net,db' --password password.txt --networkid 15 --unlock 0 console 2>node1.log" ENTER
	tmux send -t node2 "cd $(NODE2); ./geth --keystore $(KEYSTORE) --port 30302 --datadir eth/ --rpc --rpcport 10002 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,net,db' --password password.txt --networkid 15 --unlock 0 console 2>node2.log" ENTER
	tmux send -t miner "cd $(GETH); ./geth --port 30300 --datadir eth/ --rpc --rpcport 10000 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,miner,net,db' --password password.txt --unlock 0 --networkid 15 --mine --minerthreads=1 --etherbase=0 --targetgaslimit 200000000000000000 console 2>miner.log" ENTER
	
	# ./geth --keystore ~/projects/geth/geth-linux-amd64-1.8.22-7fa3509e/eth/keystore/ --port 30301 --datadir eth/ --rpc --rpcport 10001 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,net,db' --password password.txt --unlock 0 console 2>node1.log


initBC:
	tmux new -d -s geth
	tmux new -d -s node1
	tmux new -d -s node2

	tmux send -t geth "cd $(GETH)" ENTER
	tmux send -t node1 "cd $(NODE1)" ENTER
	tmux send -t node2 "cd $(NODE2)" ENTER

	tmux send -t geth "./geth account new --password password.txt --datadir eth/" ENTER
	tmux send -t geth "./geth --datadir eth/  init genesis.json" ENTER

	tmux send -t node1 "./geth --datadir eth/  init genesis.json" ENTER

	tmux send -t node2 "./geth --datadir eth/  init genesis.json" ENTER


	tmux send -t node1 "exit" ENTER

	tmux send -t node2 "exit" ENTER
	
	tmux send -t geth "exit" ENTER

	echo "update static-nodes.json" 

test:
	echo "update static-nodes.json" 


setupWrapper:
	sudo pip3 install antlr4-python3-runtime

export tool="/home/riaps/projects/transactive-blockchain/transax/solidity-wrapper/main.py"
export contract="/home/riaps/projects/transactive-blockchain/transax/smartcontract/Matching.sol"
export output="/home/riaps/projects/transactive-blockchain/transax/core"
wrap:
	python3 $(tool) $(contract) $(output)


#------------------------------------------------------------------------------
#    Docker compile contract
#------------------------------------------------------------------------------
solc : INPUT = /home/riaps/projects/transactive-blockchain/transax/smartcontract
solc:
	echo $(INPUT)
	mkdir -p $(INPUT)/output
	sudo docker run -it --rm\
		--name solcTest \
		--mount type=bind,source="$(INPUT)",target=/solidity/input \
		--mount type=bind,source="$(INPUT)/output",target=/solidity/output \
		ethereum/solc:0.4.25 \
		--optimize --overwrite --bin --bin-runtime --ast --asm --abi -o /solidity/output /solidity/input/Matching.sol
