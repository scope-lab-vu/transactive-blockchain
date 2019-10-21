export MINER=$(HOME)/projects/geth/miner
export KEYSTORE="$(HOME)/projects/geth/miner/eth/keystore"
export NODE1="$(HOME)/projects/geth/node1"
export NODE2="$(HOME)/projects/geth/node2"
export TOOLS=$(HOME)/projects/geth/geth-tools
startBC:
	tmux new -d -s node1
	tmux new -d -s node2
	tmux new -d -s miner
	tmux send -t node1 "cd $(NODE1); ./geth --keystore $(KEYSTORE) --port 30301 --datadir eth/ --rpc --rpcport 10001 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,net,db' --password password.txt --networkid 15 --unlock 0 console 2>node1.log" ENTER
	tmux send -t node2 "cd $(NODE2); ./geth --keystore $(KEYSTORE) --port 30302 --datadir eth/ --rpc --rpcport 10002 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,net,db' --password password.txt --networkid 15 --unlock 0 console 2>node2.log" ENTER
	tmux send -t miner "cd $(MINER); ./geth --port 30300 --datadir eth/ --rpc --rpcport 10000 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,miner,net,db' --password password.txt --allow-insecure-unlock --unlock 0 --networkid 15 --mine --minerthreads=1 --etherbase=0 --targetgaslimit 200000000000000000 console 2>miner.log" ENTER
	
	# ./geth --keystore ~/projects/geth/geth-linux-amd64-1.8.22-7fa3509e/eth/keystore/ --port 30301 --datadir eth/ --rpc --rpcport 10001 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,net,db' --password password.txt --unlock 0 console 2>node1.log


initBC:

	rm -rf $(MINER)/eth
	rm -rf $(NODE1)/eth
	rm -rf $(NODE2)/eth

	tmux new -d -s miner
	tmux new -d -s node1
	tmux new -d -s node2

	tmux send -t miner "cd $(MINER)" ENTER
	tmux send -t node1 "cd $(NODE1)" ENTER
	tmux send -t node2 "cd $(NODE2)" ENTER

	tmux send -t miner "./geth account new --password password.txt --datadir eth/" ENTER
	tmux send -t miner "./geth --datadir eth/  init genesis.json" ENTER

	tmux send -t node1 "./geth --datadir eth/  init genesis.json" ENTER

	tmux send -t node2 "./geth --datadir eth/  init genesis.json" ENTER


	echo "update static-nodes.json" 

	tmux send -t miner "$(TOOLS)/bootnode -genkey $(MINER)/eth/geth/nodekey" ENTER

		
	tmux send -t miner "$(eval NODEKEY=$(shell cat $(MINER)/eth/geth/nodekey))" ENTER

	tmux send -t miner "$(eval ENODE=$(shell $(TOOLS)/bootnode -nodekeyhex $(NODEKEY) -writeaddress))" ENTER 
	
	tmux send -t miner "echo [\"enode://$(ENODE)@127.0.0.1:30300?discport=0\"] > $(NODE1)/eth/geth/static-nodes.json" ENTER

	tmux send -t miner "echo [\"enode://$(ENODE)@127.0.0.1:30300?discport=0\"] > $(NODE2)/eth/geth/static-nodes.json" ENTER

	
	tmux send -t node1 "exit" ENTER

	tmux send -t node2 "exit" ENTER
	
	tmux send -t miner "exit" ENTER

	sleep 5

	cat ~/projects/geth/node1/eth/geth/static-nodes.json  
	cat ~/projects/geth/node2/eth/geth/static-nodes.json  
	
test:
	echo "update static-nodes.json" 


setupWrapper:
	sudo pip3 install antlr4-python3-runtime

export tool="$(HOME)/projects/transactive-blockchain/transax/solidity-wrapper/main.py"
export contract="$(HOME)/projects/transactive-blockchain/transax/smartcontract/Matching.sol"
export output="$(HOME)/projects/transactive-blockchain/transax/core"
wrap:
	python3 $(tool) $(contract) $(output)


#------------------------------------------------------------------------------
#    Docker compile contract
#------------------------------------------------------------------------------
solc : INPUT = $(HOME)/projects/transactive-blockchain/transax/smartcontract
solc:
	echo $(INPUT)
	mkdir -p $(INPUT)/output
	sudo docker run -it --rm\
		--name solcTest \
		--mount type=bind,source="$(INPUT)",target=/solidity/input \
		--mount type=bind,source="$(INPUT)/output",target=/solidity/output \
		ethereum/solc:0.4.25 \
		--optimize --overwrite --bin --bin-runtime --ast --asm --abi -o /solidity/output /solidity/input/Matching.sol
