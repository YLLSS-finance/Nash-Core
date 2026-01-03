
# Order Format
# Index | Content
# 0 | Order ID
# 1 | Timestamp
# 2 | Market Participant ID
# 3 | Contract ID
# 4 | Limit Price
# 5 | Order Side
# 6 | Order Quantity [red, inc]
# 7 | Order Head/Tail [head, tail]

from sortedcontainers import SortedDict

class OrderQueue:
    def __init__(self, side, existing_orders = []):
        self.side = int(side)
        self.bestPrice = None
        self.price_levels = SortedDict(key=lambda x:-x) if side == 0 else SortedDict()
        if existing_orders: self.initializeWithOrders(existing_orders)

    def initializeWithOrders(self, orders):
        orders_dict = {}
        for order in orders:
            if not order[4] in orders_dict:
                orders_dict[order[4]] = []
            orders_dict[order[4]].append(order)

        # Sort all orders in each price level by price-time priority
        for order_list in orders_dict:
            order_list.sort(key=lambda x:x[1])

        self.price_levels.clear()
        for price_level, orders_at_level in orders_dict.items():
            total_qty = sum([sum(order[6]) for order in orders_at_level])
            total_orders = len(orders_at_level)
            self.price_levels[price_level] = [orders_at_level[0], orders_at_level[-1], total_qty, total_orders]

        self.bestPrice = self.price_levels.keys()[0]

    def addOrder(self, order):
        order_price = order[4]
        if not order_price in self.price_levels:
            self.price_levels[order_price] = [order, order, sum(order[6]), 1]
            if not self.bestPrice:
                self.bestPrice = order_price
                return
            if self.side == 0:
                if order_price > self.bestPrice: self.bestPrice = order_price
            else:
                if order_price < self.bestPrice: self.bestPrice = order_price
            return

        price_level = self.price_levels[order_price]

        # This part of the code may look scary but it's really just doing two things:
        # Setting the tail of the current tail order to the new order
        # And setting the current tail order to the new order.
        price_level[1][1] = order
        price_level[1] = order