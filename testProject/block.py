import json
import hashlib
import merkletools
import time
import pprint
from transaction import Transaction


class Block:
    """
    ブロックチェーンを構成するブロック
    参考:
    https://www.slideshare.net/kenjiurushima/20140602-bitcoin1-201406031222

    マークルルート
    参考:
    https://github.com/Tierion/pymerkletools
    """

    def __init__(self, pre_hash, target, trans_list):
        """
        init時には、
        1. transactionが全て揃っている,
        上の条件を満たす必要がある
        """
        self.transaction_list = trans_list  # Transactionクラスのリスト
        self.merkle_root = self.get_merkle_root(trans_list)
        self.time = int(time.time())
        self.header = BlockHeader(pre_hash, self.merkle_root, self.time, target)

    @classmethod
    def from_json(cls, json_str):
        dictionary = json.loads(json_str)
        # transactions[]から、トランザクションを取得する
        trans_list = []
        for item in dictionary["transactions"]:
            trans_json = json.dumps(item)
            trans_list.append(Transaction.from_json(trans_json))
        return Block(dictionary["header"]["previous_block_header_hash"],
                     dictionary["header"]["target"],
                     trans_list)

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
            'transactions': []
        }
        for index, item in enumerate(self.transaction_list):
            dictionary['transactions'].append(item.get_dictionary())
        return dictionary

    def get_header_hash(self):
        return self.header.get_hash()

    def get_hash(self):
        return hashlib.sha256(hashlib.sha256(self.get_json_binary()).digest()).digest()


    def get_merkle_root(self, trans_list):
        """トランザクションのリストをmerkle treeにしてそのrootを得る"""
        # Transactionクラスのインスタンスで構成されたtrans_listを
        # 全てjson形式にしてlistに追加していく
        # パッケージの関数でバイナリのリストになるのでencode()とかはしなくていい
        # 本家はSHA256^2らしいけどSHA256で我慢
        mt = merkletools.MerkleTools()
        trans_json_list = []
        for trans in trans_list:
            trans_json_list.append(trans.get_json())
        mt.add_leaf(trans_json_list, True)
        mt.make_tree()
        return mt.get_merkle_root()

    def set_nonce(self, nonce):
        self.header.nonce = nonce


class BlockHeader:
    def __init__(self, pre_hash, merkle, tm, target, nonce=None):
        self.previous_block_header_hash = pre_hash
        self.merkle_root_hash = merkle
        self.unix_time = tm
        self.target = target
        self.nonce = nonce

    @classmethod
    def from_json(cls, json_str):
        """jsonからBlockHeaderクラスのインスタンスを返す"""
        dictionary = json.loads(json_str)
        return BlockHeader(
            dictionary['previous_block_header_hash'],
            dictionary['merkle_root_hash'],
            dictionary['unix_time'],
            dictionary['target'],
            dictionary['nonce']
        )

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


transaction = Transaction()
transaction.add_input('pre_hash', 'index', None, None)
transaction.add_input('pre_hash2', 'index2', 'sig2', 'pub_key2')
transaction.add_output(200, 'key_hash')

transaction2 = Transaction()
transaction2.add_input('pre_hash3', 'index', None, None)
transaction2.add_input('pre_hash4', 'index4', 'sig4', 'pub_key4')
transaction2.add_output(22020200, 'key_hash')

block = Block("pre_hash", "target", [transaction, transaction2])
# pprint.pprint(block.get_dictionary())
# pprint.pprint(transaction.get_dictionary())
data = json.loads(block.get_json())
print(json.dumps(data, indent=2))

