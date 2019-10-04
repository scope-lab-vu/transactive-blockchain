export GETH="/home/riaps/projects/geth-linux-amd64-1.8.22-7fa3509e"
startBC:
	cd $(GETH); ./geth --datadir eth/ --rpc --rpcport 10000 --rpcaddr localhost --nodiscover --rpcapi 'eth,web3,admin,miner,net,db' --password password.txt --unlock 0 --networkid 15 --mine --minerthreads=1 --etherbase=0 --targetgaslimit 200000000000000000 console


initBC:
	tmux new -d -s geth
	tmux send -t geth "cd $(GETH)" ENTER
	tmux send -t geth "./geth account new --password password.txt --datadir eth/" ENTER
	tmux send -t geth "./geth --datadir eth/  init genesis.json" ENTER


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
