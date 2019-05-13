
from iroha import IrohaCrypto
from .proto import transaction_pb2
import binascii
import sys
import os
from pprint import pprint


class Processor:

    def __init__(self, block_loader, keystore, peers_addresses):
        self.block_loader = block_loader
        self.keystore = keystore
        self.peers = peers_addresses
        self.peers_mapping = {}

    def process(self):
        prev_block_hash = '0' * 64

        for block in self.block_loader.blocks():
            block.block_v1.payload.prev_block_hash = prev_block_hash
            self.__process_transactions(block)
            self.__process_batches(block)
            self.__process_txs_signatures(block)
            self.__process_block_signatures(block)
            prev_block_hash = binascii.hexlify(
                IrohaCrypto.hash(block.block_v1))
        self.keystore.save_keys()
        self.__save_peers_mapping()

    def __renew_peer_addr(self, old):
        if not len(self.peers):
            print(
                'Specified peers list is too short. Please extend peers addresses list.',
                file=sys.stderr)
            sys.exit(3)
        new_peer = self.peers.pop(0)
        self.peers_mapping[old] = new_peer
        return new_peer

    def __save_peers_mapping(self):
        mapping_file = os.path.join(
            self.keystore.path, 'peers_mapping.txt')  # smells bad :(
        with open(mapping_file, 'wt') as mapping:
            pprint(self.peers_mapping, stream=mapping)

    def __process_transactions(self, block):
        """Replace all the public keys which are arguments of commands"""
        for tx_idx in range(len(block.block_v1.payload.transactions)):
            tx = block.block_v1.payload.transactions[tx_idx]
            for cmd_idx in range(len(tx.payload.reduced_payload.commands)):
                cmd = tx.payload.reduced_payload.commands[cmd_idx]
                if cmd.HasField('add_signatory'):
                    old_key = cmd.add_signatory.public_key
                    user = cmd.add_signatory.account_id
                    new_key = self.keystore.renew_key(
                        old_key, user=user).public_key
                    cmd.add_signatory.public_key = new_key
                elif cmd.HasField('remove_signatory'):
                    old_key = cmd.remove_signatory.public_key
                    user = cmd.remove_signatory.account_id
                    new_key = self.keystore.renew_key(
                        old_key, user=user).public_key
                    cmd.remove_signatory.public_key = new_key
                elif cmd.HasField('create_account'):
                    old_key = cmd.create_account.public_key
                    user = '{}@{}'.format(
                        cmd.create_account.account_name, cmd.create_account.domain_id)
                    new_key = self.keystore.renew_key(
                        old_key, user=user).public_key
                    cmd.create_account.public_key = new_key
                elif cmd.HasField('add_peer'):
                    old_key = cmd.add_peer.peer.peer_key
                    address = cmd.add_peer.peer.address
                    cmd.add_peer.peer.address = self.__renew_peer_addr(address)
                    new_key = self.keystore.renew_key(
                        old_key, peer_address=address).public_key
                    cmd.add_peer.peer.peer_key = new_key

    def __process_batches(self, block):
        """Recalculate reduced hashes in batch metas"""
        txs = block.block_v1.payload.transactions
        reduced_hashes = []
        batches = {}
        i = 0
        total_txs = len(txs)
        while i < total_txs:
            tx = txs[i]
            reduced_hash = IrohaCrypto.reduced_hash(tx)
            reduced_hashes.append(reduced_hash)

            if tx.payload.HasField('batch') and len(tx.payload.batch.reduced_hashes):
                batch = tx.payload.batch.SerializeToString()
                if not batch in batches:
                    batches[batch] = [i]
                else:
                    batches[batch].append(i)
            i += 1

        for _, batch_txs in batches.items():
            meta = txs[batch_txs[0]].payload.batch
            del meta.reduced_hashes[:]
            for tx_idx in batch_txs:
                meta.reduced_hashes.append(reduced_hashes[tx_idx])
            first = True
            for tx_idx in batch_txs:
                if first:
                    first = False
                    continue
                txs[tx_idx].payload.batch.CopyFrom(meta)

    def __process_txs_signatures(self, block):
        """Recalculate transactions signatures and resign them"""
        txs = block.block_v1.payload.transactions
        i = 0
        total_txs = len(txs)
        while i < total_txs:
            tx = txs[i]
            creator = tx.payload.reduced_payload.creator_account_id
            tx_keypairs = []
            for signature in tx.signatures:
                kp = self.keystore.renew_key(
                    signature.public_key, user=creator)
                tx_keypairs.append(kp)
            del tx.signatures[:]
            for kp in tx_keypairs:
                IrohaCrypto.sign_transaction(tx, kp.private_key)
            i += 1

    def __process_block_signatures(self, block):
        """Recalculate block signatures and resign it"""
        block_keypairs = []
        for signature in block.block_v1.signatures:
            kp = self.keystore.renew_key(
                signature.public_key, peer_address="unknown")
            block_keypairs.append(kp)
        del block.block_v1.signatures[:]
        for kp in block_keypairs:
            IrohaCrypto.sign_transaction(block.block_v1, kp.private_key)
