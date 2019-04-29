
import os
from pprint import pprint
from iroha import IrohaCrypto


class Keypair:

    def __init__(self, source_public, private, public, prefix):
        self.source_public_key = source_public
        self.private_key = private
        self.public_key = public
        self.prefix = prefix

    def save(self, path, suffix):
        file_path = os.path.join(path, self.prefix + suffix)
        with open(file_path + '.priv', 'w') as priv:
            priv.write(self.private_key)
        with open(file_path + '.pub', 'w') as pub:
            pub.write(self.public_key)


class Keystore:

    def __init__(self, keystore_path):
        self.path = keystore_path
        self.keys = {}

    def renew_key(self, public_key, prefix='key'):
        if public_key in self.keys:
            return self.keys[public_key]
        else:
            private = IrohaCrypto.private_key()
            public = IrohaCrypto.derive_public_key(private)
            keypair = Keypair(public_key, private, public, prefix)
            self.keys[public_key] = keypair
            return public

    def save_keys(self):
        index = 0
        mapping_file = os.path.join(self.path, 'keys_mapping.txt')
        with open(mapping_file, 'wt') as mapping:
            pprint(self.keys, stream=mapping)
        for _, keypair in self.keys:
            keypair.save(str(index))
            index += 1
