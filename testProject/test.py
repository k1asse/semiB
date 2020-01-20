from transaction import Transaction
import json

trans = {
	'xxx':'123','yyy':'456'
}

tmp = json.dumps(trans)

trans2 = json.loads(tmp)

print(trans2)
print()

blockchain = []

blockchain.append(trans2)

trans3 = {
	'xxx':'334','yyy':'334','zzz':'334', 'ooo': trans, 'ppp': {'a': {'a': {'a': {}}}}
}

blockchain.append(trans3)

print(blockchain[0])
print(blockchain[1])
print()

tmp2 = json.dumps(blockchain)
print(tmp2)
blockchain2 = json.loads(tmp2)

print(blockchain2[0])
print(blockchain2[1])