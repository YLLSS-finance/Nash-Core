
# Order Format
# Index / Data
# 0 / orderID
# 1 / timestamp
# 2 / mpid
# 3 / contractID
# 4 / price
# 5 / side
# 6 / [red, inc]
# 7 / [head, tail]

class OrderProperties:
    @staticmethod
    def BuyOrderComparator(order):
        return -order[4], order[1], order[2], order[0]

    @staticmethod
    def SellOrderComparator(order):
        return order[4], order[1], order[2], order[0]

    @staticmethod
    def TotalCost(order):
        return order[4] * order[6][1] if order[5] == 0 else (100 - order[4]) * order[6][1]

    @staticmethod
    def ContractCost(order):
        return order[4] if order[5] == 0 else (100 - order[4])

    