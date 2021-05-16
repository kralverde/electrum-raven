import unittest
import threading

from electrum.scrypt import scrypt_1024_1_1_80 as scryptGetHash
from electrum.util import bfh,bh2u
from electrum.ravencoin import rev_hex,int_to_hex
from electrum.blockchain import serialize_header


class Test_scrypt(unittest.TestCase):

    def test_scrypt(self):
        #0200000011f1fe21e0b66dc214be46366465cb95d29830e31ddd225a11349a836a993bf7b5db36b3e5593d039779bff204d132b65ee029a2e499ebeb5a4b19cbe862eee2b623cc5276676c1c000e1c60
        header = {'block_height': 12095, 'nonce': 1612451328, 'timestamp': 1389110198, 'version': 2, 'prev_block_hash': 'f73b996a839a34115a22dd1de33098d295cb65643646be14c26db6e021fef111', 'merkle_root': 'e2ee62e8cb194b5aebeb99e4a229e05eb632d104f2bf7997033d59e5b336dbb5', 'bits': 476866422}
        powhash = rev_hex(bh2u(scryptGetHash(bfh(serialize_header(header)))))
        self.assertEqual(powhash, '00000000335c88172421df73a1c1f22f4d7c23d8ef34c78d728c4eff3ba24a34')

