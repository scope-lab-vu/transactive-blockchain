# Ethereum Test Network Managemant Application

This program manages a test-network of Ethereum nodes. Custom Configuration
Schema is used (JSON file: 'network-config.json') is used to deploy a fresh
network onto the testbed.

Note: This project assumes that the machine running the configuration has
access to all hosts in the testbed and has a properly configured `~/.ssh/config` 
file for named access to each host. This along with python's Fabric API provides
easy access programmatically for secure command distribution among all the hosts.


## File structure

Note: Additional files exist currently, but they will be cleaned up after
intgration of code into proper heirarchy of CLI App.


```text

│
├── fabfile.py              -- Fabric Config File.
│
├── network-config.json     -- sample network configuration file.
│
├── network-manager.py      -- CLI App to manage the test network.
│
├── blockchain/
│        │
│        ├── __init__.py    -- module init file.
│        │
│        └── blockchain.py  -- blockchain specific command files.
│        
├── bootnodes/
│        │
│        ├── __init__.py    -- module init file.
│        │
│        └── bootnodes.py   -- bootnodes specific command files.
│       
├── clients/
│        │
│        ├── __init__.py    -- module init file.
│        │
│        └── clients.py     -- clients specific command files.
│        
├── config/
│        │        
│        ├── __init__.py    -- module init file.
│        │
│        └── config         -- appliciation configuration realted files.
│        
└── miners/
         │
         ├── __init__.py    -- module init file.
         │
         └── config         -- miners specific realted files.

```         

## Help on running network-manager.py

Program has `--help` command line argument detection for each command, 
sub-command, etc.
