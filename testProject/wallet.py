from ecdsa_generator import KeyAddressGenerator
import pprint


class Wallet:

    def __init__(self):
        """インスタンス生成時にアドレス・鍵をひとつ追加する"""
        self.key_address_list = []

    def new_key_address(self, number=1):
        """秘密鍵・暗号鍵・アドレスで構成されたdictをwalletリストに追加する"""
        for _ in range(number):
            pri_key, pub_key, addr = KeyAddressGenerator().get_list()
            dictionary = {
                "private_key": pri_key,
                "public_key": pub_key,
                "address": addr
            }
            self.key_address_list.append(dictionary)

    def get_list(self):
        """アドレス・秘密鍵・公開鍵のリストを取得する"""
        return self.key_address_list

    def get_address_list(self):
        """アドレスのリストだけを返す"""
        address_list = []
        for item in self.key_address_list:
            address_list.append(item["address"])
        return address_list

    def get_public_key(self, addr):
        """
        引数として指定されたアドレスに対応する公開鍵を返す
        なかったらNoneを返す
        """
        for item in self.key_address_list:
            if addr == item["address"]:
                return item["public_key"]
        return None

    def get_public_private_key(self, addr):
        """
        引数として指定されたアドレスに対応する秘密鍵と公開鍵のtupleを返す
        なかったらNoneを返す
        """
        for item in self.key_address_list:
            if addr == item["address"]:
                return (
                    item["public_key"],
                    item["private_key"]
                    )
        return None


wallet = Wallet()
wallet.new_key_address(10)
pprint.pprint(wallet.get_list())
