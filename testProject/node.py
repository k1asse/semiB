from transaction import Transaction
import socket
import selectors
import sys

sel = selectors.DefaultSelector()
args = sys.argv
NUMBER_OF_ZERO_SEQUENCE = 4

if len(args) != 3:
    print("usage: node.py [node port] [user port]")
    sys.exit()


def check_transaction(str):
    """
    取引情報のチェックを行う
    チェックに通らなかったら例外CheckTransactionErrorを呼び出す
    """
    print("取引情報がユーザからきました\n")
    sender_name = ""
    receiver_name = ""
    value = 0
    transaction = Transaction(sender_name, receiver_name, value)
    return transaction


def assign_nonce(transaction):
    """
    ナンスを代入する、0が先頭にNUMBER_OF_ZERO_SEQUENCE個来たらノード全体に送信
    """
    print("ナンスを代入します\n")
    # ナンスができたらそれをノード全体に送信する
    # だるい!!!



def generate_block(transaction):
    """
    ブロックを生成する
    """
    print("ブロックを生成します\n")


def send_result(transaction, conn):
    """
    ユーザに処理結果がOK/NGであったことを送信する
    """
    print("ユーザに処理結果を送信します")
    conn.send(b'process result from node')


def accept_node(sock, mask):
    conn, addr = sock.accept()
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read_node)


def accept_user(sock, mask):
    conn, addr = sock.accept()
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read_user)


def read_node(conn, mask):
    data = conn.recv(1000)
    # ここの分岐をconn, dataによって行う
    if data:
        print('echoing', repr(data), 'to', conn)
        conn.send(data)
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


def read_user(conn, mask):
    data = conn.recv(1000)
    # ここの分岐をconn, dataによって行う
    if data:
        recv_str = data.decode()
        if recv_str.startswith('transaction'):
            # 文字列のチェック・
            try:
                transaction = check_transaction(recv_str)
            except CheckTransactionError as e:
                print(e)
            # 以下、マイニング作業を行う
            # 適当に並べてるだけなので実際はtry-exceptとか関数とか変えていいと思う
            # ナンスの代入(TODO ここソケット監視と並行に処理しないと無理かも(threadingとか))
            assign_nonce(transaction)
            # ブロックの生成
            generate_block(transaction)
            # 処理結果の送信
            send_result(transaction, conn)
            print("正しく取引を処理しました")
        elif len(recv_str) == 0:   # ユーザからEOFが送られてきた場合
            conn.close()
        else:
            print('echoing', repr(data), 'to', conn)
            conn.send(data)
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


class CheckTransactionError(Exception):
    """送られたtransactionに関するエラーを知らせる例外クラス"""
    pass


# ノード用のソケット
sock1 = socket.socket()
sock1.bind(('localhost', int(args[1])))
sock1.listen(100)
sock1.setblocking(False)
sel.register(sock1, selectors.EVENT_READ, accept_node)

# ユーザ用のソケット
sock2 = socket.socket()
sock2.bind(('localhost', int(args[2])))
sock2.listen(100)
sock2.setblocking(False)
sel.register(sock2, selectors.EVENT_READ, accept_user)

try:
    while True:
        # ノード用のソケットを登録
        events = sel.select()
        for key, mask in events:
            callback = key.data
            print(key.data)
            callback(key.fileobj, mask)
except KeyboardInterrupt:
    print("interrupted.")
    sock1.close()
    sock2.close()
