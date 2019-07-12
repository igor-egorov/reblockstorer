
import os
import string
from pprint import pprint
from iroha import IrohaCrypto


class Keypair:
    peers_saved = 0

    def __init__(self, source_public, user, peer_address, source_private=None):
        assert(user or peer_address)
        self.used = False
        self.source_public_key = source_public
        if None == source_private:
            self.private_key = IrohaCrypto.private_key()
            self.public_key = IrohaCrypto.derive_public_key(self.private_key)
        else:
            self.private_key = source_private
            self.public_key = IrohaCrypto.derive_public_key(source_private)
            assert(source_public == self.public_key.decode('utf-8'))
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

    def __init__(self, keystore_path, existing_keys_path=None):
        self.path = keystore_path
        self.keys = {}
        if existing_keys_path:
            self.__load_existing_keys(existing_keys_path)

    def __load_existing_keys(self, path):
        for priv in os.listdir(path):
            priv_path = os.path.join(path, priv)
            if priv.endswith('.priv') and os.path.isfile(priv_path):
                key_name = priv[:-5]
                pub = key_name + '.pub'
                pub_path = os.path.join(path, pub)
                if os.path.exists(pub_path) and os.path.isfile(pub_path):
                    priv_hex = open(priv_path, 'rb').read()
                    pub_hex = open(pub_path, 'rb').read()
                    pub_hex_str = pub_hex.decode('utf-8')
                    keypair = Keypair(
                        source_public=pub_hex.decode('utf-8'),
                        user=key_name if '@' in key_name else None,
                        peer_address=key_name if '@' not in key_name else None,
                        source_private=priv_hex
                    )
                    self.keys[pub_hex_str] = keypair
                    print('Keypair loaded: name={}, guessed_type={}, public_key={}'.format(
                        key_name,
                        'user' if keypair.user else 'peer',
                        pub_hex_str
                    ))

    def renew_key(self, public_key, user=None, peer_address=None):
        if public_key in self.keys:
            self.keys[public_key].used = True
            return self.keys[public_key]
        else:
            assert(user or peer_address)
            keypair = Keypair(public_key, user, peer_address)
            keypair.used = True
            self.keys[public_key] = keypair
            return keypair

    def save_keys(self):
        mapping_file = os.path.join(self.path, 'keys_mapping.txt')
        for _, kp in self.keys.items():
            if not kp.used:
                print('Warning: keypair was loaded but not used: {}'.format(
                    kp.user if kp.user else kp.peer_address))
        with open(mapping_file, 'wt') as mapping:
            pprint(self.keys, stream=mapping)
        for _, keypair in self.keys.items():
            keypair.save(self.path)
