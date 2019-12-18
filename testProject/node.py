from transaction import Transaction
# ノード側のマシンが実行するプログラム


class Node:
    """ブロックの生成・検査を行うノード"""

    def __init__(self, user_port, node_port):
        self.number = 1  # ノード番号
        self.block_chain = []  # ブロックチェーン
        self.user_port = user_port  # ユーザとの接続を行うポート
        self.node_port = node_port  # ノードとの接続を行うポート
        NUMBER_OF_ZERO_SEQUENCE = 4  # ブロック生成の権限に必要なハッシュ値の先頭0の個数

    def connect_nodes(self):
        """
        すでに存在するノード群に接続する
        """

    def receive_transaction(self):
        """
        取引情報の受信を行う
        """

    def check_transaction(self):
        """
        取引情報のチェックを行う
        """

    def assign_nonce(self):
        """
        ナンスを代入する、0が先頭にNUMBER_OF_ZERO_SEQUENCE個来たらノード全体に送信
        """

    def generate_block(self):
        """
        ブロックを生成する
        """

    def send_result(self, user, message):
        """
        ユーザに処理結果がOK/NGであったことを送信する
        """