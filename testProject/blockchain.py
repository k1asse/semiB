import json
import hashlib
import merkletools
import time
from transaction import Transaction


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
        return json.dumps(self.get_dictionary())

    def get_json_binary(self):
        """jsonのバイナリ形式を取得する(hash化する際に利用)"""
        return self.get_json().encode()

    def get_dictionary(self):
        for index, block in enumerate(self.chain):
            dictionary = {"block" + str(index): block.get_dictionary()}
        return dictionary

    def add_block(self, block):
        """ブロックを末尾に追加"""
        self.chain.append(block)

    def get_tail_header_hash(self):
        """ブロックチェーンの末尾ブロックヘッダのハッシュを取得する"""
        if len(self.chain) == 0:
            return None
        else:
            return self.chain[-1].get_header_hash()
