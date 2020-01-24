import json
import hashlib
import merkletools
import time
from transaction import Transaction
from block import Block


class BlockChain:
    """
    ブロックチェーン
    ・ブロックの追加
    ・ブロックチェーンの末尾のデータを取得したりとかする
    """

    def __init__(self):
        self.chain = []     # 枝分かれ?何それ

    def get_json(self):
        """1回辞書型に変換して、jsonを取得する"""
        return json.dumps(self.get_block_list())

    def get_json_binary(self):
        """jsonのバイナリ形式を取得する(hash化する際に利用)"""
        return self.get_json().encode()

    def get_block_list(self):
        """大外枠はリストです"""
        block_list = []
        for bl in self.chain:
            block_list.append(bl.get_dictionary())
        return block_list

    def add_block(self, block):
        """ブロックを末尾に追加"""
        self.chain.append(block)

    def get_tail_header_hash(self):
        """ブロックチェーンの末尾ブロックヘッダのハッシュを取得する"""
        if len(self.chain) == 0:
            return None
        else:
            return self.chain[-1].get_header_hash()


transaction = Transaction()
transaction.add_input('prehash', 'index', None, None)
transaction.add_input('prehash2', 'index2', 'sig2', 'pub_key2')
transaction.add_output(200, 'key_hash')

transaction2 = Transaction()
transaction2.add_input('prehas3', 'index', None, None)
transaction2.add_input('prehash4', 'index4', 'sig4', 'pub_key4')
transaction2.add_output(22020200, 'key_hash')

block = Block("pre_hash", "target", [transaction, transaction2])
block_chain = BlockChain()
block_chain.add_block(block)
block_chain.add_block(block)

data = json.loads(block_chain.get_json())
print(json.dumps(data, indent=2))

