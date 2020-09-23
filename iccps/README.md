install geth

`cd <>/transactive-blockchain-iccps/standalone-demo`

update 

Setup new geth account

``sudo docker run \
 --mount type=bind,source="/home/riaps/projects/transactive-blockchain/geth-data",target=/data \
  -it \
  -p 30303:30303 \
  ethereum/client-go:stable account new --password /data/geth-config/password.txt --datadir /data/eth ``
  
 init geth
 
 ``sudo docker run \
  --mount type=bind,source="/home/riaps/projects/transactive-blockchain/geth-data",target=/data \
  -it \
  -p 30303:30303 \
 ethereum/client-go:stable \
 --nousb --datadir /data/eth/  init /data/geth-config/genesis.json
 ``
  
 Run geth miner node
  
``--datadir /data/eth`` specifies the data directory of the geth node. Required if running multiple nodes locally. 
``--ethash.dagdir /data/Ethash`` so we don't have to regenerate the dag everytime we start
``--networkid 15`` selects which network to use. Replace 15 with any non-negative number other than 1,2,3 or 4 since those are mainnets. 
``--nousb`` gets rid of error message by disabling USB wallet support
``--nodiscover`` don't look for peers
``--mine --minerthreads=1 --miner.etherbase=0`` make this instance a miner
``--targetgaslimit 200000000000000000`` set high limit to make sure no contract function calls fail


  ``sudo docker run \
  --mount type=bind,source="/home/riaps/projects/transactive-blockchain/geth-data",target=/data \
  -it -p 30303:30303 \
  ethereum/client-go:stable --datadir /data/eth --ethash.dagdir /data/ethash \
  --networkid 15 --nousb --nodiscover \
  --mine --miner.threads=1 --miner.etherbase=0 \
  --miner.gastarget 200000000000000000 \
  console``
   

  
 check if miner is accumulating ether  
`web3.fromWei(eth.getBalance(eth.accounts[0]))`

check existing accounts
`eth.accounts`



