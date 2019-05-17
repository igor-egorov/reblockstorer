# ReBlockStorer

A tool for regenaration of all the keys for some existing Hyperledger Iroha blockstore.

## Installation

1. Download the sources
2. `pip install .`

## Usage example

`reblockstore -b /path/to/source/blockstore -o /path/to/new/blockstore -p /path/to/peers/list -k /path/to/store/new/keys/and/mappings`

Peers list file should contain new peers addresses with internal ports (used as argument of AddPeer command) one by line.
File contents example:
```
localhost:10001
localhost:10002
```

As a result, a new blockstore will be produced with the same contents as the source blockstore, but all the keys and signatures will be regenerated and you will be able to run the network for tests or just continue the work with the new version of blockstore when old keys were lost.
