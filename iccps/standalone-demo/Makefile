export MINER=$(HOME)/projects/geth/miner
export KEYSTORE=$(HOME)/projects/geth/miner/eth/keystore
export NODE1=$(HOME)/projects/geth/node1
export NODE2=$(HOME)/projects/geth/node2
export TOOLS=$(HOME)/projects/geth/geth-tools

startBC:
	tmux new -d -s miner
	tmux send -t miner "cd $(MINER); ./geth --nodekey eth/geth/minerkey --port 30300 --datadir eth/ --rpc --rpcport 10000 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,miner,net,db' --password password.txt --allow-insecure-unlock --unlock 0 --networkid 15 --mine --minerthreads=1 --etherbase=0 --targetgaslimit 200000000000000000 console 2>miner.log" ENTER
	
	# ./geth --keystore ~/projects/geth/geth-linux-amd64-1.8.22-7fa3509e/eth/keystore/ --port 30301 --datadir eth/ --rpc --rpcport 10001 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,net,db' --password password.txt --unlock 0 console 2>node1.log


.ONESHELL:
initBC: 
	echo func;

	rm -rf $(MINER)/eth ;\
	

	$(MINER)/geth account new --password $(MINER)/password.txt --datadir $(MINER)/eth/ ;\
	$(MINER)/geth --datadir $(MINER)/eth/  init $(MINER)/genesis.json ;\
	
	
	$(TOOLS)/bootnode -genkey $(MINER)/eth/geth/minerkey; \





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
