import socket
import selectors
import sys
import json
import time
import threading
import os
import hashlib

sel = selectors.DefaultSelector()
args = sys.argv
NUMBER_OF_ZERO_SEQUENCE = 4
MAX_NODES = 10  # 最大ノード数
BUF_SIZE = 2048
blockchain = []
global first

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
    sender_name = string.split(',')[0]
    receiver_name = string.split(',')[1]
    value = string.split(',')[2]
    transaction = {
    	"sender" : sender_name,
    	"receiver" : receiver_name,
    	"value" : value,
    }
    return transaction
    #return Transaction(sender_name, receiver_name, value)


def assign_nonce(block):
    """
    ナンスを代入する、0が先頭にNUMBER_OF_ZERO_SEQUENCE個来たらノード全体に送信
    """
    global first
    first = True
    print("ナンスを代入します\n")
    block_head = {
        'index' : block['index'],
        'timestamp' : block['timestamp'],
        'proof' : 0,
        'previous_hash' : block['previous_hash'],
        'Merkle_Root' : block['Merkle_Root'],
    }
    # ナンスをインクリメントしながらブロックヘッドのハッシュ値を計算
    flag = True
    while flag:
        block_head['proof'] = block_head['proof'] + 1
        tmp = hash_block_head(block_head)
        for i in range(NUMBER_OF_ZERO_SEQUENCE):
            if tmp[i] != '0':
                break
            if i == NUMBER_OF_ZERO_SEQUENCE - 1:
                flag = False
    # ナンスができたらそれをノード全体に送信する
    # だるい!!!
    if first:
        right_block_head = json.dumps(block_head, sort_keys=True)
        right_block_head = 'nonce' + ',' + right_block_head
        send_message_latter_node(right_block_head)
        print("ナンスを見つけました")


def generate_first_block():
    """
    初期ブロックを生成する
    """
    print("初期ブロックを生成します\n")
    first_transaction = {
        'sender' : "hoge",
        'receiver' : "hoge",
        'value' : 0,
    }
    block = {
        'index' : 0,
        'timestamp' : time.time(),
        'transaction' :{
            'sender' : "hoge",
            'receiver' : "hoge",
            'value' : 0,
        },
        'proof' : 0,
        'previous_hash' : "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        'Merkle_Root' : hash_transaction(first_transaction),
    }
    blockchain.append(block)


def generate_block(transaction):
    """
    ブロックを生成する
    """
    print("ブロックを生成します\n")
    previous_block = blockchain[len(blockchain) - 1]
    block = {
        'index' : blockchain[len(blockchain) - 1]['index'] + 1,
        'timestamp' : time.time(),
        'transaction' :{
            'sender' : transaction['sender'],
            'receiver' : transaction['receiver'],
            'value' : transaction['value'],
        },
        'proof' : 0,
        'previous_hash' : hash_block(previous_block),
        'Merkle_Root' : hash_transaction(transaction),
    }
    return block

def hash_block(block):
	block_string = json.dumps(block,sort_keys=True).encode()
	return hashlib.sha256(block_string).hexdigest()

def hash_block_head(block_head):
	block_head_string = json.dumps(block_head,sort_keys=True).encode()
	return hashlib.sha256(block_head_string).hexdigest()

