import json


class Transaction:
    """取引情報を記憶するクラス"""

    def __init__(self):
        self.version = 0x0000
        self.inputs = []
        self.outputs = []

    def get_json(self):
        """1回辞書型に変換して、jsonファイルを取得する"""
        return json.dumps(self.get_dictionary())

    def get_dictionary(self):
        """Transactionのデータを辞書型に変換する"""
        dictionary = {'version': self.version,
                      'input_number': len(self.inputs),
                      'output_number': len(self.outputs),
                      'inputs': {},
                      'outputs': {}
                      }
        for index, item in enumerate(self.inputs):
            dictionary['inputs']['input' + str(index)] = item.get_dictionary()
        for index, item in enumerate(self.outputs):
            dictionary['outputs']['output' + str(index)] = item.get_dictionary()
        return dictionary

    def add_input(self, pre_hash, index, signature, pub_key):
        self.inputs.append(Input(pre_hash, index, signature, pub_key))

    def add_output(self, value, pub_key_hash):
        self.outputs.append(Output(value, pub_key_hash))


class Input:
    """トランザクションの入力部分"""

    def __init__(self, pre_hash, index, sign, pub_key):
        self.previous_hash = pre_hash
        self.output_index = index
        self.signature = sign
        self.public_key = pub_key

    def get_dictionary(self):
        """入力のデータを辞書型に変換する"""
        dictionary = {
            'previous_hash': self.previous_hash,
            'output_index': self.output_index,
            'signature': self.signature,
            'public_key': self.public_key
        }
        return dictionary


class Output:
    """トランザクションの出力部分"""

    def __init__(self, value, pub_key_hash):
        self.value = value
        self.receiver_public_key_hash = pub_key_hash

    def get_dictionary(self):
        """出力のデータを辞書型に変換する"""
        dictionary = {
            'value': self.value,
            'receiver_public_key_hash': self.receiver_public_key_hash
        }
        return dictionary


transaction = Transaction()
transaction.add_input('prehash', 'index', 'sig', 'pub_key')
transaction.add_input('prehash2', 'index2', 'sig2', 'pub_key2')
transaction.add_output(200, 'key_hash')
print(transaction.get_dictionary())
