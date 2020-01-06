import datetime


class Transaction:
    """取引情報を記憶するクラス"""

    def __init__(self, sender_name, receiver_name, value):
        self.sender_name = sender_name  # 誰から送ったか
        self.receiver_name = receiver_name  # 誰に送るか
        self.value = value  # いくら
        self.date = datetime.datetime.now()  # 送信時の日付
        self.print_all_data()

    def print_all_data(self):
        print("sender:    " + self.sender_name)
        print("receiver:  " + self.receiver_name)
        print("value:     " + str(self.value))
        print("date:      " + str(self.date))

    def print_short_data(self):
        print("Send to " + self.sender_name + " from " + self.receiver_name + ". Value: " + str(self.value))