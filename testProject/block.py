import json
import hashlib
from transaction import Transaction, Input, Output


class Block:
    """
    ブロックチェーンを構成するブロック
    参考:
    https://www.slideshare.net/kenjiurushima/20140602-bitcoin1-201406031222
    """

    def __init__(self, pre_hash, merkle, time, target, nonce):
        self.header = BlockHeader(pre_hash, merkle, time, target, nonce)
        self.transaction_list = []  # Transactionクラスのリスト

    def get_json(self):
        """1回辞書型に変換して、jsonを取得する"""
        return json.dumps(self.get_dictionary())

    def get_json_binary(self):
        """jsonのバイナリ形式を取得する(hash化する際に利用)"""
        return self.get_json().encode()

    def get_dictionary(self):
        """Blockのデータを辞書型に変換する"""
        dictionary = {
            'header': self.header.get_dictionary(),
            'transaction_number': len(self.transaction_list),
            'transactions': {}
        }
        for index, item in enumerate(self.transaction_list):
            dictionary['transactions']['transaction' + str(index)] = item.get_json()
        return dictionary

    def add_transaction(self, transaction):
        """Transactionクラスのインスタンスをリストに格納する"""
        self.transaction_list.append(transaction)


class BlockHeader:
    def __init__(self, pre_hash, merkle, time, target, nonce):
        self.previous_block_header_hash = pre_hash
        self.merkle_root_hash = merkle
        self.unix_time = time
        self.target = target
        self.nonce = nonce

    def get_json(self):
        """1回辞書型に変換して、jsonを取得する"""
        return json.dumps(self.get_dictionary())

    def get_json_binary(self):
        """jsonのバイナリ形式を取得する(hash化する際に利用)"""
        return self.get_json().encode()

    def get_dictionary(self):
        """BlockHeaderのデータを辞書型に変換する"""
        dictionary = {
            'previous_block_header_hash': self.previous_block_header_hash,
            'merkle_root_hash': self.merkle_root_hash,
            'unix_time': self.unix_time,
            'target': self.target,
            'nonce': self.nonce
        }
        return dictionary

    def get_hash(self):
        return hashlib.sha256(hashlib.sha256(self.get_json_binary()).digest()).digest()


block = Block("pre_hash", "merkle", "time", "target", "nonce")
transaction = Transaction()
transaction.add_input('prehash', 'index', None, None)
transaction.add_input('prehash2', 'index2', 'sig2', 'pub_key2')
transaction.add_output(200, 'key_hash')
block.add_transaction(transaction)
print(transaction.get_dictionary())

print(block.get_dictionary())





