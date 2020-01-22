import secrets
import ecdsa
import hashlib
import base58

"""
秘密鍵->公開鍵->アドレスの順で生成するクラス
Python で Bitcoin（仮想通貨）アドレスを作る【python3】
https://qiita.com/kaz1shuu2/items/921dcbebb7fbea14f085
"""


class KeyAddressGenerator():
    def __init__(self):
        self.private_key, self.public_key, self.address = self.generate()

    def generate(self):
        p = 2 ** 256 - 2 ** 32 - 2 ** 9 - 2 ** 8 - 2 ** 7 - 2 ** 6 - 2 ** 4 - 1  # 素数らしい
        private_key = self.new_private_key(p)
        public_key = self.new_public_key(private_key)
        address = self.new_address(bytes.fromhex("00"), public_key)
        return private_key, public_key, address

    def new_private_key(self, p):
        private_key = secrets.randbelow(p)
        private_key = format(private_key, 'x')
        print("PrivateKey = " + private_key)
        return private_key

    def new_public_key(self, private_key):
        bin_private_key = bytes.fromhex(private_key)
        signing_key = ecdsa.SigningKey.from_string(bin_private_key, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.get_verifying_key()
        public_key = bytes.fromhex("04") + verifying_key.to_string()
        public_key = public_key.hex()
        # print("PublicKey = " + public_key)
        return public_key

    def new_address(self, version, public_key):
        ba = bytes.fromhex(public_key)  # 16進数公開鍵をバイト列に変換
        digest = hashlib.sha256(ba).digest()    # baをsha256でハッシュ化してできたものを文字列にして代入
        new_digest = hashlib.new('ripemd160')
        new_digest.update(digest)
        public_key_hash = new_digest.digest()

        pre_address = version + public_key_hash
        address = hashlib.sha256(pre_address).digest()
        address = hashlib.sha256(address).digest()
        checksum = address[:4]
        address = pre_address + checksum
        address = base58.b58encode(address)
        address = address.decode()
        # print("Address = " + address)
        return address

    def get_list(self):
        return self.private_key, self.public_key, self.address


pri_key, pub_key, addr = KeyAddressGenerator().get_list()
sk = ecdsa.SigningKey.from_string(bytes.fromhex(pri_key), curve=ecdsa.SECP256k1)
vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(pub_key.replace('04', '', 1)), curve=ecdsa.SECP256k1)
signature = sk.sign(b"message")
assert vk.verify(signature, b"message")

