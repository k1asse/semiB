import json
import hashlib
import ecdsa
import pprint
from ecdsa_generator import KeyAddressGenerator


class Transaction:
    """取引情報を記憶するクラス"""

    def __init__(self):
        self.version = "0000"
        self.inputs = []
        self.outputs = []

    def get_json(self):
        """1回辞書型に変換して、jsonを取得する"""
        return json.dumps(self.get_dictionary())

    def get_json_binary(self):
        """jsonのバイナリ形式を取得する(hash化する際に利用)"""
        return self.get_json().encode()

    def get_dictionary(self):
        """Transactionのデータを辞書型に変換する"""
        dictionary = {'version': self.version,
                      'input_number': len(self.inputs),
                      'output_number': len(self.outputs),
                      'inputs': {},
                      'outputs': {}
                      }
        for index, item in enumerate(self.inputs):
            dictionary['inputs']['input' + str(index)] = item.get_dictionary()
        for index, item in enumerate(self.outputs):
            dictionary['outputs']['output' + str(index)] = item.get_dictionary()
        return dictionary

    def add_input(self, pre_hash, index, signature, pub_key):
        self.inputs.append(Input(pre_hash, index, signature, pub_key))

    def add_output(self, value, pub_key_hash):
        self.outputs.append(Output(value, pub_key_hash))

    def assign_signature(self, pub_key, prv_key):
        """送信元の公開鍵pub_keyを用いて、signとpub_keyを埋める"""
        # print(pub_key)
        #
        if len(self.inputs) > 0 and not self.inputs[0].exist_sign_and_pub_key():
            # 署名前のテンプレを作る
            h = hashlib.new('ripemd160')
            h.update(hashlib.sha256(pub_key.encode()).digest())
            self.inputs[0].signature = h.hexdigest()
            # print(self.inputs[0].get_dictionary())
            # 二重ハッシュをかけてダイジェストAを作る
            # jsonをバイナリに変換してからsha256^2
            digest_a = hashlib.sha256(hashlib.sha256(self.get_json().encode()).digest()).digest()
            sk = ecdsa.SigningKey.from_string(bytes.fromhex(prv_key), curve=ecdsa.SECP256k1)
            # 最後、代入 signatureはバイト列から16進数に変換して保存(JSONにする際バイナリだとできない)
            self.inputs[0].signature = sk.sign(digest_a).hex()
            self.inputs[0].public_key = pub_key

    def check_signature(self):
        # 署名と公開鍵を取り出す
        signature = bytes.fromhex(self.inputs[0].signature)
        public_key = self.inputs[0].public_key
        self.inputs[0].public_key = None

        # hash160(pub_key)する
        h = hashlib.new('ripemd160')
        h.update(hashlib.sha256(public_key.encode()).digest())
        self.inputs[0].signature = h.hexdigest()

        # print(self.inputs[0].get_dictionary())

        # 二重ハッシュをかけてダイジェストBを作る
        # jsonをバイナリに変換してからsha256^2
        digest_b = hashlib.sha256(hashlib.sha256(self.get_json().encode()).digest()).digest()
        # print(digest_b)

        # 公開鍵を用いて
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key.replace('04', '', 1)), curve=ecdsa.SECP256k1)
        assert vk.verify(signature, digest_b)


class Input:
    """トランザクションの入力部分"""

    def __init__(self, pre_hash, index, sign, pub_key):
        self.previous_hash = pre_hash
        self.output_index = index
        self.signature = sign
        self.public_key = pub_key

    def get_dictionary(self):
        """入力のデータを辞書型に変換する"""
        dictionary = {
            'previous_hash': self.previous_hash,
            'output_index': self.output_index,
            'signature': self.signature,
            'public_key': self.public_key
        }
        return dictionary

    def exist_sign_and_pub_key(self):
        if self.signature and self.public_key:
            return True
        else:
            return False


class Output:
    """トランザクションの出力部分"""

    def __init__(self, value, pub_key_hash):
        self.value = value
        self.receiver_public_key_hash = pub_key_hash

    def get_dictionary(self):
        """出力のデータを辞書型に変換する"""
        dictionary = {
            'value': self.value,
            'receiver_public_key_hash': self.receiver_public_key_hash
        }
        return dictionary


transaction = Transaction()
transaction.add_input('prehash', 'index', None, None)
transaction.add_input('prehash2', 'index2', 'sig2', 'pub_key2')
transaction.add_output(200, 'key_hash')
print(transaction.get_dictionary())
pri_key, pub_key, addr = KeyAddressGenerator().get_list()
transaction.assign_signature(pub_key, pri_key)
# transaction.version = "0001"
pprint.pprint(transaction.get_json())
transaction.check_signature()

