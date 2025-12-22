
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

        self.linkedBooks = []

        # price:[head, tail, qty, number of orders]
        self.book = [SortedDict(key=lambda x:-x), SortedDict(key=lambda x:x)]
        self.bestPrices = [None, None]

    def fill(self, fill_side, limit_price, order_qty, enforce_best_price):
        book = self.book[fill_side]
        prev_bestprice = self.bestPrices[fill_side]

        while True:
            best_fill_price, best_level = self.bestPrices[fill_side].peekitem(0)
            # Halt if there are no price levels in this side of the book or t
            if (not best_fill_price) or (prev_bestprice != best_fill_price): break
            if (not order_qty) or ((fill_side == 0 and best_fill_price < limit_price) or (fill_side == 1 and best_fill_price > limit_price)): break
            best_order = best_level[1]
            fill_qty = min(order_qty, sum(best_order[6]))
            self.fillOrder

    def remove_order(self, order):
        """
        Removes a specific order from the book.
        To be used when an order-removing function is called externally of the book.
        """
        order_price = order[4]
        order_side = order[5]

        # Change the links of the head and tail of the removed order.
        order_links = order[7]
        order_links[0][7][1] = order_links[1]
        order_links[1][7][0] = order_links[0]

        side_book = self.book[order_side]
        order_price_level = side_book[order_price]

        order_price_level[2] -= sum(order[6])
        order_price_level[3] -= 1
        if not order_price_level[3]:
            del side_book[order_price]
            # TODO: review syntax vaildity in the context of the sortedcontainers library
            if not side_book:
                self.bestPrices[order_side] = None
            self.bestPrices[order_side] = side_book.peekitem(0)[0]
            return

        # Clever optimisation here: Only attempt to change the head and tail order of the price level if it still exists (i.e. you are not removing the last order from the price level)
        if order == order_price_level[0]: order_price_level[0] = order_links[1]
        if order == order_price_level[1]: order_price_level[1] = order_links[0]

    def post_order(self, order):
        order[7] = [None, None]
        side_book = self.book[order[5]]
        order_price = order[4]
        if not order_price in side_book:
            side_book[order_price] = [None, None, sum(order[6]), 1]
            return
        price_level = side_book[order.price]
        order[7][0] = price_level[1]
        if not price_level[0]: price_level[0] = order
        price_level[1] = order
        price_level[2] += sum(order[6])
        price_level[3] += 1