from transaction import Transaction
# ユーザ側のマシンが実行するプログラム


class User:
    """仮想通貨のユーザ"""

    def __init__(self, name):  # インスタンス作成時に呼び出されるメソッド
        self.name = name
        self.__test_name = name
        self.balance = 100
        self.friends = []
        print("user instance initialized name: " + self.name)

    def send_request(self, transaction):
        """
        ユーザがノードたちに接続して、
        用意した取引情報を送信する
        """
        print("called send_request from " + self.name)
        transaction.print_short_data()
        self.connect_nodes()  # ノードに接続する

    def connect_nodes(self):
        """
        ノードたちに接続する (TODO send_requestに内包したらいいかも)
        """

    def make_transaction(self):
        """
        取引情報を作成する
        """


user = User("Takahashi")
user2 = User("Suzuki")

trans = Transaction("Takahashi", "Suzuki", 300)
print(user.name)  # pythonは__を変数名の前につけないとpublic変数扱い
# print(user.__test_name) private変数化(厳密には違うらしい)されてるのでエラーが出る

user.send_request(trans)