def hash_transaction(transaction):
    transaction_string = json.dumps(transaction,sort_keys=True).encode()
    return hashlib.sha256(transaction_string).hexdigest()

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
    # ブロックを生成する(TODO ブロック中の取引情報数を1として考えてるので複数に変更)
    block = generate_block(transaction)
    # ナンスを代入し始める
    assign_nonce(block)
    


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
    data = ''
    while True:
        tmp = conn.recv(BUF_SIZE).decode()
        if not tmp:
            break
        data += tmp
    # ここの分岐をconn, dataによって行う
    if data:
        if data.startswith('transaction'):
       	    thread = threading.Thread(target=transact,args=([data[12:]]))
            # 小さいポート番号を持つノードから取引情報がきた時
            # 送信元が自分なら送らない(
            if len(data.split()) > 1 and (int(data.split()[2]) != node_port):
                send_message_latter_node(data)
            # 取引情報の処理(スレッドの開始)
            # 取引情報は同時に一個しか来ない前提
            # 複数に対応するならスレッドをリスト化かして複数保持させる
            thread.start()
        elif data.startswith('nonce'):
            # ナンスを発見されたらやめる (スレッドの終了)
            #event.wait()
            global first
            first = False
            print("nonce")
            # ナンスがあってるか確認する
            nonce_check = json.loads(data[6:])
            nonce_check_hash = hash_block_head(nonce_check)
            for i in range(NUMBER_OF_ZERO_SEQUENCE):
            	if nonce_check_hash[i] != '0':
            		print("ナンスは間違っています")
            	elif i == NUMBER_OF_ZERO_SEQUENCE -1:
                    print("ナンスは正しいです")
        elif data.startswith('connection_check'):
            # 大きいポート番号をもつノードから接続確認がきた時
            print("connection_check")
            # 送信元が自分なら送らない(作った時はこないけど仕様変更に対応)
            if int(data.split()[2]) != node_port:
                send_message_former_node("connection_check")
        elif data.startswith('new_address_key'):
            # 新しいアドレスと鍵の取得
            new_address_key(data, 1)
        else:
            print("size: " + len(data) + "str: " + data)
            print("okasii at read_node()")
        #print('echoing', repr(data), 'to', conn)
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


def read_user(conn, _):
    data = ''
    while True:
        tmp = conn.recv(BUF_SIZE).decode()
        if not tmp:
            break
        data += tmp
    # ここの分岐をconn, dataによって行う
    if data:
        if data.startswith('transaction'):
            thread = threading.Thread(target=transact,args=([data[12:]]))
            # 文字列のチェック
            if is_transaction(data):
                # この文字列をそのまま次のノードに送る
                data.replace('transaction', 'transaction from' + str(node_port), 1)
                send_message_latter_node(data)
                # 取引情報の処理(スレッドの開始)
                thread.start()
                # 取引情報は同時に一個しか来ない前提
                # 複数に対応するならスレッドをリスト化かして複数保持させる
            else:
                # 取引情報じゃねえからuserに拒否メッセージを出す
                print("ユーザからの取引情報を拒否する")
            print('正しく取引を処理しました')
        elif data.startswith('new_address_key'):
            # 新しいアドレスと鍵の取得
            data.replace('new_address_key', 'new_address_key from ' + str(node_port))
            new_address_key(data, 0)
        else:
            print('echoing', repr(data), 'to', conn)
            # conn.sendall(data.encode())
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


def new_address_key(data, port):
    """
    送られてきたdataをaddressとpublic_keyに分割し、
    自分のdictに格納する
    分割せずに次のポート番号のノードに渡す
    userからの送信ならばportは0, nodeからの送信ならばportは1になる
    """
    print("new_address_key: " + data)
    tmp_data = data
    if port == 0:
        _, address, public_key = tmp_data.split(',')
        if public_key:
            # 自分のポート番号を追加して送信する
            data = data.replace('new_address_key', 'new_address_key from ' + str(node_port))
            print("new_address_key: " + data)
            send_message_latter_node(data)
            address_key_dict[address] = public_key
    elif port == 1:
        top, address, public_key = tmp_data.split(',')
        top = top.replace('new_address_key from ', '')
        if public_key and top != str(node_port):
            send_message_latter_node(data)
            address_key_dict[address] = public_key

    print(address_key_dict)


# ユーザのアドレスと公開鍵を紐付けるdict
address_key_dict = {}

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
generate_first_block()


while True:
    # ノード用のソケットを登録
    events = sel.select()
    #print(events)
    for key, mask in events:
        callback = key.data
        #print(key.data)
        callback(key.fileobj, mask)
