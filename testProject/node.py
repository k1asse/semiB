from transaction import Transaction
import socket
import selectors
import sys
import os

sel = selectors.DefaultSelector()
args = sys.argv
NUMBER_OF_ZERO_SEQUENCE = 4
MAX_NODES = 10  # 最大ノード数

if len(args) != 3:
    print("usage: node.py [node port] [user port]")
    sys.exit()

node_port = int(args[1])
user_port = int(args[2])


def is_transaction(string):
    """
    取引情報のチェックを行う
    """
    print("取引情報がユーザからきました\n")
    return True


def make_transaction_instance(string):
    print("transactionクラスのインスタンスを生成します")
    #print(string.split(',')[0])
    sender_name = string.split(',')[0]
    receiver_name = string.split(',')[1]
    value = string.split(',')[2]
    return Transaction(sender_name, receiver_name, value)


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


def transact(string):
    print("transact")
    # これサブのスレッドでやらんとしんどい(ソケット監視ができない)
    # トランザクションのインスタンスを作る
    transaction = make_transaction_instance(string)
    # ナンスを代入し始める
    assign_nonce(transaction)
    # ブロックを生成する(TODO ブロック中の取引情報数を1として考えてるので複数に変更)
    generate_block(transaction)


def accept_node(sock, _):
    conn, addr = sock.accept()
    #print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read_node)


def accept_user(sock, _):
    conn, addr = sock.accept()
    #print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read_user)


def read_node(conn, _):
    data = conn.recv(1000).decode()
    # ここの分岐をconn, dataによって行う
    if data:
        if data.startswith('transaction'):
            # 小さいポート番号を持つノードから取引情報がきた時
            # 送信元が自分なら送らない(
            if len(data.split()) > 1 and (int(data.split()[2]) != node_port):
                send_message_latter_node(data)
            # 取引情報の処理(スレッドの開始)
            # delete "transaction"
            transact(data[12:])
        elif data.startswith('nonce'):
            # ナンスを発見されたらやめる (スレッドの終了)
            print("nonce")
            # ナンスがあってるか確認する

        elif data.startswith('connection_check'):
            # 大きいポート番号をもつノードから接続確認がきた時
            print("connection_check")
            # 送信元が自分なら送らない(作った時はこないけど仕様変更に対応)
            if int(data.split()[2]) != node_port:
                send_message_former_node("connection_check")
        else:
            print("okasii at read_node()")
        print('echoing', repr(data), 'to', conn)
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


def read_user(conn, _):
    data = conn.recv(1000).decode()
    # ここの分岐をconn, dataによって行う
    if data:
        if data.startswith('transaction'):
            # 文字列のチェック
            if is_transaction(data):
                # この文字列をそのまま次のノードに送る
                data.replace('transaction', 'transaction from' + str(node_port), 1)
                send_message_latter_node(data)
                # 取引情報の処理(スレッドの開始)
                #print(data[12:])
                # delet "transaction"
                transact(data[12:])
            else:
                # 取引情報じゃねえからuserに拒否メッセージを出す
                print("ユーザからの取引情報を拒否する")
            print('正しく取引を処理しました')
        elif data == 0:   # ユーザからEOFが送られてきた場合
            sel.unregister(conn)
            conn.close()
        else:
            print('echoing', repr(data), 'to', conn)
            conn.send(data.encode())
            sel.unregister(conn)
            conn.close()
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


def send_message_former_node(string):
    """前の(ひとつ小さい)ポート番号のノードに、stringに入力されたメッセージを送る"""
    send_port = node_port - 1
    if node_port > 10000:  # 10000は最小値なので除外
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    print("send_port(former): " + str(send_port))
                    if send_port >= 10000:
                        s.connect(('127.0.0.1', send_port))
                        s.sendall(string.encode())
                    break
                except ConnectionRefusedError:
                    # コネクションがrefuseされた時、ポート番号がiだけ前のポートにメッセージを送る
                    send_port -= 1


def send_message_latter_node(string):
    """後の(ひとつ大きい)ポート番号のノードに、stringに入力されたメッセージを送る"""
    send_port = node_port + 1
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                print("send_port(latter): " + str(send_port))
                if send_port < 10000 + MAX_NODES:
                    if send_port == node_port:
                        break
                    else:
                        s.connect(('127.0.0.1', send_port))
                        s.sendall(string.encode())
                        break
                else:
                    # ポート番号の最大値に達したら先頭に送るよう変更する
                    # (send_portを10000にして再度ループを回せば最小値がでる)
                    send_port = 10000
            except ConnectionRefusedError:
                # コネクションがrefuseされた時、ポート番号がiだけ前のポートにメッセージを送る
                send_port += 1


def std_input(conn, _):
    line = sys.stdin.readline().strip()
    if line:
        print("I'll send message: " + line)
        send_message_latter_node(line)
        sel.unregister(conn)
        conn.close()
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


# ノード用のソケット
sock1 = socket.socket()
sock1.bind(('localhost', node_port))
sock1.listen(100)
sock1.setblocking(False)
sel.register(sock1, selectors.EVENT_READ, accept_node)

# ユーザ用のソケット
sock2 = socket.socket()
sock2.bind(('localhost', user_port))
sock2.listen(100)
sock2.setblocking(False)
sel.register(sock2, selectors.EVENT_READ, accept_user)

# 標準入力
sel.register(sys.stdin, selectors.EVENT_READ, std_input)

# TODO 起動時に一つ前ポート番号args[2]のソケットに接続要求を出す(args[2]が10000ならしない)
send_message_former_node("chinko")

while True:
    # ノード用のソケットを登録
    events = sel.select()
    #print(events)
    for key, mask in events:
        callback = key.data
        #print(key.data)
        callback(key.fileobj, mask)
