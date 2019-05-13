
import os
import string
from pprint import pprint
from iroha import IrohaCrypto


class Keypair:
    peers_saved = 0

    def __init__(self, source_public, user, peer_address):
        assert(user or peer_address)
        self.source_public_key = source_public
        self.private_key = IrohaCrypto.private_key()
        self.public_key = IrohaCrypto.derive_public_key(self.private_key)
        self.user = user
        self.peer_address = peer_address

    def __repr__(self):
        d = {'private': self.private_key.decode('utf-8'),
             'public': self.public_key.decode('utf-8')}
        if self.user:
            d['user'] = self.user
        if self.peer_address:
            d['peer'] = self.peer_address
        return str(d)

    def save(self, path):
        if self.user:
            prefix = self.user
        else:
            Keypair.peers_saved += 1
            prefix = 'node{}-{}'.format(
                Keypair.peers_saved, self.__format_peer_address(self.peer_address))
        file_path = os.path.join(path, prefix)
        with open(file_path + '.priv', 'w') as priv:
            priv.write(self.private_key.decode('utf-8'))
        with open(file_path + '.pub', 'w') as pub:
            pub.write(self.public_key.decode('utf-8'))

    def __format_peer_address(self, addr):
        addr = addr.replace(':', '__')
        valid_chars = '-_.(){}{}'.format(string.ascii_letters, string.digits)
        addr = ''.join(c for c in addr if c in valid_chars)
        return addr


class Keystore:

    def __init__(self, keystore_path):
        self.path = keystore_path
        self.keys = {}

    def renew_key(self, public_key, user=None, peer_address=None):
        if public_key in self.keys:
            return self.keys[public_key]
        else:
            assert(user or peer_address)
            keypair = Keypair(public_key, user, peer_address)
            self.keys[public_key] = keypair
            return keypair

    def save_keys(self):
        mapping_file = os.path.join(self.path, 'keys_mapping.txt')
        with open(mapping_file, 'wt') as mapping:
            pprint(self.keys, stream=mapping)
        for _, keypair in self.keys.items():
            keypair.save(self.path)
