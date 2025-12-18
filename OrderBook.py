
# order structure
# 0 - orderID
# 1 - timestamp
# 2 - mpid
# 3 - instrumentID
# 4 - price
# 5 - side
# 6 - [red, inc]
# 7 - [head, tail]

from sortedcontainers import SortedDict
from orderProperties import OrderProperties as op

class orderBook:
    def __init__(self, _master, contractID):
        self.fillOrder = _master.fillOrder
        self.cancelOrder = _master.cancelOrder
        self.contractID = contractID

        # price:[head, tail, qty, number of orders]
        self.book = [SortedDict(key=lambda x:-x), SortedDict(key=lambda x:x)]

    # TODO: optimise this function
    def remove_order(self, order):
        order_price = order[4]
        order_side = order[5]
        order_head, order_tail = order[7][0], order[7][1]
        if order_head: order_head[7][1] = order_tail
        if order_tail: order_head[7][0] = order_head
        side_book = self.book[order_side]
        order_price_level = side_book[order_price]
        order_price_level[2] -= sum(order[6])
        order_price_level[3] -
        if not order_price_level[3]:
            del self.book[order[5]][order_price]
            if not self.book[order[5]]:


    def post_order(self, order):
        order[7] = [None, None]
        side_book = self.book[order[5]]
        order_price = order[4]
        if not order_price in side_book:
            side_book[order_price] = [None, None, sum(order[6]), 1]
            return
        price_level = side_book[order.price]
        order[7][0] = price_level[1]
        price_level[1] = order
        price_level[2] += sum(order[6])
        price_level[3] += 1