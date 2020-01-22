from transaction import Transaction
from ecdsa_generator import KeyAddressGenerator
import socket
import selectors
import sys
import os
# ユーザ側のマシンが実行するプログラム
MAX_NODES = 10  # 最大ノード数


def send_message(string):
    """
    ノードたちに接続する (TODO send_requestに内包したらいいかも)
    ノードのユーザ用port: 10010, 10011, ..., 10019
    ユーザのport: 10020, 10021, ..., 10029
    """
    send_port = 10010
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                print("connect_nodes: " + str(send_port))
                if send_port < 10010 + MAX_NODES:
                    s.connect(('127.0.0.1', send_port))
                    s.sendall(string.encode())
                    break
                else:
                    # ポート番号の最大値に達したらノードがいなかったというエラーを出して終了
                    print("ノードがいませんでした。")
                    sys.exit()
            except ConnectionRefusedError:
                # コネクションがrefuseされた時、ポート番号がiだけ前のポートにメッセージを送る
                send_port += 1


def accept(sock, _):
    conn, addr = sock.accept()
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, _):
    data = conn.recv(1000).decode()
    # ここの分岐をconn, dataによって行う
    if data:
        print('echoing', repr(data), 'to', conn)
        conn.send(data)
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


def std_input(conn, _):
    line = sys.stdin.readline().strip()
    print("line: " + line)
    if line:
        if line == '/send':
            print("/send money")
            print("sender_address?")
            sender_address = sys.stdin.readline().strip()
            print("receiver_address?")
            receiver_address = sys.stdin.readline().strip()
            print("value?")
            value = sys.stdin.readline().strip()
            make_transaction(sender_address,receiver_address,value)
        elif line == '/history':
            print("/history")
        else:
            print("unknown command")
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


def make_transaction(sender, receiver, value):
    """
    取引情報を作成する。具体的にはsender, receiver, valueを用いて文字列を作成する
    取引情報の文字列の先頭が"transaction"であれば
    ノードが取引情報だと思ってくれます
    """
    trans = "transaction" + ',' + sender + ',' + receiver + ',' + value
    send_message(trans)


def send_address_public_key(address, public_key):
    """
    アドレス作成時にアドレスと公開鍵をノード側に渡す
    """
    print("send_address_public_key")
    send_message("new_address_key," + address + "," + public_key)



    

sel = selectors.DefaultSelector()
args = sys.argv

if len(args) != 2:
    print("usage: node.py [port]")
    sys.exit()

port = int(args[1])
# ソケットを登録
sock1 = socket.socket()
sock1.bind(('localhost', port))
sock1.listen(100)
sock1.setblocking(False)
sel.register(sock1, selectors.EVENT_READ, accept)

# 標準入力
sel.register(sys.stdin, selectors.EVENT_READ, std_input)

# ノードに接続
# send_message("hello")
# send_message("hello222")

# ウォレットの新規作成及び新規アドレスをひとつ追加する
wallet = []

wallet.append(KeyAddressGenerator().get_list())
# 新しいアドレス・公開鍵をノード側に伝えておく
send_address_public_key(wallet[0][2], wallet[0][1])




print("Commands:\nSending money: /send\nCheck transaction history: /history")

while True:
    # ノード用のソケットを登録
    events = sel.select()
    # print(events)
    for key, mask in events:
        callback = key.data
        #print(key.data)
        callback(key.fileobj, mask)
