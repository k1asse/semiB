import hashlib

from transaction import Transaction
from ecdsa_generator import KeyAddressGenerator
from transaction import Transaction, Input, Output
from wallet import Wallet
import socket
import selectors
import sys
import pprint
import os
# ユーザ側のマシンが実行するプログラム
MAX_NODES = 10  # 最大ノード数
BUF_SIZE = 2048     # recv(2)で一度に受け取るバイト数


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
                    print("送ります: " + string)
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
    data = ''
    while True:
        tmp = conn.recv(BUF_SIZE).decode()
        if not tmp:
            break
        data += tmp
    # ここの分岐をconn, dataによって行う
    if data:
        print('echoing', repr(data), 'to', conn)
        # conn.sendall(data)
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
            transaction = make_transaction_from_std()
            # pprint.pprint(transaction.get_dictionary())
        elif line == '/history':
            print("/history")
        else:
            print("unknown command")
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


def make_transaction_from_std():
    """
    標準入力により取引情報を作成する。具体的にはsender, receiver, valueを用いて文字列を作成し、その文字列を返す
    取引情報の文字列の先頭が"transaction"であれば
    ノードが取引情報だと思ってくれる
    """
    address_list = wallet.get_address_list()
    for index, address in enumerate(address_list):
        print(str(index) + ": " + address)
    while True:
        print("sender_address?")
        sender_addr_index = sys.stdin.readline().strip()
        if sender_addr_index.isdecimal() and -1 < int(sender_addr_index) < len(address_list):
            sender_addr = address_list[int(sender_addr_index)]
            break
    while True:
        print("receiver_address?")
        receiver_addr_index = sys.stdin.readline().strip()
        if receiver_addr_index.isdecimal() and -1 < int(receiver_addr_index) < len(address_list):
            receiver_addr = address_list[int(receiver_addr_index)]
            break
    while True:
        print("value?")
        value = sys.stdin.readline().strip()
        if value.isdecimal():
            value = int(value)
            break
    while True:
        print("fee?")
        fee = sys.stdin.readline().strip()
        if fee.isdecimal():
            fee = int(fee)
            break

    print("sender_addr: " + sender_addr)
    print("receiver_addr:" + receiver_addr)
    print("value: " + str(value))
    print("fee: " + str(fee))

    return make_transaction(sender_addr, receiver_addr, value, fee)


def make_transaction(sender_addr, receiver_addr, value, fee):
    transaction = Transaction()
    # receiverの公開鍵ハッシュを求める
    h = hashlib.new('ripemd160')
    h.update(hashlib.sha256(wallet.get_public_key(receiver_addr).encode()).digest())
    receiver_pub_key_hash = h.hexdigest()

    # InputとOutputをtransactionに追加
    pre_hash_index = get_pre_hash_index(sender_addr)
    transaction.add_input(pre_hash_index[0], pre_hash_index[1])
    transaction.add_output(value - fee, receiver_pub_key_hash)

    pub_pri_key = wallet.get_public_private_key(sender_addr)
    transaction.assign_signature(pub_pri_key[0], pub_pri_key[1])

    return transaction


def get_pre_hash_index(sender_addr):
    """引数sender_addrについて、pre_hash, pre_indexのタプルを返す"""
    return "pre_hash", "pre_index"


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

# walletの新規作成
wallet = Wallet()
wallet.new_key_address(3)


print("Commands:\nSending money: /send\nCheck transaction history: /history")


while True:
    # ノード用のソケットを登録
    events = sel.select()
    # print(events)
    for key, mask in events:
        callback = key.data
        # print(key.data)
        callback(key.fileobj, mask)
