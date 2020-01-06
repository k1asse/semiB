from transaction import Transaction
import socket
# ユーザ側のマシンが実行するプログラム


class User:
    """仮想通貨のユーザ"""

    def __init__(self, name):  # インスタンス作成時に呼び出されるメソッド
        self.name = name
        self.__test_name = name  # プライベート変数
        self.balance = 100
        self.friends = []
        print("user instance initialized name: " + self.name)

    def send_request(self, transaction, port):
        """
        ユーザがノードたちに接続して、
        用意した取引情報を送信する
        """
        print("called send_request from " + self.name)
        transaction.print_short_data()
        self.connect_nodes(port)  # ノードに接続する

    def connect_nodes(self, port):
        """
        ノードたちに接続する (TODO send_requestに内包したらいいかも)
        ユーザとの接続用port: 10000, 10001, ..., 10009
        TCPな
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # ノードを指定
            s.connect(('127.0.0.1', port))
            while True:
                # 文字列を取得
                string = input("string:").encode()
                # サーバにメッセージを送る
                s.sendall(string)
                # ネットワークのバッファサイズは1024なので、サーバからの文字列取得も1024
                data = s.recv(1024)
                # サーバからくる文字列を表示
                print(repr(data))


    def make_transaction(self):
        """
        取引情報を作成する
        取引情報の文字列の先頭が"transaction"であれば
        ノードが取引情報だと思ってくれます
        """


user = User("Takahashi")
user2 = User("Suzuki")

trans = Transaction("Takahashi", "Suzuki", 300)
print(user.name)  # pythonは_# _を変数名の前につけないとpublic変数扱い
# print(user.__test_name) private変数化(厳密には違うらしい)されてるのでエラーが出る
port = int(input("Port Number: "))
user.send_request(trans, port)
